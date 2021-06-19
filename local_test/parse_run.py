#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 

"""
File: parse_run.py
Author: wang.gaofei(wang.gaofei@alibaba-inc.com)
Date: 2021/6/19
"""
import json

from lib.html_parser import HtmlParser
from lib.model_table import XiaoQuModel

xiaoqu_db = XiaoQuModel()


def main_test_xiaoqu():
    xiaoqu_html = ""
    with open("xiaoqu.html") as f:
        xiaoqu_html = f.read()

    html = HtmlParser()
    ret_list = html.get_html_xiaoqu_list(xiaoqu_html)
    for i in ret_list:
        print i
    # xiaoqu_db.insert(ret_list)


def main_test_house_list():
    html = ""
    with open("house_list.html") as f:
        html = f.read()

    hp = HtmlParser()
    count = hp.get_html_house_count(html)
    print count

    url_list = hp.get_html_house_url_list(html)
    print url_list


def main_test_house_detail():
    html = ""
    with open("house_detail.html") as f:
        html = f.read()

    hp = HtmlParser()
    house = hp.get_html_house_detail("1", html, "1")
    print house


if __name__ == '__main__':
    main_test_house_detail()
