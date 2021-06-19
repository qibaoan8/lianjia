#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 

"""
File: db_run.py
Author: wang.gaofei(wang.gaofei@alibaba-inc.com)
Date: 2021/6/19
"""
from lib.log import MyLog
from lib.model_table import XiaoQuModel
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
log = MyLog("db_test", "logs").getMyLogger()
if __name__ == '__main__':
    xiaoqu = XiaoQuModel()
    all = xiaoqu.filter({"area_2": u"崇文门"})
    for i in all:
        log.info(str(i))