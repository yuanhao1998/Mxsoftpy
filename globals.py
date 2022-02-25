# -*- coding: utf_8 -*-
# @Create   : 2021/10/28 15:18
# @Author   : yh
# @Remark   : 全局变量

def request():
    """
    session处理实例
    """
    from .main import session_handler
    return session_handler


def config():
    """
    全局配置
    @return: 
    """
    from .main import _server_config
    return _server_config
