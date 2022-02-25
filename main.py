# -*- coding: utf_8 -*-
# @Create   : 2021/5/27 11:37
# @Author   : yh
# @Remark   : 主入口文件
import json
import sys
import typing as t

from pydantic import ValidationError

from .HTTPMethod import send_response
from .base import BaseMx
from .exception import NotFoundError, MxBaseException
from .view import Request, Response

if t.TYPE_CHECKING:
    from .module import Module

session_handler: Request  # session处理类，用于globals文件中全局导入request
_server_config: object  # 全集配置


class Mx(BaseMx):
    """
    app对象类
    """

    def __init__(self, **options: t.Any):
        super().__init__(**options)

        self.module_list = []  # 所有模块列表
        self.after_request_funcs = list()
        self.before_request_funcs = list()

    def before_request(self, f):
        self.before_request_funcs.append(f)
        return f

    def after_request(self, f):
        self.after_request_funcs.append(f)
        return f

    def register_module(self, module: "Module", **options: t.Any) -> None:
        """
        注册模块
        """
        self.module_list.append(module)
        for k, v in module.url_map.items():
            self.url_map[k] = v

    def full_dispatch_request(self, session):
        """
        处理请求
        """
        self.session_handler = Request(session)
        self.session_handler.module_list = self.module_list

        global session_handler
        session_handler = self.session_handler

        try:
            rv = self.preprocess_request()
            if rv is None:
                rv = self.run_func()

        except Exception as e:
            rv = self.handle_user_exception(e)

        response = self.process_response(rv)
        send_response(response)

    def preprocess_request(self):
        """
        处理before request列表
        """
        for before_func in self.before_request_funcs:
            rv = before_func(self.session_handler)
            if rv is not None:
                return rv
        return None

    def process_response(self, response: Response) -> Response:
        """
        处理after request列表
        :param response: 响应
        """
        for after_func in self.after_request_funcs:
            response = after_func(response)

        return response

    def run_func(self) -> Response:
        """
        运行url对应的函数、异常处理
        """
        func = self.get_func()

        if func:
            rv = func(self.session_handler)
            return rv[0] if isinstance(rv[0], Response) else Response(*rv, type='default')
        else:
            raise NotFoundError(self.session_handler.url)

    def get_func(self) -> t.Callable:
        """
        从url_map获取对应的函数
        :return:
        """

        url = self.session_handler.url
        if url is None:
            url = ''
        url = '/' + url if not url.startswith('/') else url
        return self.url_map.get(url)

    def handle_user_exception(self, e):
        """
        全局异常处理
        :param e: 获取到到异常
        """
        if isinstance(e, MxBaseException):
            return self.mx_base_exception_handler()
        elif isinstance(e, ValidationError):
            return self.validation_error_handler()
        else:
            raise e

    def mx_base_exception_handler(self) -> Response:
        """
        对捕获到的MxBaseException进行处理
        """
        error_type, error_value, error_traceback = sys.exc_info()

        error = error_type(error_value)
        self.session_handler.session.GetHttpResponseHead().SetStatus(error.state_code)

        return Response('%s(%s)' % (
            self.session_handler.callback, str(error_value)) if self.session_handler.callback else str(
            error_value), self.session_handler)

    def validation_error_handler(self) -> Response:
        """
        对捕获到的ValidationError进行处理
        """
        error_type, error_value, error_traceback = sys.exc_info()

        error = json.dumps({'status': 'failed',
                            'errmsg': str([{' -> '.join(str(e) for e in error['loc']): error['msg']}
                                           for error in error_value.errors()]),
                            'err_type': error_value.model.__name__ + ': 模型字段验证错误'},
                           ensure_ascii=False)

        return Response('%s(%s)' % (self.session_handler.callback, error) if self.session_handler.callback else error,
                        self.session_handler)

    class __ServerConfig:
        """
        读取配置
        """

        def __init__(self, config_path):
            from configparser import ConfigParser
            from os.path import basename, isfile
            for config in config_path:
                print(config)

                if not isfile(config):
                    continue
                conf = ConfigParser()
                try:
                    conf.read(config, encoding='gbk')
                except UnicodeDecodeError:
                    try:
                        conf.read(config, encoding='utf-8')
                    except UnicodeDecodeError:
                        conf.read(config, encoding='gb2312')
                conf_name = basename(config).split(".")[0]
                if hasattr(self, conf_name):
                    conf_name = conf_name + "_1"
                self.__setattr__(conf_name, self.__new_cls(conf_name, conf))

        def __new_cls(self, conf_name, conf):
            type_attr = {}
            for k, v in conf.items():

                if not isinstance(v, str):
                    v = self.__new_cls(k, v)
                type_attr[k] = v

            return type(conf_name, (), type_attr)

    def server_config(self, config_path: list):
        global _server_config

        _server_config = self.__ServerConfig(config_path)

    def __call__(self, session):
        """
        处理请求
        将所有处理放在其它方法中，方便他人进行中间件重写
        """

        self.full_dispatch_request(session)
