# -*- coding: UTF-8 -*-
# @Create   : 2021/5/17 9:46
# @Author   : yh
# @Remark   : session处理类
import cgi
import functools
import json
import logging
import os
import random
import string
import typing as t
from asyncio import iscoroutinefunction
from io import BytesIO
from urllib.parse import parse_qs

import anyio

from .def_http_code import HttpCode
from .exception import HTTPMethodError, DataError, AuthError, FileError
from .globals import request, config
from .parse import scope_to_environ

# noinspection PyBroadException
try:
    NO_SESSION = int(config().middle.main.NoSession)
except Exception:
    NO_SESSION = 0


class SessionData:

    def __init__(self):
        self._session_id = None
        self._company = None
        self._user = None
        self._user_id = None
        self._user_group = None
        self._role = None
        self._role_filter = None
        self._is_admin = None

    @property
    def cookie(self) -> dict:
        raise NotImplementedError

    @property
    def session_id(self) -> str:
        """
        获取session id
        """
        if NO_SESSION:
            return self.cookie.get('mxsessionid', '')
        else:
            if not self.cookie.get('mxsessionid') and request().config.version == 0:
                raise AuthError('获取session失败，请重新登录')
            return self.cookie.get('mxsessionid', '')

    @property
    def company(self) -> str:
        """
        获取公司
        """
        if self._company:
            return self._company
        else:
            if NO_SESSION:
                return 'Co_1'
            else:
                if request().config.version == 0:
                    from py_opm_wm_bm import GetSessionCompany
                    flag, company = GetSessionCompany(self.session_id)
                    if flag == 0 or flag is True:
                        self._company = company
                        return self._company
                    else:
                        logging.error('GetSessionCompany返回码异常：%s, 获取公司失败, sessionid: %s' % (flag, self.session_id))
                        raise AuthError('session异常, 获取公司失败')
                else:
                    return 'Co_1'

    @property
    def user(self) -> str:
        """
        获取当前登录用户
        """
        if self._user:
            return self._user
        else:
            if NO_SESSION:
                return '1'
            else:
                if request().config.version == 0:
                    from py_opm_wm_bm import GetSessionUserId
                    flag, user = GetSessionUserId(self.session_id)
                    if flag == 0 or flag is True:
                        self._user = user
                        return self._user
                    else:
                        logging.error('GetSessionUserId返回码异常：%s, 获取用户失败，sessionid: %s' % (flag, self.session_id))
                        raise AuthError('session异常, 获取用户失败')
                else:
                    return request().headers.get('userid', '')

    @property
    def user_group(self) -> str:
        """
        获取登录用户组
        """
        if self._user_group:
            return self._user_group
        else:
            if NO_SESSION:
                return '1'
            else:
                if request().config.version == 0:
                    from py_opm_wm_bm import GetSessionUserGroupId
                    flag, user_group = GetSessionUserGroupId(self.session_id)
                    if flag == 0 or flag is True:
                        self._user_group = user_group
                    else:
                        logging.error('GetSessionUserGroupId返回码异常：%s, 获取用户组失败, sessionid: %s' % (flag, self.session_id))
                        raise AuthError('session异常, 获取用户组失败')
                else:
                    self._user_group = ''

                return self._user_group

    @property
    def account(self) -> str:
        """
        获取登陆租户
        """
        return request().headers.get('accountid')

    @property
    def role(self) -> list:
        """
        获取登陆角色，包含基础角色
        """
        if self._role:
            return self._role
        else:
            from db.customer.Cloudwise.user import DubboUser
            role_data = DubboUser().role_info()
            self._role = [i['roleId'] for i in role_data]
            return self._role

    @property
    def role_filter(self):
        """
        当包含多个角色的时候，过滤基础角色
        """
        if self._role_filter:
            return self._role_filter
        else:
            from db.customer.Cloudwise.user import DubboUser
            role_data = DubboUser().role_info()
            self._role_filter = [i['roleId'] for i in role_data if (str(i.get('type')) != '3' and len(role_data) != 1)
                                 or len(role_data) == 1]
            return self._role_filter

    @property
    def is_admin(self) -> bool:
        """
        检查当前登陆用户是否为管理员
        """
        if isinstance(self._is_admin, tuple):
            return self._is_admin[1]
        else:
            if NO_SESSION:
                return True
            else:
                if request().config.version == 0:
                    from db.public.Setting.user import UserGroupCache
                    group_info = UserGroupCache().items(request().user_group)
                    self._is_admin = (1, group_info.get('is_admin'))
                else:
                    from db.customer.Cloudwise.user import DubboUser
                    self._is_admin = (1, DubboUser().check_admin())
                return self._is_admin[1]


