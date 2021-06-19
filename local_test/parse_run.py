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

if __name__ == '__main__':
    xiaoqu_html = ""
    with open("xiaoqu.html") as f:
        xiaoqu_html = f.read()

    html = HtmlParser()
    ret_list = html.get_html_xiaoqu_list(xiaoqu_html)
    for i in ret_list:
        print i
    # xiaoqu_db.insert(ret_list)
