# -*- coding: utf_8 -*-
# @Create   : 2021/9/13 9:12
# @Author   : yh
# @Remark   : 存放Table db数据库的操作方法
from typing import Type, List, Any

from superbsapi import CBSHandleLoc

from .BaseDB import BaseDB
from .db_def.def_table import *
from .db_def.def_type import type_map, type_c_python, type_c_str
from .exception import DBError, DataError
from . import Model

symbol_map = {
    'e': TBDB_FMC_EQUAL,  # 等于
    'ne': TBDB_FMC_UNEQUAL,  # 不等于
    'gt': TBDB_FMC_GREATERTHAN,  # 大于
    'lt': TBDB_FMC_LESSTHAN,  # 小于
    'gte': TBDB_FMC_EQUALORGREATERTHAN,  # 大于等于
    'lte': TBDB_FMC_EQUALORLESSTHAN,  # 小于等于
    'between': TBDB_FMC_GREATERTHAN
    # 其他的类型，以后用到了再添加
}


class TableDB(BaseDB):

    def __init__(self):
        super().__init__()
        self.__table = None

    def open(self, file: str, table: str = None, host: str = None, port: str = None):
        """
        打开table数据库
        :param file: 数据库名称
        :param table: 数据库表名
        :param host: 主机ip
        :param port: 端口
        """
        host = host or self.host
        port = port or self.port

        try:
            self.exec_tree('Tabledb_ReopenDb', file)
        except DBError:
            try:
                self.__chl = CBSHandleLoc()
                self.exec_tree('Tabledb_Alloc', host, file, port)
            except DBError as e:
                raise DBError(e.err_code, '打开数据库[%s]失败' % file)

        self.__table = table

        return self

    def table_list(self) -> list:
        """
        获取所有数据库表名
        """
        res = list()
        self.exec_bs('bs_tabledb_get_all_tablenames', res)

        return res

    def fields(self, table_name: str = None) -> dict:
        """
        获取表的所有字段及其属性
        :param table_name: 要获取字段类型的表名
        :return:
        """
        res = list()
        table = table_name or self.__table
        if not table:
            raise DataError('找不到table，请打开或传入表')

        self.exec_bs('bs_tabledb_get_fields', table, res)
        return {i['name']: i for i in res}

    def create_table(self, table: str, model: Type[Model], flag=None, **kwargs) -> None:
        """
        新建表
        :param table: 要创建的数据库名称
        :param model: 要创建的表，如果您不显式的声明字段长度，则默认长度为200
        :param flag: 创建风格，不传会自动判断
        :param kwargs: 附加参数
        """
        flag = 0x00000000
        if kwargs.get('auto_id'):
            flag += BS_TDTF_FLAG_AUTOID
        if kwargs.get('auto_id_index'):
            flag += BS_TDTF_FLAG_INDEXID
        if kwargs.get('primary_key'):
            flag += BS_TDTF_FLAG_PRIMARYTABLE
        if kwargs.get('desc'):
            flag += BS_TDTF_FLAG_PMKI_DESCORDER
        if kwargs.get('dyn'):
            flag += BS_TDTF_FLAG_DYNTABLE
        if not flag:
            flag = BS_TDTF_FLAG_AUTOID

        field_list = list()
        for field in model.__fields__.values():
            if not type_map.get(field.type_.__name__):
                raise DataError('不支持此解析字段的类型，字段名: %s, 解析到的类型: %s' % (field.name, field.type_.__name__))

            field_list.append({"name": field.name, "uType": type_map[field.type_.__name__],
                               "uDataLen": field.type_.max_length if hasattr(field.type_, 'max_length') else 200})

        self.exec_bs('bs_tabledb_create_table', table, field_list, flag)

    def insert(self, table: str, data: List[tuple]) -> None:
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

    @staticmethod
    def __conversion_data(value: Any, value_type: int) -> Any:
        """
        校验数据类型是否合法并value到对应转换类型
        """
        if not type_c_str.get(value_type):
            raise DataError('无法理解的C++数据类型：没有定义此类型：%s' % value_type)
        if not type_c_python.get(value_type):
            raise DataError('从C++数据类型转为Python类型时出错，没有定义转换关系：%s' % type_c_str[value_type])

        try:
            value = eval(type_c_python[value_type])(value)
        except ValueError:
            raise DataError('无法转换数据类型：将传入的数据类型%s转为C++类型%s（实际转为Python类型%s）' % (
                type(value).__name__, type_c_str[value_type], type_c_python[value_type]))

        return value

    def filter(self, table_name: str = None, count: int = 0, **kwargs) -> List[dict]:
        """
        根据条件查询符合的记录
        :param table_name: 要查询的表名（已经在open方法中打开表以后就不用再传入）
        :param count: 要获取的总条数
        :param kwargs: 查询条件
        """
        self.__table = table_name or self.__table

        if len(kwargs) > 1 or not kwargs:
            raise DataError('每次有且只能查询一个条件')
        if not self.__table:
            raise DataError('没有打开任何表')

        key = next(iter(kwargs))
        value = kwargs[key]
        table_fields = self.fields()

        try:
            key, symbol = key.rsplit('__', 1)
            if symbol not in symbol_map:
                raise DataError('查询操作错误！正确操作包含：gt、lt等')
        except ValueError:
            symbol = 'e'
        if not table_fields.get(key):
            raise DataError('数据库中没有此字段：%s' % key)

        query_conditions = list()
        value_type = table_fields[key]['uType']
        if symbol == 'between':
            if not isinstance(value, list) or len(value) != 2:
                raise DataError('between操作有且仅有两个条件')
            for i in value:
                query_conditions.append({'val': self.__conversion_data(i, value_type), 'type': value_type})
        else:
            query_conditions.append({'val': self.__conversion_data(value, value_type), 'type': value_type})

        res_list = list()
        self.exec_tree('Tabledb_SelectRecordsByField', self.__table, count, key, symbol_map[symbol], query_conditions,
                       res_list)

        return res_list
