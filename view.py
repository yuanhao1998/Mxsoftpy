# -*- coding: utf_8 -*-
# @Create   : 2021/5/17 9:46
# @Author   : yh
# @Remark   : session处理类
import ast
import json
import typing as t
from urllib.parse import parse_qs

from .def_http_code import HttpCode, HttpType
from .exception import CError, HTTPMethodError, DataError, AuthError
from .globals import request


class Request:
    """
    session处理基类
    """

    def __init__(self, session, *args, **kwargs):
        super().__init__()
        self.session = session  # session会话
        self.status_code = HttpCode.st_200_ok  # 默认的响应码
        self.response_content_type = 'application/json; charset=utf-8'  # 默认的response类型
        self.module_list = None  # 所有模块列表

        self._request_headers_cls = None
        self._response_headers_cls = None
        self._headers = None
        self._cookie = None
        self._url_cls = None
        self._peer_ip = None
        self._GET = None
        self._POST = None
        self._web_path = None
        self._request_type = None
        self._content_type = None
        self._session_id = None
        self._company = None
        self._user = None

    @property
    def session_id(self):
        """
        获取session id
        """
        # from mxsoft import CheckMxSession
        # return CheckMxSession(self.session)
        return self.cookie.get('mxsessionid')

    @property
    def company(self):
        """
        获取公司
        """
        if self._company:
            return self._company
        else:
            from py_opm_wm_bm import GetSessionCompany
            flag, company = GetSessionCompany(self.session_id)
            if flag == 0 or flag is True:
                self._company = company
                return self._company
            else:
                raise AuthError('GetSessionCompany返回码异常：%s, 获取公司失败' % flag)

    @property
    def user(self):
        """
        获取用户
        """
        if self._user:
            return self._user
        else:
            from py_opm_wm_bm import GetSessionUserId
            flag, user = GetSessionUserId(self.session_id)
            if flag == 0 or flag is True:
                self._user = user
                return self._user
            else:
                raise AuthError('GetSessionUserId返回码异常：%s, 获取用户失败' % flag)

    @property
    def request_headers_cls(self):
        """
        获取request_headers类
        """
        if self._request_headers_cls:
            return self._request_headers_cls
        else:
            try:
                self._request_headers_cls = self.session.GetHttpRequestHead()
            except TypeError:
                raise CError('session.GetHttpRequestHead()')
            return self._request_headers_cls

    @property
    def response_headers_cls(self):
        """
        获取response_headers类
        :return:
        """
        if self._response_headers_cls:
            return self._response_headers_cls
        else:
            try:
                self._response_headers_cls = self.session.GetHttpResponseHead()
            except TypeError:
                raise CError('session.GetHttpResponseHead()')
            return self._response_headers_cls

    @property
    def headers(self) -> dict:
        """
        获取并返回所有请求头
        """
        if self._headers:
            return self._headers
        else:
            header_list = list()
            header_dict = dict()
            try:
                self.request_headers_cls.GetAllHead(header_list)
            except TypeError:
                raise TypeError('session.GetHttpRequestHead().GetAllHead()')
            for header in header_list:
                header_class = header.split(': ')
                if len(header_class) == 2:
                    header_dict[header_class[0].lower()] = header_class[1]
            self._headers = header_dict
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

            for cookie in self.headers.get('cookie').split('; '):
                try:
                    k, v = cookie.split('=')
                except ValueError:
                    raise AuthError('没有cookie')
                cookie_dict[k] = v

            self._cookie = cookie_dict
            return self._cookie

    @property
    def url_cls(self):
        """
        获取请求url类
        class GetUrl:
            GetFragment()、GetHost()、 GetPass()、GetPath()、GetQuery()、GetQueryStringMap()、GetQueryStringMapEx()、
            GetScheme()、GetUrlType()、GetUser()
        """
        if self._url_cls:
            return self._url_cls
        else:
            try:
                self._url_cls = self.session.GetUrl()
            except TypeError:
                raise CError('session.GetUrl()')
            return self._url_cls

    @property
    def url(self) -> str:
        """
        获取请求url
        """
        try:
            return self.url_cls.GetPath()
        except TypeError:
            raise CError('session.GetUrl().GetPath()')

    @property
    def peer_ip(self):
        """
        获取请求ip
        """
        if self._peer_ip:
            return self._peer_ip
        else:
            from mxsoft import GetPeerIP
            self._peer_ip = GetPeerIP(self.session)
            return self._peer_ip

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
            query = dict()
            try:
                self.url_cls.GetQueryStringMapEx(query)
            except TypeError:
                raise CError('GetUrl().GetQueryStringMapEx()')
            self._GET = query
            return self._GET

    @property
    def POST(self) -> t.Any:
        """
        获取post方法传递的参数
        """
        if self._POST:
            return self._POST
        else:
            parse_dict = {
                'application/x-www-form-urlencoded': self._post_x_www_form_urlencoded,
                'application/json': self._post_json
            }
            try:
                post_length, post_data = self.session.GetPostString()
            except TypeError:
                raise CError('GetPostString()')
            try:
                data = parse_dict.get(
                    self.content_type.split(';')[0] if self.content_type else 'application/x-www-form-urlencoded')(
                    post_data)
            except TypeError:
                raise DataError('不支持的body参数类型: %s，目前支持的类型(%s)' % (self.content_type, ','.join(parse_dict.keys())))
            self._POST = data
            return self._POST

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

    def _post_form_data(self):
        """
        解析form-data
        """
        # TODO 未来再支持form_data

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
                        data_ = data_ if isinstance(json.loads(data_), int) else json.loads(data_)
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
                        j_data[key] = val if isinstance(json.loads(val), int) else json.loads(val)
                    except (ValueError, SyntaxError, TypeError):
                        pass

                    """判断是否需要递归"""
                    if isinstance(j_data[key], dict) or isinstance(j_data[key], list):
                        j_data[key] = _dumps_json(j_data[key])
                return j_data

        json_data = _dumps_json(json_data)
        return json_data

    @property
    def web_path(self) -> str:
        """
        获取web服务所在目录
        """
        if self._web_path:
            return self._web_path
        else:
            try:
                self._web_path = self.session.GetRootPath()
            except TypeError:
                raise CError('session.GetRootPath()')
            return self._web_path

    @property
    def request_type(self) -> str:
        """
        获取请求类型
        """
        if self._request_type:
            return self._request_type
        else:
            try:
                res = self.request_headers_cls.GetRequestType()
            except TypeError:
                raise CError('session.GetHttpRequestHead().GetRequestType()')
            self._request_type = HttpType.type_dict[res] if HttpType.type_dict.get(res) else HttpType.type_dict[0]
            return self._request_type

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
        try:
            self.response_headers_cls.SetAddHead(str(header), str(value))
        except TypeError:
            raise CError('session.GetHttpResponseHead().SetAddHead()')

    def upload(self, path: str, overwrite=True) -> str:
        """
        存储上传的文件
        :param path: 上传路径 <！！！ 只需要写上传路径，不要写文件名，此方法会返回文件名 ！！！>
        :param overwrite: 如果已有此文件是否覆盖
        :return: 上传的文件名
        """
        flag, file_name = self.session.UploadFile(path, overwrite)
        if flag:
            return file_name
        raise CError("读取上传文件错误")


