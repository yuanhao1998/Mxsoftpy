# -*- coding: UTF-8 -*-
# @Create   : 2021/5/17 9:47
# @Author   : yh
# @Remark   : 在此编写所有自定义异常类
import json

from .db_def.db_error import error_dict
from db_def.def_http_code import HttpCode


class MxBaseException(Exception):
    """
    异常基类
    """
    state_code = HttpCode.st_200_ok  # 默认响应码

    def __init__(self, msg: str = None) -> None:
        """
        :param msg: 错误提示信息
        """
        super().__init__()
        self.msg = msg


class CError(MxBaseException):
    """
    c++方法调用异常
    """

    def __str__(self):
        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': 'c++方法调用异常'}, ensure_ascii=False)


class ModelCheckError(MxBaseException):
    """
    model层字段验证异常
    """

    def __str__(self):
        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '模型字段验证错误'}, ensure_ascii=False)


class ParamsError(MxBaseException):
    """
    参数异常
    """

    def __str__(self):
        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '参数错误'}, ensure_ascii=False)


class DBError(MxBaseException):
    """
    数据库调用异常
    """

    def __init__(self, err_code: int, msg: str = None):
        """
        :param err_code: 数据库错误码
        :param msg: 错误提示信息
        """
        super().__init__()
        self.err_code = err_code  # 数据库错误码
        self.msg = msg

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg,
                           'err_type': '数据库错误，错误码: %s, 错误原因: %s' % (self.err_code, error_dict.get(self.err_code))},
                          ensure_ascii=False)


class DataError(MxBaseException):
    """
    数据异常：通常为数据不符合要求
    """

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '数据错误'}, ensure_ascii=False)


class NotFoundError(MxBaseException):
    """
    url路径未找到
    """
    state_code = HttpCode.st_404_not_found

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '未知的url请求'}, ensure_ascii=False)


class HTTPMethodError(MxBaseException):
    """
    请求方式异常
    """

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '错误的请求方法'}, ensure_ascii=False)


class RPCConnError(MxBaseException):
    """
    云智慧RPC连接异常
    """

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '云智慧RPC连接异常'}, ensure_ascii=False)


class FileError(MxBaseException):
    """
    文件异常
    """

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '文件错误'}, ensure_ascii=False)


class AuthError(MxBaseException):
    """
    权限异常
    """

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': '权限错误'}, ensure_ascii=False)


class LicenseError(MxBaseException):
    """
    license异常
    """

    def __str__(self):

        return json.dumps({'status': 'failed', 'errmsg': self.msg, 'err_type': 'license异常'}, ensure_ascii=False)
