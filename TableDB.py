# -*- coding: utf_8 -*-
# @Create   : 2021/9/13 9:12
# @Author   : yh
# @Remark   : 存放Table db数据库的操作方法
from typing import Type, List

from superbsapi import *

from BaseDB import BaseDB
from db_def.def_table import *
from db_def.def_type import type_map
from exception import DBError, DataError
from model import Model


class TableDB(BaseDB):

    def open(self, db: str, host: str = None, port: str = None):
        """
        打开table数据库
        :param db: 数据库名称
        :param host: 主机ip
        :param port: 端口
        """
        host = host or self.host
        port = port or self.port

        try:
            self.exec_tree('Tabledb_ReopenDb', db)
        except DBError:
            try:
                self.__chl = CBSHandleLoc()
                self.exec_tree('Tabledb_Alloc', host, db, port)
            except DBError as e:
                raise DBError(e.err_code, '打开数据库表[%s]失败' % db)

        return self

    def table_list(self) -> list:
        """
        获取所有数据库表名
        """
        res = list()
        self.exec_bs('bs_tabledb_get_all_tablenames', res)

        return res

    def create_table(self, table: str, model: Type[Model], flag=None, **kwargs) -> None:
        """
        新建表
        :param table: 要创建的数据库名称
        :param model: 要创建的表，如果您不显式的声明字段长度，则默认长度为200
        :param flag: 创建风格，不传会自动判断
        :param kwargs: 附加参数
        """
        if kwargs.get('auto_id'):
            flag = BS_TDTF_FLAG_AUTOID
        if kwargs.get('auto_id_index'):
            flag = BS_TDTF_FLAG_INDEXID
        if kwargs.get('primary_key'):
            flag = BS_TDTF_FLAG_PRIMARYTABLE
        if kwargs.get('desc'):
            flag = BS_TDTF_FLAG_PMKI_DESCORDER
        if kwargs.get('dyn'):
            flag = BS_TDTF_FLAG_DYNTABLE
        if not flag:
            flag = BS_TDTF_FLAG_AUTOID

        field_list = list()
        for field in model.__fields__.values():
            if not type_map.get(field.type_.__name__):
                raise DataError('不支持此解析字段的类型，字段名: %s, 解析到的类型: %s' % (field.name, field.type_.__name__))

            field_list.append({"name": field.name, "uType": type_map[field.type_.__name__],
                               "uDataLen": field.type_.max_length if hasattr(field.type_, 'max_length') else 200})

        self.exec_bs('bs_tabledb_create_table', table, field_list, flag)

    def insert(self, table: str,  data: List[tuple]) -> None:
        """
        向表中插入数据
        :param table: 表名
        :param data: 要insert的数据
        """
        if not isinstance(data, list):
            raise DataError('错误的数据类型，data应为列表，其中的元素应为元组')

        insert_list = list()

        for item in data:
            insert_list.append({'name': item[0], 'value': item[1], 'valuetype': self._check_item(item)})

        self.exec_bs('bs_tabledb_insert_record', table, insert_list)