class WSGIRequest:
    """
    解析来来自WSGI Server的请求参数
    """

    def __init__(self, environ: dict):
        self.environ = environ
        self.status_code = HttpCode.st_200_ok  # 默认的响应码
        self.response_content_type = 'application/json; charset=utf-8'  # 默认的response类型
        self.module_list = None  # 所有模块列表

        self.url = self.environ.get('REQUEST_URI', '').split('?')[0]  # 请求的url
        self.peer_ip = self.environ.get('REMOTE_ADDR', '')
        self.request_type = self.environ.get('REQUEST_METHOD', 'GET')
        self._content_type = self.environ.get('CONTENT_TYPE', '')
        self._headers = None
        self._cookie = None
        self._GET = None
        self._POST = None
        self._web_path = None

        self._session_id = None
        self._company = None
        self._user = None

    @property
    def session_id(self):
        """
        获取session id
        """
        return self.cookie.get('mxsessionid')

    @property
    def company(self):
        """
        获取公司
        """
        if self._company:
            return self._company
        else:
            from py_opm_wm_bm import GetSessionCompany
            flag, company = GetSessionCompany(self.session_id)
            if flag == 0 or flag is True:
                self._company = company
                return self._company
            else:
                raise AuthError('GetSessionCompany返回码异常：%s, 获取公司失败' % flag)

    @property
    def user(self):
        """
        获取用户
        """
        if self._user:
            return self._user
        else:
            from py_opm_wm_bm import GetSessionUserId
            flag, user = GetSessionUserId(self.session_id)
            if flag == 0 or flag is True:
                self._user = user
                return self._user
            else:
                raise AuthError('GetSessionUserId返回码异常：%s, 获取用户失败' % flag)

    @property
    def headers(self) -> dict:
        """
        获取并返回所有请求头
        """
        if self._headers:
            return self._headers
        else:
            self._headers = {}
            for k, v in self.environ.items():
                if k.startswith('HTTP_'):
                    self._headers[k[5:].lower()] = v
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

            for cookie in self.environ.get('HTTP_COOKIE').split('; '):
                try:
                    k, v = cookie.split('=')
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
            query = self.environ.get('QUERY_STRING', '')
            self._GET = {k: v for k, v in parse_qs(query).items()}
            return self._GET

    @property
    def POST(self) -> t.Any:
        """
        获取post方法传递的参数
        """
        if self._POST:
            return self._POST
        else:
            parse_dict = {
                'application/x-www-form-urlencoded': self._post_x_www_form_urlencoded,
                'application/json': self._post_json
            }
            post_length = self.environ.get('CONTENT_LENGTH')
            post_data = self.environ.get('wsgi.input').read(int(post_length)).decode('utf-8')
            try:
                data = parse_dict.get(
                    self.content_type.split(';')[0] if self.content_type else 'application/x-www-form-urlencoded')(
                    post_data)
            except TypeError:
                raise DataError('不支持的body参数类型: %s，目前支持的类型(%s)' % (self.content_type, ','.join(parse_dict.keys())))
            self._POST = data
            return self._POST

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

    def _post_form_data(self):
        """
        解析form-data
        """
        # TODO 未来再支持form_data

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
        return json.loads(post_data)

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
        if kwargs.get('type') == 'default':
            self.data = self.package_data(data, self.request.callback)
        else:
            try:
                json.loads(data)
                self.data = data
            except Exception:
                self.data = json.dumps(data, ensure_ascii=False)

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


class View:
    def __init__(self, request: "Request", *args, **kwargs):
        super().__init__()
        self.request = request

    def dispatch_request(self):
        """
        根据请求类型调用对应的类方法
        """

        meth = getattr(self, self.request.request_type.lower(), None)

        if meth is None and self.request.request_type == "HEAD":
            meth = getattr(self, "get", None)

        if not meth:
            raise HTTPMethodError(self.request.request_type)
        return meth(), self.request
