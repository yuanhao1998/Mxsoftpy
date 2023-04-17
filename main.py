# -*- coding: UTF-8 -*-
# @Create   : 2021/5/27 11:37
# @Author   : yh
# @Remark   : 主入口文件
import datetime
import json
import subprocess
import sys
import os
import threading
import contextvars
import time
import traceback
import typing as t

from pydantic import ValidationError

from .base import BaseMx
from .exception import NotFoundError, MxBaseException
from .view import Request, Response

if t.TYPE_CHECKING:
    from .module import Module

request_context = contextvars.ContextVar('request')  # request上下文变量


class Mx(BaseMx):
    """
    app对象类
    """

    def __init__(self, **options: t.Any):
        super().__init__(**options)

        self.module_list = []  # 所有模块列表
        self.after_request_funcs = list()  # 响应钩子
        self.before_request_funcs = list()  # 请求钩子
        self.config = None  # 配置
        self.i18n = None  # 国际化

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

    async def full_dispatch_request(self, scope, receive, send):
        """
        处理asgi服务器的请求
        """
        self.session_handler = Request(scope, receive, send)
        self.session_handler.module_list = self.module_list
        self.session_handler.config = self.config
        if scope.get('type') == 'http' and self.session_handler.request_type.lower() == 'post':
            self.session_handler.POST_PROP = await self.session_handler.POST_ASYNC

        request_context.set(self.session_handler)

        try:
            rv = await self.preprocess_request()
            if rv is None:
                rv = await self.run_func()

        except Exception as e:
            rv = self.handle_user_exception(e)

        response = await self.process_response(rv)
        await send(
            {
                "type": "http.response.start",
                "status": response.request.status_code,
                "headers": [(k.encode(), v.encode()) for k, v in response.request.headers.items()],
            }
        )
        data = await response.data
        await send({"type": "http.response.body",
                    "body": bytes(data, encoding='utf-8') if not isinstance(data, bytes) else data})

    async def preprocess_request(self):
        """
        处理before request列表
        """
        for before_func in self.before_request_funcs:
            rv = before_func(self.session_handler)
            if rv is not None:
                return rv
        return None

    async def process_response(self, response: Response) -> Response:
        """
        处理after request列表
        :param response: 响应
        """

        # 没有content-type时，设置默认的content-type
        response.request.headers[
            'content-type'] = response.request.content_type or response.request.response_content_type
        for after_func in self.after_request_funcs:
            response = after_func(response)
        data = await response.data
        response.request.headers["content-length"] = str(
            len(bytes(data, encoding='utf-8') if not isinstance(data, bytes) else data))
        return response

    async def run_func(self) -> Response:
        """
        运行url对应的函数、异常处理
        """
        func = self.get_func()

        if func:
            rv = await func(self.session_handler)
            return rv if isinstance(rv, Response) else Response(rv, type='default')
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

    def mx_base_exception_handler(self) -> Response:
        """
        对捕获到的MxBaseException进行处理
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

    def unknown_error_handler(self) -> Response:
        """
        未知错误处理
        """
        error_value = "发生了一些问题"
        return Response('%s(%s)' % (
            self.session_handler.callback, str(error_value)) if self.session_handler.callback else str(
            error_value), self.session_handler, type="default")

    def handle_user_exception(self, e):
        """
        处理wsgi的异常
        """
        if isinstance(e, MxBaseException):
            return self.mx_base_exception_handler()
        elif isinstance(e, ValidationError):
            return self.validation_error_handler()
        else:
            log_path = os.path.join(__file__.split('Server')[0], "Server", 'middle', 'Pymod',
                                    datetime.date.today().strftime('%Y%m%d') + 'error.log')
            path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + '/middle/Pymod/'
            if not os.path.exists(path):
                os.makedirs(path)
            traceback.print_exc(file=open(log_path, 'a+'))
            raise e

    async def __call__(self, scope, receive, send):
        """
        处理请求
        将所有处理放在其它方法中，方便他人进行中间件重写
        """
        return await self.full_dispatch_request(scope, receive, send)

    @staticmethod
    def load_cache():
        from utils.middleware.cache import add_cache
        print('-------------python开始加载缓存-------------')
        add_cache()
        print('-------------python加载缓存结束-------------')

    def run(self, listen='*:7121', reload=False, **kwargs):
        """
        运行服务
        :param listen: 监听地址
        :param reload: 是否自动重载
        """
        from waitress import serve

        if reload:
            self.run_with_reloader(serve, listen=listen, **kwargs)
        else:
            self.load_cache()
            serve(self, listen=listen, **kwargs)

    def run_with_reloader(self, main_func, **kwargs):
        """
        自动重载实现
        """
        reloader = Reloader()
        if os.environ.get('WAITRESS_RUN_MAIN') == 'true':
            thread = threading.Thread(target=main_func, args=(self,), kwargs=kwargs)
            thread.setDaemon(True)
            thread.start()
            reloader.code_changed()
        else:
            self.load_cache()
            sys.exit(reloader.restart_with_reloader())


class Reloader:
    """
    自动重载实现类
    """

    def __init__(self):
        self._mtimes = {}

    @staticmethod
    def _get_args_for_reloading() -> t.List[str]:
        """
        获取重载参数 （python解释器路径、启动文件、参数等）
        """

        rv = [sys.executable]
        py_script = sys.argv[0]
        args = sys.argv[1:]
        __main__ = sys.modules["__main__"]

        if getattr(__main__, "__package__", None) is None or (
                os.name == "nt"
                and __main__.__package__ == ""
                and not os.path.exists(py_script)
                and os.path.exists(f"{py_script}.exe")
        ):
            py_script = os.path.abspath(py_script)

            if os.name == "nt":

                if not os.path.exists(py_script) and os.path.exists(f"{py_script}.exe"):
                    py_script += ".exe"

                if (
                        os.path.splitext(sys.executable)[1] == ".exe"
                        and os.path.splitext(py_script)[1] == ".exe"
                ):
                    rv.pop(0)

            rv.append(py_script)
        else:
            if sys.argv[0] == "-m":
                args = sys.argv
            else:
                if os.path.isfile(py_script):
                    py_module = t.cast(str, __main__.__package__)
                    name = os.path.splitext(os.path.basename(py_script))[0]

                    if name != "__main__":
                        py_module += f".{name}"
                else:
                    py_module = py_script

                rv.extend(("-m", py_module.lstrip(".")))

        rv.extend(args)
        return rv

    def restart_with_reloader(self):
        """
        重载调用
        """
        while True:
            new_environ = os.environ.copy()
            new_environ['WAITRESS_RUN_MAIN'] = 'true'
            exit_code = subprocess.call(self._get_args_for_reloading(), env=new_environ)
            if exit_code != 3:
                return exit_code

    def code_changed(self):
        """
        检测代码是否修改
        """
        while True:
            time.sleep(0.5)  # 每隔0.5秒检测一次、降低资源消耗。
            for module in list(sys.modules.values()):

                filename = getattr(module, '__file__', None)
                if not (filename and os.path.isfile(filename)):
                    continue

                if filename[-4:] in ('.pyc', '.pyo', '.pyd'):
                    filename = filename[:-1]

                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    continue

                old_time = self._mtimes.get(module)
                if old_time is None:
                    self._mtimes[module] = mtime
                elif old_time < mtime:
                    self._mtimes[module] = mtime
                    print('-------------监测到修改数据、自动重载---------------')
                    return sys.exit(3)
