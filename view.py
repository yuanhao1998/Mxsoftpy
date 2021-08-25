# -*- coding: utf_8 -*-
# @Create   : 2021/5/17 9:46
# @Author   : yh
# @Remark   : session处理类
import typing as t
import json
from urllib.parse import unquote

from .conf_base import ConfBase
from .exception import CError, HTTPMethodError, DataError
from .def_http_code import HttpCode, HttpType


class Request(ConfBase):
    """
    session处理基类
    """

    def __init__(self, session, *args, **kwargs):
        super().__init__()
        self.session = session  # session会话
        self.status_code = HttpCode.st_200_ok  # 默认的响应码
        self.response_content_type = 'text/html;charset=UTF-8'  # 默认的response类型

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
                    header_dict[header_class[0]] = header_class[1]
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
            try:
                cookie_str = self.request_headers_cls.GetCookie()
            except TypeError:
                raise CError('session.GetHttpRequestHead().GetCookie()')
            cookie_list = cookie_str.split('; ')

            for cookie in cookie_list:
                k, v = cookie.split('=')
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
    def POST(self) -> dict:
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
        return {unquote(post.split('=')[0]): unquote(post.split('=')[1]) if len(post.split('=')) == 2 else ''
                for post in post_data.split('&')}

    @staticmethod
    def _post_json(post_data: str) -> dict:
        """
        解析json
        """
        return json.loads(post_data)

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
            self._content_type = self.headers.get('Content-Type') or self.headers.get('content-type')
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


class Response:
    """
    响应类
    """

    def __init__(self, msg: t.Any, *args, **kwargs):
        self.msg = msg

    def __str__(self):
        return self.msg


class View(ConfBase):
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
        return self.request, meth()
