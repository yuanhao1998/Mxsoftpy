# -*- coding: UTF-8 -*-
# @Create   : 2021/5/27 14:36
# @Author   : yh
# @Remark   : 脚手架基类

import typing as t


class BaseMx:

    def __init__(self, **options: t.Any) -> None:
        self.url_map = dict()  # 路由字典
        self.session_handler = None

    def add_url_rule(self, url: str, func: t.Callable, **options: t.Any) -> None:
        """
        向url_map中添加路由对应关系
        :param url: url路径
        :param func: url路径对应的方法
        """
        self.url_map[url] = func

    def route(self, url: str, **options: t.Any) -> t.Callable:
        """
        添加路由装饰器
        :param url: url路径
        """
        def decorator(func):
            self.add_url_rule(url, func)
            return func

        return decorator

    def add_resource(self, resource: t.Callable, url: str, **options: t.Any) -> None:
        """
        绑定CBV视图
        :param resource: 视图名
        :param url: 要绑定的url路径
        """

        async def view(session):  # 接受此session参数，但是类方法中不需要使用，从session_handler中可获取到
            cls = resource(session)
            return await cls.dispatch_request()
        view.__name__ = resource.__name__
        view.__doc__ = getattr(resource, 'post', '').__doc__
        self.add_url_rule(url, view)
