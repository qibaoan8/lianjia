#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
# 
########################################################################
 
"""
File: models.py
Author: mushi(mushi.hgx@alibaba-inc.com)
Date: 2018/03/07 20:57:21
"""

import os
import json
# from framework.libs import mysqldb
import traceback

from . import mysqldb

from .utils_str import parse_url
from .codecs import ResponseJsonSerializer
from .exceptions import ENotImplement, EInvalidParam, EInvalidData, EUnsupported


class BaseModel(object):
    """

    """
    def __init__(self, schema=None):
        """

        """
        super(BaseModel, self).__init__()
        self.table = None
        self.schema = schema
        self._init_db()

    def all(self, limit=200, dictionary=True):
        """
        获取该表所有数据，默认返回200条,先临时做这个限制

        :param limit:
        :param dictionary 返回字典格式还是tuple格式
        :return ret: list, 查询结果，list中每一个项目为dict类型得kv对，分别对应数据库中的字段
        """
        self.__pre_check()
        limit_str = self.__parse_limit(limit)
        sql = "select * from %s %s" % (self.table, limit_str)
        ret = self.query(sql, dictionary=dictionary)
        return ret

    def get(self, limit=0, offset=0, dictionary=True, **kwargs):
        """
        给定一组条件，返回符合条件的结果行，相当于 select * from tbl_xxx where a=1 and b=2
        相比于直接使用filter，本方法可读性更好，如：roles = self._model.katao_role().get(group_id=group_id)

        :param limit: int
        :param offset: int
        :param dictionary bool, 返回字典格式还是tuple格式
        :param kwargs:
        :return:
        """
        if kwargs == {}:
            kwargs = None
        return self.filter(cons=kwargs, limit=limit, offset=offset, dictionary=dictionary)

    def filter(self, cons, cols=None, order=None, limit=0, offset=0, dictionary=True):
        """
        根据条件查询指定字段

        :param cons: dict, 查询条件
        :param cols: list, 要查询的字段列表
        :param order list, 排序规则，参见__parse_order
        :param limit: int
        :param offset: int
        :param dictionary bool, 返回字典格式还是tuple格式
        :return:
        """
        self.__pre_check()
        con_str = self._parse_cons(cons)
        cols_str = self.__parse_cols(cols)
        order_str = self.__parse_order(order)
        limit_str = self.__parse_limit(limit=limit, offset=offset)
        sql = "select %s from %s %s %s %s" % (cols_str, self.table, con_str, order_str, limit_str)
        ret = self.query(sql, dictionary=dictionary)
        return ret

    def query(self, sql, dictionary=True):
        """
        拦截下，留点日志，方便debug
        :param sql: str
        :param dictionary bool 返回字典格式还是tuple格式
        :return:
        """
        ret = self.db_handler.query(sql, dictionary=dictionary)
        return ret

    def insert(self, data, on_duplicate_update_key=None):
        """
        插入数据库，插入多条和一条的接口相同

        :param on_duplicate_update_key: list 当主键或者唯一键冲突时更新哪些key的值？key必须再data中存在
        :param data: list, 每个项目为一个dict, key为列名，value为目标值, 需要包含一行的所有列
        :return:
        """
        self.__pre_check()

        #sql格式：insert into xxx (a, b, c) values(%s, %s, %s)
        if len(data) <= 0:
            return -1
        key_list = data[0].keys()
        keys = ",".join(key_list)
        values = ",".join(["%s" for i in range(len(data[0]))])
        sql = "insert into %s (%s) values(%s)" % (self.table, keys, values)
        if on_duplicate_update_key is not None:
            parts = ['{key}=values({key})'.format(key=key) for key in on_duplicate_update_key]
            sql = '%s ON DUPLICATE KEY UPDATE %s' % (sql, ', '.join(parts))

        #格式： [("a", "a", a), ("b", "b", b)]
        data_list = []
        for item in data:
            tmp_list = []
            for k in key_list:
                if type(item[k]) in [dict, list, tuple]:
                    tmp_list.append(json.dumps(item[k], cls=ResponseJsonSerializer, ensure_ascii=False))
                    continue
                tmp_list.append(item[k])
            data_list.append(tuple(tmp_list))

        ret = self.db_handler.execute_many(sql, data_list)
        return ret

    def replace(self, data):
        """
        插入数据库,如果有则删除之再插入，替换多条和一条的接口相同，返回最后一个插入行的@rowid，没有插入则返回-1
        请注意：本方法与insert into on dumplicate update 相比sql可读性更好，但会删除原来的数据！

        :param data: list, 每个项目为一个dict, key为列名，value为目标值, 需要包含一行的所有列
        :return:
        """
        self.__pre_check()

        #sql格式：replace into xxx (a, b, c) values(%s, %s, %s)
        if len(data) <= 0:
            return -1
        key_list = data[0].keys()
        keys = ",".join(key_list)
        values = ",".join(["%s" for i in range(len(data[0]))])
        sql = "replace into %s (%s) values(%s)" % (self.table, keys, values)

        #格式： [("a", "a", a), ("b", "b", b)]
        data_list = []
        for item in data:
            tmp_list = []
            for k in key_list:
                if type(item[k]) in [dict, list, tuple]:
                    tmp_list.append(json.dumps(item[k], cls=ResponseJsonSerializer,ensure_ascii=False))
                    continue
                tmp_list.append(item[k])
            data_list.append(tuple(tmp_list))

        ret = self.db_handler.execute_many(sql, data_list)
        return ret

    def update(self, data, cons=None):
        """
        更新数据

        :param data: dict, 要更新的字段的kv对
        :param cons: dict, 筛选条件
        """
        con_str = self._parse_cons(cons)
        tmp_list = []
        for k, v in data.items():
            v_type = type(v)
            if v_type in [int, long, float]:
                tmp_list.append("%s=%s" % (k, v))
            elif v_type in [dict, list, tuple]:
                tmp_list.append("%s='%s'" % (k, json.dumps(v, cls=ResponseJsonSerializer, ensure_ascii=False)))
            else:
                tmp_list.append("%s='%s'" % (k, v))
        data_str = ",".join(tmp_list)
        sql = "update %s set %s %s" % (self.table, data_str, con_str)
        ret = self.db_handler.execute(sql)

        return ret

    def delete(self, cons):
        """
        删除数据库部分数据，通过cons进行过滤
        :param cons: dict, 删除条件
        :return:
        """
        con_str = self._parse_cons(cons)
        if "where" not in con_str:
            return False
        sql = 'DELETE FROM %s %s' %(self.table, con_str)
        ret = self.db_handler.execute(sql)
        return ret

    def raw(self, sql, dictionary=True):
        """
        原始SQL查询接口

        :param sql: str, 原始sql语句
        :return:
        """

        if sql.lower().startswith("select"):
            return self.query(sql, dictionary=dictionary)
        return self.db_handler.execute(sql)

    def _parse_cons(self, cons):
        """
        将条件dict转化为sql语句
        因为子类中有用到，所以改为保护函数

        :param cons:
        :return:
        """
        if cons is None or len(cons) == 0:
            return "where 1=1"
        tmp_list = []
        for k, v in cons.items():
            if isinstance(v, int) or isinstance(v, float):
                con = "%s=%s " % (k, v)
            elif isinstance(v, list) and len(v) > 1:
                con = "%s in (%s) " %(k, self.__parse_in(v))
            elif isinstance(v, list) and len(v) == 1:
                fix = self.__get_fix(v[0])
                con = "%s=%s%s%s " % (k, fix, v[0], fix)
            else:
                con = "%s='%s' " % (k, v)
            tmp_list.append(con)

        con_str = "where " + " and ".join(tmp_list)
        return con_str

    @staticmethod
    def __parse_cols(cols):
        """
        将要查询的列转化为sql

        :param cols:
        :return:
        """
        if cols is None or len(cols) == 0:
            return "*"
        return ",".join(cols)

    @staticmethod
    def __parse_order(order):
        """
        生成 order 条件, 参数是个二维数组
        请注意，按照sql规范，参与order的字段必须出现在结果字段列表中，排序只支持desc|asc, 本方法并不会做此检查，请自行保证
        :param order: [[col1, desc], [col2, asc]]
        :return:  order by col1 desc, col2 asc
        """

        if order is None or len(order) == 0:
            return ""

        return 'order by ' + ', '.join([' '.join(i) for i in order])

    def __parse_limit(self, limit=0, offset=0):
        """
        生成 limit 条件
        :return:
        """
        if not isinstance(limit, int) or not isinstance(offset, int):
            raise EInvalidParam('SQL_ERROR: limit/offset must be int type')

        if limit == 0:
            return ""
        return 'limit %s offset %s' % (limit, offset)

    def __pre_check(self):
        """
        #1TODO nothing
        """
        if self.table is None:
            raise ENotImplement("DB table is None") 

        if self.db_handler is None:
            self._init_db()

    def __parse_in(self, list_data):
        fixed_list = []
        for item in list_data:
            fix = self.__get_fix(item)
            fixed_list.append("{fix}{item}{fix}".format(fix=fix, item=item))
        return ', '.join(fixed_list)

    def __get_fix(self, item):
        """根据元素类型，确定他前后应该用什么字符包围：int/float空字符，其它单引号"""
        if isinstance(item, int) or isinstance(item, float):
            return ""
        else:
            return "'"

    def _init_db(self):
        """
        数据库初始化
        """
        self.uri = 'mysql+mysqlconnector://root:root@127.0.0.1:3306/house'

        db = parse_url(self.uri)
        self.db_handler = mysqldb.Connection(db.server, db.database, user=db.username, password=db.password, **db.kwargs)

