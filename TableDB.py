# -*- coding: UTF-8 -*-
# @Create   : 2021/9/13 9:12
# @Author   : yh
# @Remark   : 存放Table db数据库的操作方法
import datetime
import re
from typing import Type, List, Any, Union

from superbsapi import CBSHandleLoc

from . import Model
from .BaseDB import BaseDB
from .db_def.def_table import TBDB_DT_RS
from .db_def.def_type import type_map, type_c_python, type_c_str
from .exception import DBError, DataError

sql_symbol_map = {
    'e': '=',  # 等于
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

    def __init__(self, host=None, port=None):
        super().__init__(host, port)
        self.__table = None

    def open(self, file: str = None, table: str = None, host: str = None, port: int = None):
        """
        打开table数据库
        :param file: 数据库名称
        :param table: 数据库表名
        :param host: 主机ip
        :param port: 端口
        """

        file = file or self._get_file()

        try:
            self.exec_tree('Tabledb_ReopenDb', file)
        except DBError:
            try:
                _host, _port = self._get_table_host_port(table)
                self.__chl = CBSHandleLoc()
                self.exec_tree('Tabledb_Alloc', host or _host, file, port or _port)
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

    def fields(self, table) -> dict:
        """
        获取表的所有字段及其属性
        :param table: 要获取字段类型的表名
        :return:
        """
        res = list()
        self.exec_bs('bs_tabledb_get_fields', table, res)
        return {i['name']: i for i in res}

    def create_table(self, table: str, model: Type[Model], flag, **kwargs) -> None:
        """
        新建表
        :param table: 要创建的数据库名称
        :param model: 要创建的表，如果您不显式的声明字段长度，则默认长度为200
        :param flag: 创建风格
        :param kwargs: 附加参数
        """

        field_list = list()
        for field in model.__fields__.values():
            if not type_map.get(field.type_.__name__):
                raise DataError(
                    '不支持此解析字段的类型，字段名: %s, 解析到的类型: %s' % (field.name, field.type_.__name__))
            temp = {"name": field.name, "uType": type_map[field.type_.__name__], 'uFlag': 0,
                               "uDataLen": field.type_.max_length if hasattr(field.type_, 'max_length') else 0}
            if kwargs.get(field.name):
                if isinstance(kwargs[field.name], dict):
                    temp.update(kwargs[field.name])
                elif isinstance(kwargs[field.name], list):
                    for i in kwargs[field.name]:
                        temp.update(i)

            field_list.append(temp)

        self.exec_bs('bs_tabledb_create_table', table, field_list, flag)

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

    class __TimeDelta(object):
        def __init__(self, **kwargs):
            self._query = dict()
            for k, v in kwargs.items():
                if k in ['days', 'seconds', 'microseconds', 'milliseconds', 'minutes', 'hours', 'weeks'] and isinstance(
                        v, (float, int)):
                    self._query[k] = v

        def res(self):
            return self._query

    def record_by_time(self, table_name: str = None, start_time: int = None, end_time: int = None, count=0,
                       **kwargs) -> list:
        """
        根据时间获取记录
        :param table_name: 要获取的表名
        :param start_time: 开始时间戳
        :param end_time: 结束时间戳
        :param count: 要获取的条数，为0则获取所有
        :param kwargs: 时间参数 ['days', 'seconds', 'microseconds', 'milliseconds', 'minutes', 'hours', 'weeks']
        :return:
        """
        self.__table = table_name or self.__table
        res = list()
        if not self.__table:
            raise DataError('找不到table，请打开或传入表')
        if start_time is None and end_time is None:
            now = datetime.datetime.now()
            end_time = int(now.timestamp())
            start_time = int((now - datetime.timedelta(**self.__TimeDelta(**kwargs).res())).timestamp())
        elif start_time is not None and end_time is None:
            end_time = int((datetime.datetime.fromtimestamp(start_time) + datetime.timedelta(
                **self.__TimeDelta(**kwargs).res())).timestamp())
        elif start_time is None and end_time is not None:
            start_time = int((datetime.datetime.fromtimestamp(end_time) - datetime.timedelta(
                **self.__TimeDelta(**kwargs).res())).timestamp())

        self.exec_tree('Tabledb_SelectRecordsByCTime', self.__table, count, start_time, end_time, res)
        return res

    def last_data(self, table_name: str = None) -> dict:
        """
        获取最新的一条数据
        """
        self.__table = table_name or self.__table
        res1, res2 = dict(), dict()
        try:
            self.exec_bs('bs_tabledb_get_dyn_and_lastrd', self.__table, res1, res2)
        except DBError as e:
            if e.err_code in [288, 1012]:
                return {}
            else:
                raise e
        return res2

    def exec_for_sql(self, sql: str) -> List[dict]:
        """
        根据sql查询数据
        :param sql: 查询sql
        """
        res_list = []
        try:
            self.exec_tree('Tabledb_Query', sql, res_list)
        except DBError as e:
            if e.err_code == 288:  # 错误码288意思是表为空，不应该报错
                pass
            else:
                raise e

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

    def delete_table(self, table_name: str = None, flag=TBDB_DT_RS):
        """
        删除table表
        :param table_name: table名称
        :param flag: 删除模式
        :return:
        """
        if not table_name and self.__table:
            raise DBError(1, '未指定要删除的table')
        return self.exec_bs('bs_tabledb_delete_table', table_name or self.__table, flag)

    def filter(self, table: str = None, prop_list: Union[str, list] = None, page_size=0, page_index=1, is_desc=False,
               default_expression=None, count: int = None, **kwargs) -> tuple:
        """
        table表筛选
        :param prop_list: 筛选需查询的字段，不传查所有
        :param table: 数据库表，不传默认使用open传入的table
        :param default_expression: 手动传入条件关系，默认关系为 and
        :param page_index: 第几页
        :param page_size: 每页条数
        :param is_desc: 是否反序  <！！！ 注意：数据库暂时不支持，此次仅暂时预留 ！！！>
        :param count: 总条数
        :param kwargs: 传入的查询条件
        """
        prop = ','.join([str(i) for i in prop_list]) if isinstance(prop_list, list) else prop_list or '*'

        sql = f"select {prop} from {table or self.__table}"
        count_sql = f"select count(*) from {table or self.__table}"

        query_list = list()

        for key, value in kwargs.items():
            try:
                key, symbol = key.rsplit('__', 1)
                assert symbol in sql_symbol_map, '查询操作错误！正确操作包含：%s，您的操作：%s' % (
                str([i for i in sql_symbol_map]), symbol)
            except ValueError:
                symbol = 'e'

            if symbol == 'in':
                value = tuple(value) if isinstance(value, list) else value
                assert isinstance(value, tuple), '查询格式错误！正确示例：a__in=(1, 3, 4, 5)'
                assert len(value) != 0, '使用in时元组不能为空'

            elif symbol == 'between':
                assert isinstance(value, list) and len(value) == 2, '查询格式错误！正确示例：a__between=[1, 3]'
                value = ' and '.join([str(i if type(i).__name__ != 'str' else '\'' + i + '\'') for i in value])

            # query_list.append(
            #     "%s %s %s" % (
            #     key, sql_symbol_map[symbol], value))

            if sql_symbol_map[symbol] == 'between':
                value = value
                print(1)
            else:
                print(2)
                value = value if type(value).__name__ != 'str' else '\'' + value + '\''
            print(value)
            query_list.append(
                "%s %s %s" % (
                    key, sql_symbol_map[symbol], value))

        if default_expression:
            expression_list = re.split('\d', default_expression)[1:-1]
            for index, value in enumerate(query_list):
                expression_list.insert(0 + index * 2, value)

            sql += ' where ' + ' '.join(expression_list)
            count_sql += ' where ' + ' '.join(expression_list)
        else:
            sql += ' where ' + ' and '.join(query_list) if query_list else ''
            count_sql += ' where ' + ' and '.join(query_list) if query_list else ''

        if count and page_size:
            limit_num2 = count - (page_index - 1) * page_size if count < page_index * page_size else page_size
            if limit_num2 <= 0:  # 当要取的数据量 <= 0，直接返回空
                return 0, []
            else:
                sql += ' limit ' + ','.join([str(max(0, (page_index - 1) * page_size)), str(limit_num2)])
        elif count:
            sql += ' limit ' + ','.join([str(0), str(count)])
        elif page_size:
            sql += ' limit ' + ','.join([str((page_index - 1) * page_size), str(page_size)])

        try:
            total = self.exec_for_sql(count_sql)[0]['count(*)']
            data = self.exec_for_sql(sql)
        except DBError as e:
            if e.err_code in [288, 1012]:  # 错误码288、1012意思是表为空，不应该报错
                total, data = 0, []
            else:
                raise e

        return min(count, total) if count else total, data
