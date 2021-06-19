# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 16:38:37 2018

@author: zhangying
"""

import logging
import datetime
import sys


class MyLog():
    """程序调试日志输出"""

    def __init__(self, name, filepath):
        """初始化属性"""

        # 初始化日志器
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.formatter = logging.Formatter(self.format)

        # 输出到文件
        filepath = (filepath + "/log_" + str(datetime.date.today()) + ".txt")
        self.file_handler = logging.FileHandler(filepath)
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        # 输出到控制台
        self.stream_handler = logging.StreamHandler(sys.stdout)
        self.stream_handler.setLevel(level=logging.DEBUG)
        # formatter = logging.Formatter(LOG_FORMAT)
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

    def getMyLogger(self):
        """获得自定义的日志器"""
        return self.logger
