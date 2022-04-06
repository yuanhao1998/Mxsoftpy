# -*- coding: utf_8 -*-
# @Create   : 2021/9/13 9:24
# @Author   : yh
# @Remark   : 数据库操作方法基类，用于执行数据库方法及返回值校验
from typing import Union, Any, List, Type

from superbsapi import *

from mxsoftpy import Model
from .db_def.db_error import BS_NOERROR
from .db_def.def_type import type_map
from .exception import DBError, DataError
from .globals import request


class BaseDB:

    port = None
    host = None

    def __init__(self, host=None, port=None) -> None:
        """
        初始化属性
        :param host: 主机
        :param port: 端口
        """
        self._chl = CBSHandleLoc()
        self._handle = None
        self.host, self.port = host, port
        self.__cls_value(self.host, self.port)

    @property
    def handle(self):
        """
        返回数据库操作句柄
        """
        return self._chl.GetConfHandle()

    @staticmethod
    def return_value(res: tuple) -> Union[int, str, tuple, None]:
        """
        用于直接返回结果集的函数，处理其返回值

        :param res: 错误信息及函数返回的数据
        :return: 返回信息
        """
        msg = res[0] if isinstance(res, tuple) else res
        if msg != BS_NOERROR:
            raise DBError(msg)
        if res:
            return res[1] if len(res) == 2 else res[1:]
        return None

    def exec_tree(self, operate: str, *args: Any, **kwargs: Any) -> Union[int, str, tuple, None]:
        """
        用于执行Tree开头的函数

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        func = getattr(self._chl, operate)
        res = func(*args, **kwargs)
        return self.return_value(res)

    def exec_bs(self, operate: str, *args: Any, **kwargs: Any) -> Union[int, str, tuple, None]:
        """
        用于执行bs开头的函数

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        res = eval(operate)(self._chl.GetConfHandle(), *args, **kwargs)
        return self.return_value(res)

    @classmethod
    def exec_class(cls, operate: str, *args, **kwargs):
        """
        用于执行类方法

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        func = getattr(CBSHandleLoc, operate)
        res = func(*args, **kwargs)
        return cls.return_value(res)

    def exec(self, operate: str, *args, **kwargs):
        """
        用于执行直接连接的函数（不在CBSHandleLoc类中的连接函数）

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        res, self._handle = eval(operate)(*args, **kwargs)
        return self.return_value(res)

    def exec2(self, operate: str, *args, **kwargs):
        """
        用于执行直接连接的函数（不在CBSHandleLoc类中且直接获取值的函数）

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        res = eval(operate)(*args, **kwargs)
        return self.return_value(res)

    def exec_handle(self, operate: str, *args, **kwargs):
        """
        用于使用上面连接所产生handle的函数

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        if self._handle:
            res = eval(operate)(self._handle, *args, **kwargs)
        else:
            raise DataError('找不到句柄，请先连接到数据库')
        return self.return_value(res)

    @staticmethod
    def _check_item(item: tuple) -> int:
        """
        校验item是否符合数据要求并返回value type
        """
        if not isinstance(item, tuple) or len(item) not in [2, 3]:
            raise DataError('错误的数据类型，items列表中的数据应为元组且长度为2或3')
        value_type = type_map.get(item[2]) if len(item) == 3 else type_map.get(
            type(item[1]).__name__)
        if not value_type:
            raise DataError('无法获取到value的类型！如果您未手动传入类型或确信传入类型正确，请于type_map中添加此类型')
        value_type = type_map[item[2]] if len(item) == 3 else type_map[type(item[1]).__name__]
        return value_type

    def _generation_items(self, items: Union[List[tuple], dict, Model]) -> list:
        """
        生成符合数据库插入格式的数据
        """
        data_list = list()
        if isinstance(items, list):
            for item in items:
                data_list.append({'name': item[0], 'value': item[1], 'valuetype': self._check_item(item)})
        elif isinstance(items, dict):
            for k, v in items.items():
                if type_map.get(type(v).__name__):
                    data_list.append({'name': k, 'value': v, 'valuetype': type_map[type(v).__name__]})
                else:
                    raise DataError('未知的value_type, 类型：%s ,值：%s' % (str(type(v)), v))
        elif isinstance(items, Model):
            for field in items.__fields__.values():
                if type_map.get(field.type_.__name__):
                    data_list.append({'name': field.name, 'value': getattr(items, field.name),
                                      'valuetype': type_map[field.type_.__name__]})
                else:
                    raise DataError('不支持此解析字段的类型，字段名: %s, 解析到的类型: %s' % (field.name, field.type_.__name__))

        else:
            raise DataError('生成符合数据库插入格式的数据时，传入错误的数据类型：%s，items应为items、dict或Model' % type(items).__name__)

        return data_list

    @classmethod
    def __cls_value(cls, host=None, port=None) -> None:
        """
        将实例属性添加到类属性
        :param host: 主机
        :param port: 端口
        """
        cls.host = host
        cls.port = port

    @staticmethod
    def _check_conn_params(cls: Type["BaseDB"], host, port, name=None) -> tuple:
        """
        获取并检查连接参数并返回
        :param cls: 类
        :param host: 主机ip
        :param port: 端口
        :param name: key名
        """
        if not host or not port:
            if not cls.host or not cls.port:
                _host, _port = cls._get_host_port2(name)
                host, port = host or cls.host or _host, port or cls.port or _port
            else:
                host, port = host or cls.host, port or cls.port

        return host, port

    @staticmethod
    def _get_file() -> str:
        """
        判断所使用的数据库，优先层次：
                                1：当前公司同名数据库
                                2：base
        """
        # noinspection PyBroadException
        try:
            return request().company
        except Exception:
            return 'Co_1'

    @staticmethod
    def _get_host_port2(key):
        # noinspection PyBroadException
        # try:
        #     from bsmiddle import DbServer_GetDataSource
        #     host, port = DbServer_GetDataSource(request().company, key.split('_', 1)[0])
        # except BaseException:
        try:
            from utils.conf.mxconfig import MxConfig
            host = MxConfig.HOST
            port = MxConfig.PORT
        except (ModuleNotFoundError, ImportError, AttributeError):
            host = '127.0.0.1'
            port = 8123
        return host, port

    def _get_host_port(self, key: str) -> tuple:

        if self.host and self.port:
            return self.host, self.port
        else:
            host, port = self._get_host_port2(key)
            return self.host or host, self.port or port
