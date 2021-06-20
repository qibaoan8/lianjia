#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 

"""
File: fuse.py
Author: wang.gaofei(wang.gaofei@alibaba-inc.com)
Date: 2021/6/19
"""
import datetime
import time

"""
熔断器
"""


class Fuse():
    def __init__(self):
        self.last_use = datetime.datetime.now()
        self.used_count = 0
        # 时间周期 秒
        self.time_cycel = 1
        self.max_use_count = 10

    def check(self, sleep=0):
        """
        检查是否熔断
        """
        if sleep > 0:
            time.sleep(sleep)
            return

        while True:
            now = datetime.datetime.now()
            if (now - self.last_use).seconds >= self.time_cycel:
                self.last_use = now
                self.used_count += 1
                return
            else:
                if self.used_count < self.max_use_count:
                    self.used_count += 1
                    return
                else:
                    time.sleep(0.1)

    def set_time_cycel(self, cycel):
        if cycel > 0:
            self.time_cycel = cycel
            return True
        return False

    def set_max_use_count(self, count):
        if count > 0:
            self.max_use_count = count
            return True
        return False


if __name__ == '__main__':
    fuse = Fuse()
    fuse.check()
    fuse.check()
    fuse.check()
    fuse.check()
