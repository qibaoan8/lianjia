# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 17:00:31 2018

@author: zhangying
"""
import re

from bs4 import BeautifulSoup
from lib.log import MyLog
from popo.xiaoqu import XiaoQu


class HtmlParser():
    """网页解析模块"""

    def __init__(self):
        """构造函数，初始化属性"""
        self.log = MyLog("html_parser", "../logs").getMyLogger()

    def lianjia_url_to_xiaoqu_id(self, url):
        """
        链家小区url内的id提取
        """
        try:
            strs = url.split("/")
            last_str = strs[len(strs) - 2]
            if last_str[0] == "c":
                last_str = last_str[1:]
            return last_str
        except Exception as e:
            self.log.error("url split error", repr(e))
        return ""

    def lianjia_url_to_house_id(self, url):
        """
        链家房源url内的id提取
        """
        # https://bj.lianjia.com/ershoufang/101107712846.html
        try:
            strs = re.split('[/.]+', url)
            id = strs[len(strs) - 2]
            if id:
                return id
        except Exception as e:
            self.log.error("url split error", repr(e))
        return ""

    def get_html_xiaoqu_list(self, html, update_batch):
        """
        从html内提取小区信息
        """

        def get_create_year(text):
            try:
                if u"建成" not in text:
                    return 0
                for i in re.split('[/, \n]+', text):
                    if u"建成" in i:
                        year = i.split(u"年")[0]
                        return int(year)
            except Exception as e:
                return 0

        ret_xiaoqu = []

        if html is None:
            self.log.error("页面解析(page)：pg页面为空！")
            return

        bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
        xiaoqu_content = bsObj.find("ul", {"class": "listContent"})
        xiaoqu_content_list = xiaoqu_content.findAll("li", {"class": "clear xiaoquListItem"})

        if not xiaoqu_content_list:
            return ret_xiaoqu

        for child in xiaoqu_content_list:

            # init
            area = ""
            area_2 = ""
            turnover = 0

            # url 、 name 、 area
            url = child.a["href"]
            name = child.find("div", {"class": "title"}).get_text().replace("\n", "")
            xiaoqu_id = self.lianjia_url_to_xiaoqu_id(url)
            positionInfo = child.find("div", {"class": "positionInfo"})
            info_list = positionInfo.findAll("a")
            if len(info_list) >= 2:
                area = "".join(info_list[0].string)
                area_2 = "".join(info_list[1].string)

            # 建设时间
            buding_year = get_create_year(positionInfo.get_text())

            # 成交量
            houseInfo = child.find("div", {"class": "houseInfo"})
            info_list = houseInfo.findAll("a")
            if info_list:
                trunover_text = info_list[0].string
                if u"成交" in trunover_text and u"套" in trunover_text:
                    turnover = trunover_text.split(u"成交")[1].split(u"套")[0]

            # 均价
            totalPrice = child.find("div", {"class": "totalPrice"})
            price_text = "".join(totalPrice.find("span").string)
            try:
                price = int(price_text)
            except Exception as e:
                price = 0

            # 在售数量
            xiaoquListItemSellCount = child.find("div", {"class": "xiaoquListItemSellCount"})
            houses = int("".join(xiaoquListItemSellCount.find("span").string))

            xiaoqu = XiaoQu()
            xiaoqu.xiaoqu_name = name
            xiaoqu.xiaoqu_id = xiaoqu_id
            xiaoqu.area = area
            xiaoqu.area_2 = area_2
            xiaoqu.build_year = buding_year
            xiaoqu.turnover = turnover  # 成交量
            xiaoqu.price = price  # 均价
            xiaoqu.houses = houses  # 在售数量
            xiaoqu.update_batch = update_batch  # 爬取批次
            ret_xiaoqu.append(xiaoqu)
            self.log.info(str(xiaoqu))

        self.log.info("1.3 PG页面解析：pg页面解析成功！")
        return ret_xiaoqu

    def get_html_xiaoqu_count(self, html):
        """
        获取页面内的小区总数
        """
        if html is None:
            self.log.error("页面解析(page)：pg页面为空！")
            return

        bsObj = BeautifulSoup(html, "html.parser", from_encoding="utf-8")

        h2 = bsObj.find("h2", {"class": "total fl"})
        span = h2.find("span")

        return int(span.text)

    def get_html_house_count(self, html):
        """
        获取页面内房源的总数
        """
        bs = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
        h2 = bs.find("h2", {"class": "total fl"})
        span = h2.find("span")
        return int(span.text)

    def get_html_house_url_list(self, html):
        """
        从html内提取房源url
        """
        ret_url_list = []

        bs = BeautifulSoup(html, "html.parser", from_encoding="utf-8")
        house_content = bs.find("ul", {"class": "sellListContent"})
        print house_content
        house_content_list = house_content.findAll("li", {"class": "clear LOGVIEWDATA LOGCLICKDATA"})

        print house_content_list
        if not house_content_list:
            return ret_url_list

        for house_info in house_content_list:
            url = house_info.a["href"]
            ret_url_list.append(url)
        return ret_url_list

    def get_html_house_detail(self, house_id, html_body, update_batch):
        """
        从html 内提取房源详细信息
        """

        house_id = house_id
        # 标题
        house_title = ""
        # 好房
        is_good_house = False
        # 总价
        price_total = 0
        # 单价
        price_unit = 0
        # 房屋户型
        bed_room = 1
        living_room = 1
        # 建筑面积
        house_size = 0.0
        # 房屋朝向
        house_orientation = ""
        # 配备电梯
        have_elevator = False
        # 挂牌时间
        listing_time = None

        # title
        bs = BeautifulSoup(html_body, "html.parser", from_encoding="utf-8")
        house_title = bs.find("h1", {"class": "main"}).get_text()
        print house_title

        # is_good_house
        html_a = bs.find("a", {"class": "haofangInfo CLICKDATA VIEWDATA"})
        if html_a:
            is_good_house = True
        print is_good_house

        # price_total
        price_html = bs.find("div", {"class": "price"})
        price_total = int("".join(price_html.find("span", {"class": "total"}).string)) * 10000
        # price_unit

        price_unit_text = price_html.find("div", {"class": "unitPrice"}).get_text()
        price_unit = int(price_unit_text.split(u"元")[0])
        print price_unit

        return

        ershoufang_data = []
        communityName = "null"
        areaName = "null"
        total = "null"
        unitPriceValue = "null"

        tag_com = bs.find("div", {"class": "communityName"}).find("a")

        tag_total = bs.find("span", {"class": "total"})
        if tag_total is not None:
            total = tag_total.get_text()
        else:
            self.log.error("页面解析(detail)：找不到total标签！")

        tag_unit = bs.find("span", {"class": "unitPriceValue"})
        if tag_unit is not None:
            unitPriceValue = tag_unit.get_text()
        else:
            self.log.error("页面解析(detail)：找不到total标签！")

        ershoufang_data.append(id)
        ershoufang_data.append(communityName)
        ershoufang_data.append(areaName)
        ershoufang_data.append(total)
        ershoufang_data.append(unitPriceValue)

        # print(bsObj.find("div",{"class":"introContent"}).find("div",{"class":"base"}).find("div",{"class":"content"}).ul)
        counta = 12
        for a_child in bs.find("div", {"class": "introContent"}).find("div", {"class": "base"}).find("div", {
            "class": "content"}).ul.findAll("li"):
            # print(child1)
            [s.extract() for s in a_child("span")]
            ershoufang_data.append(a_child.get_text())
            counta = counta - 1

        while counta > 0:
            ershoufang_data.append("null")
            counta = counta - 1

        countb = 8
        for b_child in bs.find("div", {"class": "introContent"}).find("div", {"class": "transaction"}).find("div", {
            "class": "content"}).ul.findAll("li"):
            information = b_child.span.next_sibling.next_sibling.get_text()
            ershoufang_data.append(information)
            countb = countb - 1

        while countb > 0:
            ershoufang_data.append("null")
            countb = countb - 1

        self.log.info("2.3 页面解析(detail)：页面解析成功！")
        return ershoufang_data
