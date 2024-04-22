# -*- coding: UTF-8 -*-
# @Create   : 2021/8/19 14:56
# @Author   : yh
# @Remark   : mx框架db层
from .CacheDB import CacheDB
from .mqDB import MQ
from .TableDB import TableDB
from .TreeDB import TreeDB


class DB:

    def __init__(self, *args, **kwargs):
        self._tree = None
        self._table = None
        self._mq = None
        self._cache = None

    @property
    def tree(self):
        if self._tree:
            return self._tree
        self._tree = TreeDB()
        return self._tree

    @property
    def table(self):
        if self._table:
            return self._table
        self._table = TableDB()
        return self._table

    @property
    def mq(self):
        if self._mq:
            return self._mq
        self._mq = MQ()
        return self._mq

    @property
    def cache(self):
        if self._cache:
            return self._cache
        self._cache = CacheDB()
        return self._cache
