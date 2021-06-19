#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 

"""
File: log_run.py
Author: wang.gaofei(wang.gaofei@alibaba-inc.com)
Date: 2021/6/19
"""
import logging
import sys


def get_my_log():

    pass
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    log = logging.getLogger("name")
    # stdout = logging.StreamHandler(sys.stdout)
    # log.addHandler(stdout)
    log.info("abc")
    # logging.info("abc")

if __name__ == '__main__':
    get_my_log()