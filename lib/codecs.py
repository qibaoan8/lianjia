#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
#

"""
File: codecs
Author: 上郡(shangjun.csb@alibaba-inc.com)
Date: 2020-03-06 09:05
"""
import decimal
import json
from datetime import datetime
from elasticsearch_dsl import DocType


class ResponseJsonSerializer(json.JSONEncoder):
    """
    decimal型浮点数的序列化
    """
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            if obj._isinteger():
                return int(obj)
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, DocType):
            return obj.to_dict()
        return super(ResponseJsonSerializer, self).default(obj)