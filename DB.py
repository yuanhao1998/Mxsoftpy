# -*- coding: utf_8 -*-
# @Create   : 2021/8/19 14:56
# @Author   : yh
# @Remark   : mx框架db层
from .CacheDB import CacheDB
from .mqDB import MQ
from .TableDB import TableDB
from .TreeDB import TreeDB


class DB:

    def __init__(self, *args, **kwargs):
        self.tree = TreeDB()
        self.table = TableDB()
        self.mq = MQ()
        self.cache = CacheDB()