class Request(SessionData):
    """
    解析来来自WSGI Server的请求参数
    """

    def __init__(self, scope, receive, send):
        super().__init__()
        self._stream_consumed = False  # 判断String流是否被读取
        self.scope = scope
        self.receive = receive
        self.send = send
        self.status_code = HttpCode.st_200_ok  # 默认的响应码
        self.response_content_type = 'application/json; charset=utf-8'  # 默认的response类型
        self.module_list = None  # 所有模块列表
        self.config = None  # 配置文件

        self.url = self.scope.get('path', '').split('?')[0]  # 请求的url
        self.peer_ip = self.scope.get('server', ('', 0))[0]
        self.request_type = self.scope.get('method', 'GET')
        self._content_type = None
        self._headers = None
        self._cookie = None
        self._GET = None
        self._POST = None
        self._POST_NEW = None

    @property
    def headers(self) -> dict:
        """
        获取并返回所有请求头
        """
        if self._headers:
            return self._headers
        else:
            self._headers = {}
            for i in self.scope.get('headers', []):
                self._headers[i[0].decode().lower()] = i[1].decode()
            return self._headers

    @property
    def cookie(self) -> dict:
        """
        获取请求cookie
        """
        if self._cookie:
            return self._cookie
        else:
            cookie_dict = dict()

            if NO_SESSION:
                pass
            else:
                for cookie in self.headers.get('cookie', '').split('; '):
                    try:
                        k, v = cookie.split('=', 1)
                    except ValueError:
                        raise AuthError('没有cookie')
                    cookie_dict[k] = v

            self._cookie = cookie_dict
            return self._cookie

    @property
    def callback(self) -> str:
        """
        返回回调标志
        """
        return self.GET.get('callbackparam') or ""

    @property
    def GET(self) -> dict:
        """
        获取get方法传递的参数
        """
        if self._GET:
            return self._GET
        else:
            query = self.scope.get('query_string', b'').decode()
            self._GET = {k: v[0] for k, v in parse_qs(query).items()}
            return self._GET

    async def stream(self):
        if hasattr(self, "_body"):
            yield self._body
            yield b""
            return

        if self._stream_consumed:
            raise RuntimeError("IO流已被使用")

        self._stream_consumed = True
        while True:
            message = await self.receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if body:
                    yield body
                if not message.get("more_body", False):
                    break
        yield b""

    @property
    async def POST_ASYNC(self) -> t.Any:
        """
        获取post方法传递的参数，异步
        """
        if self._POST:
            return self._POST
        else:
            parse_dict = {
                'application/x-www-form-urlencoded': self._post_x_www_form_urlencoded,
                'application/json': self._post_json,
                'multipart/form-data': self._post_form_data
            }
            chunks = []
            async for chunk in self.stream():
                chunks.append(chunk)
            try:
                content_type = self.content_type.split(';')[0] if self.content_type\
                    else 'application/x-www-form-urlencoded'
                data = parse_dict.get(content_type)(b"".join(chunks) if content_type == 'multipart/form-data'
                                                    else b"".join(chunks).decode())
            except TypeError:
                raise DataError(
                    '不支持的body参数类型: %s，目前支持的类型(%s)' % (self.content_type, ','.join(parse_dict.keys())))
            self._POST = data
            return self._POST

    @property
    def POST_PROP(self) -> t.Any:
        return self._POST

    @POST_PROP.setter
    def POST_PROP(self, data):
        self._POST = data

    @property
    def POST(self):
        if not self._POST_NEW:
            post_prop = request().POST_PROP
            if not post_prop:
                data = {}
            elif isinstance(post_prop, list):
                data = [i for i in post_prop]
            else:
                data = {k: v for k, v in post_prop.items()}
            self._POST_NEW = data
        return self._POST_NEW

    def allowed_file(self, filename) -> bool:
        """
        判断是否是允许的文件类型
        :param filename: 要查询的文件
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.config.ALLOWED_EXTENSIONS

    def upload_file(self, path: str = None) -> t.Union[dict, list]:
        """
        存储上传的文件
        :param path: 上传路径, 不传使用默认配置
        """
        res = []
        for file in self._POST:
            if not file.get('filename'):
                continue
            if not self.allowed_file(file.get('filename')):
                raise FileError('不支持的文件类型: %s' % file.get('filename'))

            path = path or self.config.TMP_DIR
            if not os.path.exists(path):
                os.makedirs(path)
            while os.path.exists(os.path.join(path, file['filename'])):
                file['filename'] = file['filename'] + ''.join(random.sample(string.ascii_letters + string.digits, 8))
            with open(os.path.join(path, file.get('filename')), 'wb') as f:
                f.write(file['data'])
            res.append(file)
        return res[0] if len(res) == 1 else res

    def upload(self, path):
        """
        文件上传，老的方法，不推荐使用此方法了
        """
        file = self.upload_file(path)
        return file['filename']

    @property
    def PUT(self) -> t.Any:
        """
        获取put方法传递参数
        """
        return self.POST

    @property
    def DELETE(self) -> dict:
        """
        获取delete方法传递的参数
        """
        return self.GET

    def _post_form_data(self, post_data):
        """
        解析form-data、用于文件上传
        """

        fs = cgi.FieldStorage(fp=BytesIO(post_data), environ=scope_to_environ(self.scope),
                              headers=self.headers, keep_blank_values=1)

        return [{'name': i.name, 'filename': i.filename, 'data': i.value, 'detail': i} for i in fs.list]

    @staticmethod
    def _post_x_www_form_urlencoded(post_data: str) -> dict:
        """
        解析x-www-form-urlencoded
        """
        return {k: v[0] for k, v in parse_qs(post_data, keep_blank_values=True).items()}

    @staticmethod
    def _post_json(post_data: str) -> dict:
        """
        解析json
        """
        json_data = json.loads(post_data)

        def _dumps_json(j_data):

            if isinstance(j_data, list):
                """列表分支"""
                for idx, data_ in enumerate(j_data):
                    try:
                        if isinstance(json.loads(data_), (list, dict)):
                            data_ = json.loads(data_)

                    except (ValueError, SyntaxError, TypeError):
                        pass

                    """判断是否需要递归"""
                    if isinstance(data_, dict) or isinstance(data_, list):
                        data_ = _dumps_json(data_)
                    j_data[idx] = data_
                return j_data

            elif isinstance(j_data, dict):
                """字典分支"""
                for key, val in j_data.items():
                    try:
                        if isinstance(json.loads(val), (list, dict)):
                            j_data[key] = json.loads(val)

                    except (ValueError, SyntaxError, TypeError):
                        pass

                    """判断是否需要递归"""
                    if isinstance(j_data[key], dict) or isinstance(j_data[key], list):
                        j_data[key] = _dumps_json(j_data[key])
                return j_data

        json_data = _dumps_json(json_data)
        return json_data

    @property
    def content_type(self):
        """
        获取请求content_type
        """
        if self._content_type:
            return self._content_type
        else:
            self._content_type = self.headers.get('content-type')
            return self._content_type

    def add_header(self, header: str, value: str):
        """
        添加响应头
        :param header: 要添加的响应头
        :param value: 响应头的值
        """
        self.headers[header] = value

    @property
    def web_path(self) -> str:
        """
        获取web服务所在目录
        """
        return os.path.join(__file__.split('webexpress')[0], 'webexpress')


class Response:
    """
    响应类
    """

    def __init__(self, data: t.Any, request_handle: Request = None, *args, **kwargs):
        """
        初始化响应类
        :param data: 响应数据
        :param request_handle: request实例
        :param kwargs:
                        type：响应类型
                            args：default 默认响应，会调用package_data对data进行包装
        """
        self.request = request_handle if request_handle else request()
        self.kwargs = kwargs
        self.res = data

    @property
    async def data(self) -> str:
        if self.kwargs.get('type') == 'default':
            return await self.package_data(self.res, self.request.callback)
        else:
            return self.res

    @staticmethod
    async def package_data(data: t.Any, callback: str) -> json:
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


async def run_in_threadpool(func, *args, **kwargs):
    if kwargs:
        func = functools.partial(func, **kwargs)
    return await anyio.to_thread.run_sync(func, *args)


class View:
    def __init__(self, request: Request, *args, **kwargs):
        super().__init__()
        self.request = request

    async def dispatch_request(self):
        """
        根据请求类型调用对应的类方法
        """

        meth = getattr(self, self.request.request_type.lower(), None)

        if meth is None and self.request.request_type == "head":
            meth = getattr(self, "get", None)

        if not meth:
            raise HTTPMethodError(self.request.request_type)

        return await meth() if iscoroutinefunction(meth) else await run_in_threadpool(meth)
