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
from lib.model_table import XiaoQuModel

if __name__ == '__main__':
    xiaoqu = XiaoQuModel()
    all = xiaoqu.all()
    print all