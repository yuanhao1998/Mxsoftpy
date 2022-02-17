# -*- coding: utf_8 -*-
# @Create   : 2021/9/13 9:12
# @Author   : yh
# @Remark   : 存放Table db数据库的操作方法
import logging
import re
from typing import Type, List, Union

from superbsapi import CBSHandleLoc

from .BaseDB import BaseDB
from .db_def.def_type import type_map
from .exception import DBError, DataError
from . import Model

symbol_map = {
    'ne': '!=',  # 不等于
    'gt': '>',  # 大于
    'lt': '<',  # 小于
    'gte': '>=',  # 大于等于
    'lte': '<=',  # 小于等于
    'like': 'like',  # 模糊匹配，使用 * 做为通配符
    'in': 'in',  # 范围查找（枚举）
    'between': 'between',  # 范围查找（范围）
    # sql中支持limit,   # eq:limit a,b 从第a个开始，查询b条数据
    # 其他的类型，数据库支持了再添加
}


class TableDB(BaseDB):

    def open(self, file: str, host: str = None, port: str = None):
        """
        打开table数据库
        :param file: 数据库名称
        :param host: 主机ip
        :param port: 端口
        """
        host = host or self.host
        port = port or self.port

        try:
            self.exec_tree('Tabledb_ReopenDb', file)
        except DBError:
            try:
                _host, _port = self._get_host_port(file)
                host, port = host or _host, port or _port
                self.__chl = CBSHandleLoc()
                self.exec_tree('Tabledb_Alloc', host, file, port)
                logging.warning('正在重新连接数据库并打开table[%s]' % file)
            except DBError as e:
                raise DBError(e.err_code, '打开数据库[%s]失败' % file)

        return self

    def table_list(self) -> list:
        """
        获取所有数据库表名
        """
        res = list()
        self.exec_bs('bs_tabledb_get_all_tablenames', res)

        return res

    def fields(self, table) -> dict:
        """
        获取表的所有字段及其属性
        :param table: 要获取字段类型的表名
        :return:
        """
        res = list()
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

        field_list = list()
        for field in model.__fields__.values():
            if not type_map.get(field.type_.__name__):
                raise DataError('不支持此解析字段的类型，字段名: %s, 解析到的类型: %s' % (field.name, field.type_.__name__))

            field_list.append({"name": field.name, "uType": type_map[field.type_.__name__],
                               "uDataLen": field.type_.max_length if hasattr(field.type_, 'max_length') else 200})

        self.exec_bs('bs_tabledb_create_table', table, field_list, flag)

    def exec_for_sql(self, sql: str) -> List[dict]:
        """
        根据sql查询数据
        :param sql: 查询sql
        """
        res_list = []
        self.exec_tree('Tabledb_Query', sql, res_list)
        return res_list

    def insert(self, table: str, keys: tuple, values: List[tuple]):
        """
        插入数据
        :param table:数据库表，必传
        :param keys:插入的字段名，需传表中所有字段，必传
        :param values: 插入的字段值，必传
        eq:  db.insert(db,(a,b,c),[(1,2,3),(1,2,3)]
        """
        if not isinstance(keys, tuple):
            raise DataError('错误的数据类型，keys应为元组')

        if not isinstance(values, list):
            raise DataError('错误的数据类型，values应为列表，其中的元素多个字段应为元组，单个字段应为字符串')

        if len(keys) != len(values[0]):
            if not isinstance(values[0], tuple):
                raise DataError('错误的数据类型，values应为列表，其中的元素多个字段应为元组，单个字段应为字符串或数字')
            raise DataError('keys数量与value数量不符，eq: db.insert(db,(a,b,c),[(1,2,3),(1,2,3)]')

        keys = ','.join(keys)
        sql = f"insert into {table} ({keys}) values {','.join([str(i) for i in values])}"

        return self.exec_for_sql(sql)

    def filter(self, table: str = None, prop_list: Union[str, list] = None, page_size=0, page_index=1,
               default_expression=None, count: int = None, **kwargs):
        """
        table表筛选
        :param prop_list: 筛选需查询的字段，不传查所有
        :param table: 数据库表，不传默认使用open传入的table
        :param default_expression: 手动传入条件关系，默认关系为 and
        :param page_index: 第几页
        :param page_size: 每页条数
        :param count: 总条数
        :param kwargs: 传入的查询条件
        """
        prop = ','.join([str(i) for i in prop_list]) if isinstance(prop_list, list) else prop_list or '*'

        sql = f"select {prop} from {table}"
        count_sql = f"select count(*) from {table}"

        query_list = list()

        for key, value in kwargs.items():
            try:
                key, symbol = key.rsplit('__', 1)
                assert symbol in symbol_map, '查询操作错误！正确操作包含：%s，您的操作：%s' % (str([i for i in symbol_map]), symbol)
            except ValueError:
                symbol = '='

            if symbol == 'in':
                assert isinstance(value, tuple), '查询格式错误！正确示例：a__in=(1, 3, 4, 5)'
                assert len(value) != 0, '使用in时元组不能为空'

            elif symbol == 'between':
                assert isinstance(value, list) and len(value) != 2, '查询格式错误！正确示例：a__between=[1, 3]'
                value = ' and '.join([str(i) for i in value])

            query_list.append(f"{key} {symbol} {value}")

        if default_expression:
            expression_list = re.split('\d', default_expression)[1:-1]
            for index, value in enumerate(query_list):
                expression_list.insert(0 + index * 2, value)

            sql += ' where ' + ' '.join(expression_list)
            count_sql += ' where ' + ' '.join(expression_list)
        else:
            sql += ' where ' + ' and '.join(query_list)
            count_sql += ' where ' + ' and '.join(query_list)

        if count:
            sql += ' limit ' + ','.join([str(0), str(count)])
        elif page_size:
            sql += ' limit ' + ','.join([str((page_index - 1) * page_size), str(page_size)])

        total = self.exec_for_sql(count_sql)[0]['count(*)']
        logging.debug('exec sql: %s' % sql)

        return total, self.exec_for_sql(sql)
