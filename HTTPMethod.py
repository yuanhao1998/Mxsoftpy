# -*- coding: utf_8 -*-
# @Create   : 2021/5/26 9:47
# @Author   : yh
# @Remark   : http会话相关的公共方法
from .def_http_code import HttpCode, WeMr


def redirect(session, url: str, params: dict):
    """
    重定向
    :param session: http会话
    :param url: 要重定向的url
    :param params: 参数字典
    :return:
    """
    query = list()

    for k, v in params.items():
        query.append(k + "=" + v)
    if len(query) > 0:
        url = url + "?" + "&".join(query)

    headers = session.GetHttpResponseHead()
    headers.SetStatus(HttpCode.st_302_found)
    headers.SetStatusDescription("OK")
    headers.SetContentType("text/html")
    headers.SetLocation(url)
    headers.SetContentLength(0)
    session.SendHeader()
    session.SendData("")


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
