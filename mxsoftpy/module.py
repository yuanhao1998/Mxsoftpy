# -*- coding: UTF-8 -*-
# @Create   : 2021/5/27 14:17
# @Author   : yh
# @Remark   : 模块类
import typing as t

from mxsoftpy.base import BaseMx


class Module(BaseMx):

    def __init__(self, name, url_prefix: str = None, **options: t.Any) -> None:
        super().__init__()
        self.name = name
        self.url_prefix = url_prefix

    def add_url_rule(self, url: str, func: t.Callable, **options: t.Any) -> None:
        """
        重写添加路由方法，在路由中加入url_prefix
        """
        self.url_map[(self.url_prefix or '') + url] = func
