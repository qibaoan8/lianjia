# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 10:35:07 2018

@author: zhangying
"""
from config.conf import area_map
from lib.downloader import HtmlDownloader
from lib.model_table import XiaoQuModel
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


class SpiderMain():
    """爬虫程序主模块"""

    def __init__(self):
        """构造函数，初始化属性"""
        self.urls = UrlManager()
        self.log = MyLog("spider_main", "logs").getMyLogger()
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        # self.util=utill.DBConn()

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
        return

    def craw(self, root_url):
        """爬虫入口函数"""
        areas = {
            "gulou": 100, "jianye": 72, "qinhuai": 100,
            "xuanwu": 67, "yuhuatai": 32, "qixia": 62,
            "baijiahu": 33, "chalukou1": 26, "jiangningqita11": 3,
            "dongshanzhen": 29, "jiangningdaxuecheng": 15, "jiulonghu": 12,
            "jiangjundadao11": 22, "kexueyuan": 9, "qilinzhen": 42,
            "tiexinqiao": 9, "pukou": 100, "liuhe": 1,
        }

        # areas = {"gulou":1}

        # 1、抓取所有二手房详情界面链接，并将所有连接放入URL管理模块
        for area, pg_sum in areas.items():
            for num in range(1, pg_sum + 1):
                # 1.1 拼接页面地址: https://nj.lianjia.com/ershoufang/gulou/pg2/
                pg_url = root_url + area + "/pg" + str(num) + "/"
                self.log.info("1.1 拼接页面地址：" + pg_url)
                # 1.2 启动下载器,下载页面.
                try:
                    html_cont = self.downloader.download(pg_url)
                except Exception as e:
                    self.log.error("1.2 下载页面出现异常:" + repr(e))
                    time.sleep(60 * 30)
                else:
                    # 1.3 解析PG页面，获得二手房详情页面的链接,并将所有链接放入URL管理模块
                    try:
                        ershoufang_urls = self.parser.get_erhoufang_urls(html_cont)
                    except Exception as e:
                        self.log.error("1.3 页面解析出现异常:" + repr(e))
                    else:
                        self.urls.add_new_urls(ershoufang_urls)
                        # 暂停0~3秒的整数秒，时间区间：[0,3]
                        time.sleep(random.randint(0, 3))

        time.sleep(60 * 20)
        # 2、解析二手房具体细心页面
        id = 1
        stop = 1
        while self.urls.has_new_url():
            # 2.1 获取url
            try:
                detail_url = self.urls.get_new_url()
                self.log.info("2.1 二手房页面地址：" + detail_url)
            except Exception as e:
                self.log.error("2.1 拼接地址出现异常:" + detail_url)

            # 2.2 下载页面
            try:
                detail_html = self.downloader.download(detail_url)
            except Exception as e:
                self.log.error("2.2 下载页面出现异常:" + repr(e))
                self.urls.add_new_url(detail_url)
                time.sleep(60 * 30)
            else:
                # 2.3 解析页面
                try:
                    ershoufang_data = self.parser.get_ershoufang_data(detail_html, id)
                except Exception as e:
                    self.log.error("2.3 解析页面出现异常:" + repr(e))
                else:
                    pass


if __name__ == "__main__":
    # 初始化爬虫对象
    obj_spider = SpiderMain()
    obj_spider.get_xiaoqu_list(1)
