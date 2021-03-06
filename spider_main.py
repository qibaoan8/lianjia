# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 10:35:07 2018

@author: zhangying
"""
from config.conf import area_map
from lib.downloader import HtmlDownloader
from lib.model_table import XiaoQuModel, HouseModel
from lib.super_queue import Super_Queue
from lib.url_manager import UrlManager
from lib.log import MyLog
from lib.html_parser import HtmlParser
import time
import random
import math
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

xiaoqu_db = XiaoQuModel()
house_db = HouseModel()


class SpiderMain():
    """爬虫程序主模块"""

    def __init__(self):
        """构造函数，初始化属性"""
        self.urls = UrlManager()
        self.log = MyLog("spider_main", "logs").getMyLogger()
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        # self.util=utill.DBConn()

    def get_house_list(self, update_batch):
        """
        获取房源
        """
        sql = "select * from %s WHERE houses > 0 and update_batch = %s" % (xiaoqu_db.table, update_batch)
        xiaoqu_list = xiaoqu_db.raw(sql)
        if not xiaoqu_list:
            self.log.warn("not fount xiaoqu")
            return
        # 设置断点续传状态
        for xiaoqu in xiaoqu_list:

            # 查询已有房源列表
            exsit_house_list = house_db.filter({"update_batch": update_batch, "xiaoqu_id": xiaoqu.xiaoqu_id})
            if len(exsit_house_list) >= xiaoqu.houses:
                self.log.info("断点续传跳过小区: %s" % xiaoqu.xiaoqu_name)
                continue
            else:
                self.log.info("断点续传放过小区: %s, exsit_house_list: %s , xiaoqu.houses: %s" % (
                    xiaoqu.xiaoqu_name, len(exsit_house_list), xiaoqu.houses))

            # 记录所有房源id  exsit_house_id_list
            exsit_house_id_list = []
            if exsit_house_list:
                for house in exsit_house_list:
                    exsit_house_id_list.append(house.house_id)

            # 获取线上房源
            url_house_list = "https://bj.lianjia.com/ershoufang/c%s/" % xiaoqu.xiaoqu_id
            house_list_html_body = self.downloader.download(url_house_list)
            house_total_count = self.parser.get_html_house_count(house_list_html_body)

            # 更新小区房源数量
            if house_total_count != xiaoqu.houses:
                self.log.info("更新小区数据，原房源数量：%s， 新房源数量：%s" % (xiaoqu.houses, house_total_count))
                xiaoqu.houses = house_total_count
                xiaoqu_db.update(xiaoqu, {"id": xiaoqu.id})

            if house_total_count <= 0 or len(exsit_house_list) >= house_total_count:
                # 如果没房源或者数据库内有，跳过
                self.log.info("断点续传再次跳过小区: %s , 判断的是在线房源数量 , house_total_count: %s, exsit_house_list: %s" % (
                    xiaoqu.xiaoqu_name, house_total_count, len(exsit_house_list)))
                continue

            page_size = 30.0

            start_page = int(len(exsit_house_list) / page_size) + 1
            self.log.info("%s 小区的房源从第%s页开始获取" % (xiaoqu.xiaoqu_name, start_page))

            for page in range(start_page, int(math.ceil(house_total_count / page_size)) + 1):
                url_house_list = "https://bj.lianjia.com/ershoufang/pg%sc%s/" % (page, xiaoqu.xiaoqu_id)
                # https://bj.lianjia.com/ershoufang/pg2c1111027382209/
                html_body = self.downloader.download(url_house_list)
                house_url_list = self.parser.get_html_house_url_list(html_body)

                # 多线程获取房源消息
                sq = Super_Queue(30)
                house_list = sq.start(self.get_xiaoqu_detail,house_url_list)
                for n in range(len(house_list)):
                    house_list[n].xiaoqu_id = xiaoqu.xiaoqu_id
                    house_list[n].update_batch = update_batch
                    self.log.info("get house: %s" % str(house_list[n]))
                # 写库
                ret = house_db.insert(house_list, on_duplicate_update_key=house_db.update_key)
                self.log.info("house db inster ret %s" % ret)
        return

    def get_xiaoqu_detail(self, url):
        """
        获取房源详细信息
        :param url:
        :return:
        """
        html_body = self.downloader.download(url)
        house_id = self.parser.lianjia_url_to_house_id(url)
        house = self.parser.get_html_house_detail(html_body)
        house.house_id = house_id
        return house

    def get_xiaoqu_list(self, update_batch):
        """
        获取小区列表
        """
        areas_list = [
            "dongcheng",
            "xicheng",
            "chaoyang",
            "haidian",
            "fengtai",
            "shijingshan",
            "tongzhou",
            "changping",
            "shunyi",
        ]

        for area in areas_list:
            url_meta = "https://bj.lianjia.com/xiaoqu/%s/" % area
            # https://bj.lianjia.com/xiaoqu/dongcheng/pg2/
            html_body = self.downloader.download(url_meta)
            total_count = self.parser.get_html_xiaoqu_count(html_body)
            if total_count <= 0:
                continue
            page_size = 30.0

            # 查询库里有多少条，然后从多少页开始；
            area_zh = area_map.get(area, "")
            exsit_count = len(xiaoqu_db.filter({"area": area_zh}))
            if exsit_count >= total_count:
                self.log.info("%s 小区数据全部存在" % area_zh)
                continue

            start_page = int(exsit_count / page_size) + 1
            self.log.info("%s 小区从第%s页开始获取" % (area_zh, start_page))

            for page in range(start_page, int(math.ceil(total_count / page_size)) + 1):
                url = "%spg%s/" % (url_meta, page)
                html_body = self.downloader.download(url)
                xiaoqu_list = self.parser.get_html_xiaoqu_list(html_body, update_batch)
                ret = xiaoqu_db.insert(xiaoqu_list, on_duplicate_update_key=xiaoqu_db.update_key)
                self.log.info("xiaoqu db inster ret %s" % ret)
        return


if __name__ == "__main__":
    # 初始化爬虫对象
    obj_spider = SpiderMain()
    update_batch = 1
    # obj_spider.get_xiaoqu_list(1)
    obj_spider.get_house_list(update_batch)
