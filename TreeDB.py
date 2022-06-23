# -*- coding: UTF-8 -*-
# @Author : yh
# @Time : 2020/11/5 16:18
# @Remark: 存放Tree db数据库的操作方法，详情见TreeModel使用手册
from typing import List, Any, Union

from mxsoftpy import Model
from superbsapi import CBSHandleLoc

from .BaseDB import BaseDB
from .exception import DBError, DataError
from .db_def.def_type import *
from .db_def.def_tree import *

symbol_map = {
    'e': TRDB_FMC_EQUAL,  # 等于
    'ne': TRDB_FMC_UNEQUAL,  # 不等于
    'gt': TRDB_FMC_GREATERTHAN,  # 大于
    'lt': TRDB_FMC_LESSTHAN,  # 小于
    'gte': TRDB_FMC_EQUALORGREATERTHAN,  # 大于等于
    'lte': TRDB_FMC_EQUALORLESSTHAN,  # 小于等于

    'like': TRDB_FMC_LIKE,  # 模糊匹配，使用 * 做为通配符
    'nclike': TRDB_FMC_NOCASE_LIKE,  # 模糊匹配，不区分大小写
    'in': TRDB_FMC_IN,  # 范围查找（枚举）
    'between': TRDB_FMC_RANGE  # 范围查找（范围）
}


