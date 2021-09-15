# -*- coding: utf_8 -*-
# @Create   : 2021/9/13 9:24
# @Author   : yh
# @Remark   : 数据库操作方法基类，用于执行数据库方法及返回值校验
from typing import Union, Any

from .db_def.def_type import type_map
from .exception import DBError, DataError
from superbsapi import *

from .db_def.db_error import BS_NOERROR


class BaseDB:
    def __init__(self, host='127.0.0.1', port=8123) -> None:
        self.__chl = CBSHandleLoc()
        self.host = host
        self.port = port

    @staticmethod
    def return_value(res: tuple) -> Union[int, tuple, None]:
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

    def exec_tree(self, operate: str, *args: Any, **kwargs: Any) -> Union[int, tuple, None]:
        """
        用于执行Tree db开头的函数

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        func = getattr(self.__chl, operate)
        res = func(*args, **kwargs)
        return self.return_value(res)

    def exec_bs(self, operate: str, *args: Any, **kwargs: Any) -> Union[int, str, tuple, None]:
        """
        用于执行bs开头的函数

        :param operate: 使用的函数
        :param args kwargs: 函数所使用的变量
        :return: 执行结果
        """
        res = eval(operate)(self.__chl.GetConfHandle(), *args, **kwargs)
        return self.return_value(res)

    def exec_class(self, operator: str, *args, **kwargs):
        """
        用于执行类方法

        :param operator: 使用的函数
        :return: 执行结果
        """
        func = getattr(CBSHandleLoc, operator)
        res = func(*args, **kwargs)
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
