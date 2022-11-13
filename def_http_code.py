# -*- coding: UTF-8 -*-
# @Create   : 2021/5/27 15:34
# @Author   : yh
# @Remark   : http请求响应相关
class HttpCode:
    st_100_continue = 100
    st_101_switch_protocols = 101
    st_200_ok = 200
    st_201_created = 201
    st_202_accepted = 202
    st_203_non_authoritative_information = 203
    st_204_no_content = 204
    st_205_reset_content = 205
    st_206_partial_content = 206
    st_300_multiple_choices = 300
    st_301_moved_permanently = 301
    st_302_found = 302
    st_303_see_other = 303
    st_304_not_modified = 304
    st_305_use_porxy = 305
    st_306_unused = 306
    st_307_temp_redirct = 307
    st_400_bad_request = 400
    st_401_unauthorized = 401
    st_403_forbidden = 403
    st_404_not_found = 404
    st_405_mothed_not_allowed = 405
    st_406_not_accepttable = 406
    st_407_proxy_authentication_required = 407
    st_408_request_timeout = 408
    st_409_conflict = 409
    st_410_gone = 410
    st_411_length_required = 411
    st_412_precondition_failed = 412
    st_413_request_entity_too_large = 413
    st_414_request_uri_too_long = 414
    st_415_unsupported_media_type = 415
    st_416_requested_range_not_satisfiable = 416
    st_417_expectation_failed = 417
    st_500_internal_server_error = 500
    st_501_not_implemented = 501
    st_502_bad_getway = 502
    st_503_service_unavailable = 503
    st_504_getway_timeout = 504
    st_505_http_version_not_supported = 505


class WeMr:
    WE_MR_BADREQUEST = 400
    WE_MR_BUFFERTOOSMALL = 10
    WE_MR_COMMUNICATION_ERROR = 3
    WE_MR_FAILED = 2
    WE_MR_NOTFOUNDPAGE = 404
    WE_MR_OK = 1
    WE_MR_UNKNOWNTYPE = 40


class HttpType:
    delete = 6
    get = 1
    head = 4
    options = 3
    post = 2
    put = 5
    trace = 7
    unknown = 0

    type_dict = {
        0: 'UNKNOWN',
        1: 'GET',
        2: 'POST',
        3: 'OPTIONS',
        4: 'HEAD',
        5: 'PUT',
        6: 'DELETE',
        7: 'TRACE'
    }


hop_by_hop = frozenset(
    (
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    )
)