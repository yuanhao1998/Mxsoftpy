# -*- coding: utf_8 -*-
# @Author : yh
# @Time : 2020/11/5 16:18
# @Remark: 存放Tree db数据库的操作方法，详情见TreeModel使用手册
import logging
from typing import List, Any, Union

from superbsapi import *

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
    'in': TRDB_FMC_RANGE,  # 范围查找（枚举）
    'between': TRDB_FMC_RANGE  # 范围查找（范围）
    # 其他的类型，以后用到了再添加
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

    def open(self, main_key: str, sub_key: str = None, host: str = None, file: str = 'base',
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
        host = host or self.host
        port = port or self.port

        if not flag:
            if sub_key:
                flag = TRDB_OPKF_OPENEXIST if '\\' in sub_key else TRDB_OPKF_DOTPATH
            else:
                flag = TRDB_OPKF_OPENEXIST if '\\' in main_key else TRDB_OPKF_DOTPATH

        if sub_key:
            try:
                self.exec_tree('Treedb_ReopenMainKey', sub_key, flag, path_flag, main_key, main_key_pwd, file)
            except DBError:
                try:
                    logging.warning('正在重新连接数据库并打开主键[%s]-子键[%s]' % (main_key, sub_key))
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
                        logging.warning('正在重新连接数据库并打开主键[%s]' % main_key)
                        self.__chl = CBSHandleLoc()
                        self.exec_tree('Treedb_Alloc', host, file, main_key, main_key_pwd, TRDB_OPKF_OPENEXIST, port)
                    except DBError as e:
                        raise DBError(e.err_code, '打开主键[%s]时' % main_key)
        return self

    def main_keys(self, host: str = None, file: str = 'base', port: int = None) -> list:
        """
        获取所有主键
        eg: sub_keys = db.open('MXSE', '1.SD', file='ccubase').main_keys()

        :param host: 主机名
        :param file: 数据库名
        :param port: 端口号
        :return: 主键列表
        """
        host = host or self.host
        port = port or self.port

        res_list = list()
        self.exec_tree('Treedb_GetAllMainKeyNames', res_list, host, file, port)
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

    def insert_main_key(self, main_key: str, host: str, file: str,  main_pwd: str = '', port: int = 0):
        """
        插入主键
        eg: db.insert_main_key('test', host='127.0.0.1', file='IOT')

        :param main_key: 主键名
        :param file: 文件名
        :param host: 主机ip
        :param main_pwd: 主键密码
        :param port:
        """
        return self.exec_class('Treedb_CreateMainKey', host, file, main_key, main_pwd, port)

    def insert_sub_keys(self, sub_keys: Union[str, list], flag: int = TDDB_OPKF_CREATEDYNKEY) -> None:
        """
        批量插入子键
        eg: db.open('MXSE', '1.SD', file='ccubase').insert_sub_keys(['test1', 'test2'])

        :param sub_keys: 子键列表
        :param flag: 打开风格
        """
        if isinstance(sub_keys, str):
            sub_keys = [sub_keys]
        for sub_key in sub_keys:
            self.exec_tree('Treedb_InsertSubKey', sub_key, flag)

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

    def insert_items(self, items: List[tuple], overwrite=True) -> int:
        """
        批量插入数据
        eg: db.open('MXSE', '1.SD', file='ccubase').insert_items([('mxlabel', 'test'), ('mxid', 123)])

        :param items: 插入的数据
        :param overwrite: 是否覆盖原值
        """
        if not isinstance(items, list):
            raise DataError('错误的数据类型，items应为列表')
        data_list = list()
        for item in items:
            data_list.append({'name': item[0], 'value': item[1], 'valuetype': self._check_item(item)})

        return self.exec_bs('bs_treedb_insert_propertys', data_list, overwrite)

    def insert_key_items(self, items: List[tuple], key: str = None) -> str:
        """
        批量插入子键及k,v
        eg: db.open('MXSE', '1.SD', file='ccubase').insert_key_items(
                                                    items=[('mxlabel', 'test'), ('mxid', 123)], key='key1')

        :param items: 插入的数据, 如果元组传入三个元素，将第三个元素当作数据类型（见文首type_map），如果只传入两个，则自动获取数据类型
        :param key: 子键名称,不传自动生成
        :return: 生成的子键
        """
        if isinstance(items, tuple):
            items = [items]
        if not isinstance(items, list):
            raise DataError('错误的数据类型，items应为列表')
        items_list = list()
        for item in items:
            items_list.append({'name': item[0], 'value': item[1], 'valuetype': self._check_item(item)})
        return self.exec_bs('bs_treedb_insert_key_and_properties', key or '', TRDB_OPKF_OPENEXIST, items_list,
                            True)

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

    def filter(self, **kwargs) -> tuple:
        """
        根据属性筛选符合条件的子键（可分页显示）

        :param kwargs: 传入的查询条件
                        page_size：每页条数
                        page_index：第几页
                        order_by：排序字段
                        is_desc：是否反序
                        default_expression：手动传入条件关系，默认关系为 and
        :return: 总条数，查询结果
        """

        try:
            page_size = kwargs.pop('page_size')
            assert page_size, '未获取到数据！'
        except (KeyError, AssertionError):
            page_size = 0
        try:
            page_index = kwargs.pop('page_index')
            assert page_index, '未获取到数据！'
        except (KeyError, AssertionError):
            page_index = 1
        try:
            order_by = kwargs.pop('order_by')
            assert order_by, '未获取到数据！'
        except (KeyError, AssertionError):
            order_by = ''
        try:
            is_desc = kwargs.pop('is_desc')
        except KeyError:
            is_desc = False
        try:
            default_expression = kwargs.pop('default_expression')
            assert default_expression, '未获取到数据！'
        except (KeyError, AssertionError):
            default_expression = None
        args, range_conditions = list(), dict()

        i = 0
        expression_list = list()

        for key, value in kwargs.items():
            try:
                key, symbol = key.rsplit('__', 1)
                if symbol not in symbol_map:
                    raise DataError('查询操作错误！正确操作包含：gt、lt等')
            except ValueError:
                symbol = 'e'

            temp = {'key': key, 'value_type': type(value).__name__, 'symbol': symbol, 'value': value}

            if symbol == 'in':
                j = 0
                if not isinstance(value, list):
                    raise DataError('查询格式错误！正确示例：a__in=[1, 3, 4, 5]')
                if len(value) == 0:
                    raise DataError('使用in时列表不能为空')
                for v in value:
                    temp = {'key': key, 'value_type': type(v).__name__, 'symbol': 'e', 'value': v}
                    args.append(temp)
                    if j == 0:
                        expression_temp = '(%s' % i
                    else:
                        expression_temp += ' or ' + str(i)
                    i += 1
                    j += 1
                expression_temp += ')'
                expression_list.append(expression_temp)
            elif symbol == 'between':
                if not isinstance(value, list) or len(value) not in [2, 3]:
                    raise DataError('查询格式错误！正确示例：a__between=[1, 3]，详情见TreeModel使用手册')
                temp['range_conditions'] = {'vLiData': value[0], 'vEnd': value[1]}
                temp['value_type'] = value[2] if len(value) == 3 else type(value[0]).__name__
                expression_list.append(' %s ' % i)
                args.append(temp)
                i += 1
            else:
                expression_list.append(' %s ' % i)
                args.append(temp)
                i += 1

        default_query_conditions = list()
        for arg in args:
            if arg['symbol'] not in symbol_map:
                raise DataError('查询操作错误！正确操作包含：gt、lt等，详情见TreeModel使用手册')
            if arg['value_type'] not in type_map:
                raise DataError('查询数据类型！正确操作包含：str、int等，详情见TreeModel使用手册')
            data = {'name': arg['key'], 'nCondition': symbol_map[arg['symbol']], 'vLiData': arg['value'],
                    'vLiDataType': type_map[arg['value_type']]}
            if arg.get('range_conditions'):
                data.update(arg['range_conditions'])
            default_query_conditions.append(data)

        res_list = list()
        res = self.exec_bs('bs_treedb_query_subkey_by_condition_ex', default_query_conditions,
                           default_expression if default_expression else ' and '.join(expression_list),
                           res_list, page_size, (page_index - 1) * page_size, order_by, is_desc)

        return res, res_list
