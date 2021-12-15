# -*- coding: utf_8 -*-
# @Create   : 2021/5/27 11:37
# @Author   : yh
# @Remark   : 主入口文件
import json
import sys
import typing as t
from itertools import chain

from pydantic import ValidationError

from .HTTPMethod import send_response
from .base import BaseMx
from .exception import NotFoundError, CError, MxBaseException
from .view import Request, Response

if t.TYPE_CHECKING:
    from .module import Module

session_handler: Request   # session处理类


class Mx(BaseMx):
    """
    app对象类
    """

    def __init__(self, **options: t.Any):
        super().__init__(**options)
        self.after_request_funcs = dict()
        self.before_request_funcs = dict()

    def before_request(self, f):
        self.before_request_funcs.setdefault(None, []).append(f)
        return f

    def after_request(self, f):
        self.after_request_funcs.setdefault(None, []).append(f)
        return f

    @staticmethod
    def set_response(request: "Request") -> "Request":
        """
        添加响应信息
        """
        try:
            request.response_headers_cls.SetStatus(request.status_code)
        except TypeError:
            raise CError('session.GetHttpResponseHead().SetStatus()')
        try:
            request.response_headers_cls.SetContentType(request.response_content_type)
        except TypeError:
            raise CError('session.GetHttpResponseHead().SetContentType()')
        return request

    @staticmethod
    def package_data(data: t.Any, callback: str) -> json:
        """
        打包响应数据
        :param data: 视图返回的数据
        :param callback: 回调标识
        :return: 打包后的数据
        """
        if isinstance(data, tuple):
            data = json.dumps({'status': 'success', 'errmsg': data[0], 'data': data[1] if len(data) == 2 else data[1:]},
                              ensure_ascii=False)
        else:
            data = json.dumps({'status': 'failed', 'errmsg': data, 'err_type': ''}, ensure_ascii=False)

        if callback:
            data = '%s(%s)' % (callback, data)

        return data

    def response_handle(self, request: "Request", res: t.Any) -> tuple:
        """
        响应处理
        :param res: 视图返回的数据
        :param request: 请求类
        :return:
        """
        request = self.set_response(request)
        if isinstance(res, Response):
            res = res()
        else:
            res = self.package_data(res, request.callback)
        return request.session, res

    def register_module(self, module: "Module", **options: t.Any) -> None:
        """
        注册模块
        """
        for k, v in module.url_map.items():
            self.url_map[k] = v

    def get_func(self, session) -> t.Callable:
        """
        从url_map获取对应的函数
        :return:
        """
        self.session_handler = Request(session)

        global session_handler
        session_handler = self.session_handler
        
        url = self.session_handler.url
        if url is None:
            url = ''
        url = '/' + url if not url.startswith('/') else url
        return self.url_map.get(url)

    def mx_base_exception_handler(self) -> None:
        """
        对捕获到的MxBaseException进行处理
        """
        error_type, error_value, error_traceback = sys.exc_info()
        self.session_handler = self.set_response(self.session_handler)

        error = error_type(error_value)
        self.session_handler.session.GetHttpResponseHead().SetStatus(error.state_code)

        send_response(self.session_handler.session, '%s(%s)' % (
            self.session_handler.callback, str(error_value)) if self.session_handler.callback else str(
            error_value))

    def validation_error_handler(self):
        """
        对捕获到的ValidationError进行处理
        """
        error_type, error_value, error_traceback = sys.exc_info()
        self.session_handler = self.set_response(self.session_handler)

        error = json.dumps({'status': 'failed',
                            'errmsg': str([{' -> '.join(str(e) for e in error['loc']): error['msg']}
                                           for error in error_value.errors()]),
                            'err_type': error_value.model.__name__ + ': 模型字段验证错误'},
                           ensure_ascii=False)

        send_response(self.session_handler.session,
                      '%s(%s)' % (self.session_handler.callback, error) if self.session_handler.callback else error)

    def run_func(self, session) -> None:
        """
        运行url对应的函数、异常处理
        """
        func = self.get_func(session)

        # funcs = self.before_request_funcs.get(None, ())
        # funcs = chain(funcs, self.before_request_funcs[])
        #
        # for func in funcs:
        #     func(self.session_handler)

        if func:
            try:
                resp_cls, res = func(self.session_handler)
                send_response(*self.response_handle(resp_cls, res))
            except MxBaseException:
                self.mx_base_exception_handler()
            except ValidationError:
                self.validation_error_handler()

        else:
            raise NotFoundError(self.url_map)

    def __call__(self, session):
        """
        处理请求
        将所有处理放在其它方法中，方便他人进行中间件重写
        """
        self.run_func(session)
