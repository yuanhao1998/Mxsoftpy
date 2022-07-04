# -*- coding: UTF-8 -*-
# @Create   : 2021/5/26 9:47
# @Author   : yh
# @Remark   : http会话相关的公共方法
from mxsoftpy.exception import CError

from .def_http_code import HttpCode, WeMr
from .view import Response


def redirect(*args, **kwargs):
    from .main import local_val

    if local_val.model == 'wsgi':
        return redirect_wsgi(*args, **kwargs)
    else:
        return redirect_mx(*args, **kwargs)


def redirect_mx(session, url: str, params: dict = None):
    """
    重定向
    :param session: http会话
    :param url: 要重定向的url
    :param params: 参数字典
    :return:
    """
    url = url + '?' + '&'.join([k + "=" + v for k, v in params.items()])if params else url

    headers = session.GetHttpResponseHead()
    headers.SetStatus(HttpCode.st_302_found)
    headers.SetStatusDescription("OK")
    headers.SetContentType("text/html")
    headers.SetLocation(url)
    headers.SetContentLength(0)
    session.SendHeader()
    session.SendData("")


def redirect_wsgi(url: str, params: dict = None, status_code=302):
    """
    重定向
    :param request: 请求
    :param url: 要重定向的url
    :param params: 参数字典
    :param status_code: 重定向状态码，默认302
    """
    url = url + '?' + '&'.join([k + "=" + v for k, v in params.items()])if params else url

    response = Response('')

    response.request.status_code = status_code
    response.request.headers['Location'] = url
    return response


def add_response(response):
    """
    添加响应信息
    """
    try:
        response.request.response_headers_cls.SetStatus(response.request.status_code)
    except TypeError:
        raise CError('session.GetHttpResponseHead().SetStatus()')
    try:
        response.request.response_headers_cls.SetContentType(response.request.response_content_type)
    except TypeError:
        raise CError('session.GetHttpResponseHead().SetContentType()')
    return response


def send_response(response):
    """
    返回响应数据
    :param response: 响应实例
    """

    if not response.request.session:
        return WeMr.WE_MR_BADREQUEST
    data_len = len(response.data)
    if type(response.data) is not bytes:
        data_bytes = bytes(response.data, encoding='utf-8')
    else:
        data_bytes = response.data
    if data_len > 1000:
        response.request.session.GetHttpResponseHead().SetContentLength(len(data_bytes))
        response.request.session.SendHeader()
        response.request.session.SendData(data_bytes)
    elif data_len > 0:
        response.request.session.GetHttpResponseHead().SetContentLength(len(data_bytes))
        response.request.session.SendHeader()
        response.request.session.SendData(response.data)
    return WeMr.WE_MR_OK
