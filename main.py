# -*- coding: utf_8 -*-
# @Create   : 2021/5/27 11:37
# @Author   : yh
# @Remark   : 主入口文件
import json
import sys
import typing as t

from pydantic import ValidationError
# from viztracer import VizTracer

from .HTTPMethod import send_response, add_response
from .base import BaseMx
from .def_http_code import hop_by_hop
from .exception import NotFoundError, MxBaseException
from .view import Request, Response, WSGIRequest

if t.TYPE_CHECKING:
    from .module import Module

session_handler: Request  # session处理类，用于globals文件中全局导入request


class Mx(BaseMx):
    """
    app对象类
    """

    def __init__(self, **options: t.Any):
        super().__init__(**options)

        self.module_list = []  # 所有模块列表
        self.after_request_funcs = list()  # 响应钩子
        self.before_request_funcs = list()  # 请求钩子

        from .load import load
        load()  # 初始化

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
        # a = VizTracer(log_func_args=True, log_func_retval=True, max_stack_depth=10)
        # a.start()
        try:
            rv = self.preprocess_request()
            if rv is None:
                rv = self.run_func()

        except Exception as e:
            rv = self.handle_user_exception(e)
        # a.stop()
        # a.save(r'\\Mac\Home\Desktop\result.json')

        response = self.process_response(rv)
        send_response(add_response(response))

    def full_dispatch_wsgi_request(self, environ, start_response):
        """
        处理wsgi服务器的请求
        :param environ: 请求信息
        :param start_response: 响应函数
        """
        self.session_handler = WSGIRequest(environ)

        global session_handler
        session_handler = self.session_handler

        try:
            rv = self.preprocess_request()
            if rv is None:
                rv = self.run_func()

        except Exception as e:
            rv = self.handle_wsgi_user_exception(e)

        response = self.process_response(rv)
        start_response(str(response.request.status_code),
                       [(k, v) for k, v in response.request.headers.items() if k not in hop_by_hop])
        return [bytes(response.data, encoding='utf-8')]

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

    def wsgi_mx_base_exception_handler(self) -> Response:
        """
        对捕获到的MxBaseException进行处理、适用于wsgi模式
        """
        error_type, error_value, error_traceback = sys.exc_info()

        error = error_type(error_value)
        self.session_handler.status_code = error.state_code

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

    def handle_wsgi_user_exception(self, e):
        """
        处理wsgi的异常
        :param e:
        :return:
        """
        if isinstance(e, MxBaseException):
            return self.wsgi_mx_base_exception_handler()
        elif isinstance(e, ValidationError):
            return self.validation_error_handler()
        else:
            raise e

    def __call__(self, environ=None, start_response=None, session=None):
        """
        处理请求
        将所有处理放在其它方法中，方便他人进行中间件重写
        """
        if environ and start_response:
            return self.full_dispatch_wsgi_request(environ, start_response)
        self.full_dispatch_request(session)
