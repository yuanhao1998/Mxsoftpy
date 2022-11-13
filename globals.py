# -*- coding: UTF-8 -*-
# @Create   : 2021/10/28 15:18
# @Author   : yh
# @Remark   : 全局变量
import typing

if typing.TYPE_CHECKING:
    from .view import Request


def request() -> "Request":
    """
    session处理实例
    """
    from .main import request_context
    return request_context.get()


def config():
    """
    全局配置
    """
    from .load import _server_config
    return _server_config