class TreeDB(BaseDB):

    def begin(self) -> int:
        """
        开启事务
        """
        return self.exec_tree('Treedb_BeginTransaction')

    def commit(self) -> int:
        """
        提交事务
        :return:
        """
        return self.exec_tree('Treedb_CommitTransaction')

    def rollback(self) -> int:
        """
        回滚事务
        """
        return self.exec_tree('Treedb_RollbackTransaction')

    def create_index(self, name, name_type, flag=0):
        """
        创建索引
        :param name: 要建立索引的字段名称
        :param name_type: 字段类型
        :param flag: 默认升序，设置BS_RITF_INDEX_DESC则为降序
        :return:
        """
        return self.exec_bs('bs_treedb_create_index', [{'name': name, 'uFlag': flag,
                                                        'uType': type_map.get(name_type) or name_type}])

    def delete_index(self):
        """
        删除索引
        :return:
        """

        # TODO 用到了再写吧
        # return self.exec_bs('bs_treedb_delete_index')

    def get_index_names(self):
        """
        查询索引名称
        :return: ["id","name"]
        """
        # 如果没有会报错 223
        index_list = []
        self.exec_bs('bs_treedb_get_index_names', index_list)
        return index_list

    def open(self, main_key: str, sub_key: str = None, host: str = None, file: str = None,
             main_key_pwd: str = '', flag: int = None, port: int = None, path_flag: bool = False) -> "TreeDB":
        """
        打开数据库键 [只打开主键或子键 / 同时打开主键和子键（子键路径）]
        eg: db = TreeModel()
            db.open('MXSE', '1.SD', file='ccubase', host='127.0.0.1')

        :param main_key: 主键名
        :param sub_key: 子键名
        :param host: 主机名
        :param file: 数据库名
        :param main_key_pwd: 主键密码
        :param flag: 打开风格
        :param port: 端口号
        :param path_flag: 如果路径上有子键不存在是否自动创建
        :return: 类对象
        """
        file = file or self._get_file()

        if not flag:
            if sub_key:
                flag = TRDB_OPKF_OPENEXIST if '\\' in sub_key else TRDB_OPKF_OPENEXIST | TRDB_OPKF_DOTPATH
            else:
                flag = TRDB_OPKF_OPENEXIST if '\\' in main_key else TRDB_OPKF_OPENEXIST | TRDB_OPKF_DOTPATH

        if sub_key:
            try:
                self.exec_tree('Treedb_ReopenMainKey', sub_key, flag, path_flag, main_key, main_key_pwd, file)
            except DBError:
                try:
                    _host, _port = self._get_host_port(main_key)
                    host, port = host or _host, port or _port
                    self.__chl = CBSHandleLoc()
                    self.exec_tree('Treedb_Alloc', host, file, main_key, main_key_pwd, TRDB_OPKF_OPENEXIST, port)
                    self.exec_tree('Treedb_ReopenSubKey', sub_key, flag)
                except DBError as e:
                    raise DBError(e.err_code, '打开主键[%s]-子键[%s]时' % (main_key, sub_key))
        else:
            try:
                self.exec_tree('Treedb_ReopenSubKey', main_key, flag)
            except DBError:
                try:
                    self.exec_tree('Treedb_ReopenMainKey', '', flag, path_flag, main_key, main_key_pwd, file)
                except DBError:
                    try:
                        _host, _port = self._get_host_port(main_key)
                        host, port = host or _host, port or _port
                        self.__chl = CBSHandleLoc()
                        self.exec_tree('Treedb_Alloc', host, file, main_key, main_key_pwd, TRDB_OPKF_OPENEXIST, port)
                    except DBError as e:
                        raise DBError(e.err_code, '打开主键[%s]时' % main_key)
        return self

    @classmethod
    def file_names(cls, host: str = None, port: int = None) -> list:
        """
        获取数据库所有数据库名
        eg: TreeDB.main_keys(host='127.0.0.1', port=8123)

        :param host: 主机
        :param port: 端口
        """
        host, port = cls._check_conn_params(cls, host, port)

        res_list = list()
        cls.exec_class('bs_tabledb_get_all_dbnames', res_list, host, port)
        return res_list

    @classmethod
    def main_keys(cls, file: str, host: str = None, port: int = None) -> list:
        """
        获取数据库下所有的主键
        eg: TreeDB.main_keys(file='master', host='127.0.0.1', port=8123)

        :param file: 数据库名
        :param host: 主机
        :param port: 端口
        """

        host, port = cls._check_conn_params(cls, host, port, file)

        res_list = list()
        cls.exec_class('Treedb_GetAllMainKeyNames', res_list, host, file, port)
        return res_list

    def sub_keys(self) -> list:
        """
        获取当前键下所有的子键名
        eg: sub_keys = db.open('MXSE', '1.SD', file='ccubase').sub_keys()

        :return: 子键列表
        """
        res_list = list()
        self.exec_tree('Treedb_GetAllSubKeys', res_list)
        return res_list

    def sub_items(self, key_list=None, prop_list=None) -> dict:
        """
        获取当前键下，指定子键，指定属性的 key-value键值对
        eg: sub_items = db.open('MXSE', '1.SD', file='ccubase').sub_items(
                                key_list=['1.SD.1', '1.SD.2'], prop_list='_target_ip')
        <<<!!! 当key_list为空的时候会获取全部，需要自行注意 !!!>>>

        :param key_list: 要获取的子键列表
        :param prop_list: 要获取的属性列表
        :return: 子键及其属性字典
        """
        res_dict = dict()
        if isinstance(key_list, str):
            key_list = [key_list]
        if isinstance(prop_list, str):
            prop_list = [prop_list]

        self.exec_bs('bs_treedb_get_subkey_properties', key_list or [], prop_list or [], res_dict)
        return res_dict

    def items(self, prop_list=None) -> dict:
        """
        获取当前键下、指定属性的 key-value键值对, prop_list为空会获取所有属性
        eg: items = db.open('MXSE', '1.SD', file='ccubase').items(['max', 'mx_updatedatatime'])

        :param prop_list: 要获取属性
        """
        prop_list = [prop_list] if isinstance(prop_list, str) else prop_list

        res_dict = dict()
        self.exec_bs('bs_treedb_get_properties', prop_list if prop_list else [], res_dict)
        return res_dict

    def props(self) -> list:
        """
        获取所有属性名
        eg: props = db.open('MXSE', '1.SD', file='ccubase').props()

        :return: 属性名列表
        """
        res_list = list()
        self.exec_tree('Treedb_GetAllPropertyNames', res_list)
        return res_list

    def fetchone_value(self, prop_name: str) -> Any:
        """
        获取一个属性的值
        eg: max = db.open('MXSE', '1.SD', file='ccubase').fetchone_value('max')

        :param prop_name: 要获取的属性名称
        :return: 属性值
        """
        return self.exec_tree('Treedb_GetProperty', prop_name)

    @classmethod
    def insert_file(cls, file_name: str, host: str = None, port: int = None) -> int:
        """
        插入数据库
        eg: TreeDB.insert_file('test', host='127.0.0.1', port=8123)

        :param file_name: 数据库名称
        :param host: 主机ip
        :param port: 端口
        """

        host, port = cls._check_conn_params(cls, host, port, file_name)
        return cls.exec_class('Treedb_CreateFile', host, file_name, port)

    @classmethod
    def insert_main_key(cls, main_key: str, file: str, main_pwd: str = '', host: str = None, port: int = None) -> int:
        """
        插入主键
        eg: db.insert_main_key('test', host='127.0.0.1', file='IOT')

        :param main_key: 主键名
        :param file: 文件名
        :param main_pwd: 主键密码
        :param host: 主机ip
        :param port: 端口
        """

        host, port = cls._check_conn_params(cls, host, port, file)
        return cls.exec_class('Treedb_CreateMainKey', host, file, main_key, main_pwd, port)

    def insert_sub_keys(self, sub_keys: Union[str, list] = '', flag: int = TDDB_OPKF_CREATEDYNKEY) -> Union[str, list]:
        """
        批量插入子键
        eg: db.open('MXSE', '1.SD', file='ccubase').insert_sub_keys(['test1', 'test2'])

        :param sub_keys: 子键列表
        :param flag: 打开风格
        """
        if isinstance(sub_keys, str):
            return self.exec_tree('Treedb_InsertSubKey', sub_keys, flag)
        else:
            res = []
            for sub_key in sub_keys:
                res.append(self.exec_tree('Treedb_InsertSubKey', sub_key, flag))
            return res

    def insert_item(self, prop: str, value: Any, value_type: str = None, overwrite: bool = True) -> int:
        """
        插入一条数据
        eg: db.open('MXSE', '1.SD', file='ccubase').insert_item('mxlabel', 'test')

        :param prop: 键
        :param value: 值
        :param value_type: 指定的数据类型，不传自动获取
        :param overwrite: 是否覆盖原值
        """
        value_type = type_map.get(value_type) or type_map.get(type(value).__name__)
        if not value_type:
            raise DataError('未知的value_type, 类型：%s ,值：%s' % (str(type(value)), value))
        return self.exec_bs('bs_treedb_insert_property', prop, value, value_type, overwrite)

    def insert_items(self, items: Union[List[tuple], dict, Model], overwrite=True) -> int:
        """
        批量插入数据
        eg: db.open('MXSE', '1.SD', file='ccubase').insert_items([('mxlabel', 'test'), ('mxid', 123)])
            db.open('MXSE', '1.SD', file='ccubase').insert_items({'mxlabel': 'test', 'mxid': 123})

        :param items: 插入的数据
        :param overwrite: 是否覆盖原值
        """

        return self.exec_bs('bs_treedb_insert_propertys', self._generation_items(items), overwrite) if items else 0

    def insert_key_items(self, items: Union[List[tuple], dict], key: str = None) -> str:
        """
        批量插入子键及k,v
        eg: db.open('MXSE', '1.SD', file='ccubase').insert_key_items(
                                                    items=[('mxlabel', 'test'), ('mxid', 123)], key='key1')
            db.open('MXSE', '1.SD', file='ccubase').insert_key_items(
                                                    items={'mxlabel': 'test', 'mxid': 123}, key='key1')

        :param items: 插入的数据, 如果元组传入三个元素，将第三个元素当作数据类型（见文首type_map），如果只传入两个，则自动获取数据类型
        :param key: 子键名称,不传自动生成
        :return: 生成的子键
        """

        return self.exec_bs('bs_treedb_insert_key_and_properties', key or '', TRDB_OPKF_OPENEXIST,
                            self._generation_items(items), True) if items else 0

    def delete(self, keys: Union[list, str, None] = None) -> None:
        """
        删除 单个子键/子键列表/自身
        eg: db.open('MXSE', '1.SD', file='ccubase').delete()

        :param keys: 要删除的子键。
        <<<!!! 值为空时会删除自身 !!!>>>
        <<<!!! 值为空时会删除自身 !!!>>>
        <<<!!! 值为空时会删除自身 !!!>>>
        """
        if isinstance(keys, list):
            for key in keys:
                self.exec_tree('Treedb_DeleteSubKey', key)
        elif isinstance(keys, str):
            self.exec_tree('Treedb_DeleteSubKey', keys)

        if keys is None:
            self.exec_bs('bs_treedb_delete_key')

    def delete_prop(self, prop: Union[str, None] = None) -> None:
        """
        删除一个属性、所有属性
        eg: db.open('MXSE', '1.SD', file='ccubase').delete_prop()

        :param prop: 要删除的属性名
        """
        if prop:
            self.exec_tree('Treedb_DeleteProperty', prop)
        else:
            self.exec_tree('Treedb_DeleteAllProperty')

    def rename(self, old_key: str, new_key: str) -> int:
        """
        重命名一个子键、自身
        eg: db.open('MXSE', '1.SD', file='ccubase').rename('1.SD.1', '1.SD.111')

        :param old_key: 要重命名的子键
        :param new_key: 新的名字
        （重命名自身的时候只需要传递新的名字）
        """
        if new_key:
            return self.exec_tree('Treedb_RenameSubKey', old_key, new_key)
        else:
            return self.exec_tree('Treedb_RenameThisKey', old_key)

    def rename_prop(self, old_prop: str, new_prop: str) -> int:
        """
        重命名一个属性
        eg: db.open('MXSE', '1.SD', file='ccubase').rename_prop('mxlabel', 'malabel-rename')

        :param old_prop: 要重命名的属性
        :param new_prop: 新的属性名
        """
        return self.exec_tree('Treedb_RenameProperty', old_prop, new_prop)

    @staticmethod
    def __generate_filter_data(kwargs: dict) -> tuple:
        """
        生成查询条件
        :param kwargs: 查询参数
        """
        args, expression_list, i = list(), list(), 0

        for key, value in kwargs.items():
            try:
                key, symbol = key.rsplit('__', 1)
                assert symbol in symbol_map, '查询操作错误！正确操作包含：%s，您的操作：%s' % (str([i for i in symbol_map]), symbol)
            except ValueError:
                symbol = 'e'

            temp = {'key': key, 'value_type': type(value).__name__, 'symbol': symbol, 'value': value}

            if symbol == 'in':
                assert isinstance(value, list), '查询格式错误！正确示例：a__in=[1, 3, 4, 5]'
                assert len(value) != 0, '使用in时列表不能为空'
                temp['vInValues'] = temp['value']
                temp['value_type'] = type(value[0]).__name__
                expression_list.append(' %s ' % i)
                args.append(temp)
                i += 1
            elif symbol == 'between':
                assert isinstance(value, list) and len(value) in [2, 3], '查询格式错误！正确示例：a__between=[1, 3]'
                temp['range_conditions'] = {'vLiData': value[0], 'vEnd': value[1]}
                temp['value_type'] = value[2] if len(value) == 3 else type(value[0]).__name__
                expression_list.append(' %s ' % i)
                args.append(temp)
                i += 1
            elif symbol == 'like':
                if isinstance(value, str):
                    expression_list.append(' %s ' % i)
                    if len(temp['value']) >= 2:
                        temp['value'] = temp['value'][0] + temp['value'][1:-1].replace('*', '\\*').replace('?', '\\?')\
                                        + temp['value'][-1]
                    args.append(temp)
                    i += 1
                elif isinstance(value, list):
                    assert len(value) != 0, '使用列表时不能为空列表'
                    j = 0
                    for v in value:
                        temp = {'key': key, 'value_type': type(v).__name__, 'symbol': 'like',
                                'value': (v[0] + v[1:-1].replace('*', '\\*').replace('?', '\\?') + v[-1])
                                if len(v) >= 2 else v}
                        args.append(temp)
                        if j == 0:
                            expression_temp = '(%s' % i
                        else:
                            expression_temp += ' or ' + str(i)
                        i += 1
                        j += 1
                    expression_temp += ')'
                    expression_list.append(expression_temp)
                else:
                    raise AssertionError('未知操作')
            else:
                expression_list.append(' %s ' % i)
                args.append(temp)
                i += 1

        default_query_conditions = list()
        for arg in args:
            assert arg['symbol'] in symbol_map, '查询操作错误！正确操作包含：%s，您的操作：%s' % (
                str([i for i in symbol_map]), arg['symbol'])
            assert arg['value_type'] in type_map, '查询数据类型！正确操作包含：%s，您的数据类型：%s' % (
                str([i for i in type_map]), arg['value_type'])
            data = {'name': arg['key'], 'nCondition': symbol_map[arg['symbol']], 'vLiData': arg['value'],
                    'vLiDataType': type_map[arg['value_type']]}

            if arg.get('range_conditions'):  # 判断是否有between
                data.update(arg['range_conditions'])
            if arg.get('vInValues'):  # 判断是否有in
                del data['vLiData']
                data.update({'vInValues': arg['vInValues']})

            default_query_conditions.append(data)

        return default_query_conditions, expression_list

    def filter_update(self, __prop__, __value__, __value_type__=None, default_expression=None, **kwargs):
        """
        根据属性筛选符合条件的子键、更新属性

        :param default_expression: 手动传入条件关系，默认关系为 and
        :param __prop__: 要修改的属性
        :param __value__: 更新的值
        :param __value_type__: 更新的值类型，不传会自动获取

        """
        default_query_conditions, expression_list = self.__generate_filter_data(kwargs)
        return self.exec_bs('bs_treedb_edit_property_by_condition', default_query_conditions,
                            default_expression or ' and '.join(expression_list),
                            __prop__, __value__, __value_type__ or type_map.get(type(__value__).__name__))

    def filter(self, page_size=0, page_index=1, order_by='', is_desc=False, default_expression=None, **kwargs) -> tuple:
        """
        根据属性筛选符合条件的子键（可分页显示）

        :param default_expression: 手动传入条件关系，默认关系为 and
        :param is_desc: 是否反序
        :param order_by: 排序字段
        :param page_index: 第几页
        :param page_size: 每页条数
        :param kwargs: 传入的查询条件
        :return: 总条数，查询结果
        """
        default_query_conditions, expression_list = self.__generate_filter_data(kwargs)

        res_list = list()
        res = self.exec_bs('bs_treedb_query_subkey_by_condition_ex', default_query_conditions,
                           default_expression or ' and '.join(expression_list),
                           res_list, page_size, (page_index - 1) * page_size, order_by, is_desc)

        return res, res_list
