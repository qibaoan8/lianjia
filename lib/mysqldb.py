#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2018 alibaba-inc.com, Inc. All Rights Reserved
# 
########################################################################


""" 
A lightweight wrapper around MySQLdb.
File: mysqldb.py
Author: mushi.hgx(mushi.hgx@alibaba-inc.com)
"""

import copy
import itertools
import logging
import os
import time
import mysql.connector
import traceback


class Connection(object):
    """
    A lightweight wrapper around MySQLdb DB-API connections.

    The main value we provide is wrapping rows in a dict/object so that
    columns can be accessed by name. Typical usage::

        db = mysqldb.Connection("localhost", "mydatabase")
        for article in db.query("SELECT * FROM articles"):
            print article.title

    Cursors are hidden by the implementation, but other than that, the methods
    are very similar to the DB-API.

    We explicitly set the timezone to UTC and assume the character encoding to
    UTF-8 (can be changed) on all connections to avoid time zone and encoding errors.

    The sql_mode parameter is set by default to "traditional",
    which "gives an error instead of a warning"
    (http://dev.mysql.com/doc/refman/5.0/en/server-sql-mode.html). However, it can be set to
    any other mode including blank (None) thereby explicitly clearing the SQL mode.
    """

    def __init__(self, host, database, user=None, password=None,
                 max_idle_time=7 * 3600, connect_timeout=60,
                 charset="utf8", **kwargs):
        """
        Create a connection to MySQL
        args:
            host:the ip:port of MySQL server
            database:db name
            user:db user name, default is None
            password:db passwd, default is None
        """
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)
        self.connect_timeout = int(connect_timeout)

        args = dict(db=database)
        if user is not None:
            args["user"] = user
        if password is not None:
            args["passwd"] = password

        # We accept a path to a MySQL socket file or a host(:port) string
        if "/" in host:
            args["unix_socket"] = host
        else:
            self.socket = None
            pair = host.split(":")
            if len(pair) == 2:
                args["host"] = pair[0]
                args["port"] = int(pair[1])
            else:
                args["host"] = host
                args["port"] = 8507
        args['charset'] = charset
        args['connect_timeout'] = self.connect_timeout

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error("Cannot connect to MySQL on %s", self.host,
                        exc_info=True)

    def __del__(self):
        self.close()

    def close(self):
        """Closes this database connection.
        You should use close() after all your sqls are executed over
        """
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        """Closes the existing database connection and re-opens it."""
        self.close()
        for i in range(0, 3):
            self._db = mysql.connector.connect(**self._db_args)
            if self._db is not None:
                self._db.autocommit = True
                break
            else:
                time.sleep(1)

    def query(self, query, dictionary=True, *parameters, **kwparameters):
        """Query the mysql
        Args:
            query: the sql to query
            dictionary: optional, return item as dict or tuple, default is True
            parameters: optional, default is []
            kwparameters: optional, default is {}
        Return:
            a row list for the given query and parameters
        """
        result = []
        cursor = self._cursor()
        ret = self._execute(cursor, query, parameters, kwparameters)
        if ret != -1:
            if dictionary:
                column_names = [d[0] for d in cursor.description]
                result = [Row(itertools.izip(column_names, row)) for row in cursor]
            else:
                result = [row for row in cursor]
        #cursor.close()
        self.close()
        return result

    def execute(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query.
        Args:
            query: the sql to insert/update/delete
            parameters: optional, default is []
            kwparameters: optional, default is {}
        Return:
            the lastrowid from the query
        """
        return self._execute_lastrowid(query, *parameters, **kwparameters)

    def _execute_lastrowid(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the lastrowid from the query."""
        result = -1
        cursor = self._cursor()
        ret = self._execute(cursor, query, parameters, kwparameters)
        if ret != -1:
            result = cursor.lastrowid
        cursor.close()
        return result

    def _execute_rowcount(self, query, *parameters, **kwparameters):
        """Executes the given query, returning the rowcount from the query."""
        result = -1
        cursor = self._cursor()
        ret = self._execute(cursor, query, parameters, kwparameters)
        if ret != -1:
            result = cursor.rowcount
        cursor.close()
        return result

    def execute_many(self, query, parameters):
        """Executes the given query against all the given param sequences.
        Args:
            query: the sql patten to query
            parameters: the values of the paras in the sql
        Return:
            the lastrowid from the query

        Eg:
        query = "insert into xxx (a, b) values(%s, %s)"
        parameters = [("xxx", "xxx"), ("bbb", "bbb")]
        """
        return self._executemany_lastrowid(query, parameters)

    def _executemany_lastrowid(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the lastrowid from the query.
        """
        result = -1
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            result = cursor.lastrowid
        except Exception as e:
            logging.error("Error occurd in executemany_lastrowid, error=[%s]" % str(e))
        finally:
            cursor.close()
        return result

    def _executemany_rowcount(self, query, parameters):
        """Executes the given query against all the given param sequences.

        We return the rowcount from the query.
        """
        result = -1
        cursor = self._cursor()
        try:
            cursor.executemany(query, parameters)
            result = cursor.rowcount
        except Exception:
            logging.error("Error occurd in executemany_rowcount")
        finally:
            cursor.close()
        return result

    def start_transaction(self):
        """Start a transaction to exec sql.
        When a transaction started, the sql will not be commited automatically
        until the transaction commit
        """
        self._db.autocommit = False

    def commit_transaction(self):
        """commit the sqls of this transaction"""
        cursor = self._cursor()
        cursor.close()
        self._db.commit()
        self._end_transaction()

    def rollback_transaction(self):
        """Rollback a transaction, the sql of this transaction will not be commited"""
        cursor = self._cursor()
        cursor.close()
        self._db.rollback()
        self._end_transaction()

    def _end_transaction(self):
        """End a transaxtion, the auto_commit will be open"""
        self._db.autocommit=True

    def _ensure_connected(self):
        # Mysql by default closes client connections that are idle for
        # 8 hours, but the client library does not report this fact until
        # you try to perform a query and it fails.  Protect against this
        # case by preemptively closing and reopening the connection
        # if it has been idle for too long (7 hours by default).
        if (self._db is None or not self._db.is_connected() or
            (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def _execute(self, cursor, query, parameters, kwparameters):
        try:
            return cursor.execute(query, kwparameters or parameters)
        except Exception as e:
            logging.error("Error exec sql, error=[%s]" % str(e))
            self.close()
            return -1

    #alias of other executions
    update = _execute_rowcount
    updatemany = _executemany_rowcount

    insert = _execute_lastrowid
    insertmany = _executemany_lastrowid


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

