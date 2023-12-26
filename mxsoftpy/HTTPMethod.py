# -*- coding: UTF-8 -*-
# @Create   : 2021/5/26 9:47
# @Author   : yh
# @Remark   : http会话相关的公共方法
from view import Response


def redirect(url: str, params: dict = None, status_code=302):
    """
    重定向
    :param url: 要重定向的url
    :param params: 参数字典
    :param status_code: 重定向状态码，默认302
    """
    url = url + '?' + '&'.join([k + "=" + v for k, v in params.items()]) if params else url

    response = Response('')

    response.request.status_code = status_code
    response.request.headers['Location'] = url
    return response
