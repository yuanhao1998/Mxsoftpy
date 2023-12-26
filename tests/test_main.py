# @Create  : 2023/12/26 14:13
# @Author  : great
# @Remark  : 单元测试入口

from starlette.testclient import TestClient as TestClient
from mxsoftpy import Mx, View

app = Mx()


class ClsAsyncHelloWorld(View):

    async def get(self):
        return "ok", "Cls Async Get Hello World"

    async def post(self):
        return "ok", "Cls Async Post Hello World"


class ClsSyncHelloWorld(View):

    def get(self):
        return "ok", "Cls Sync Get Hello World"

    def post(self):
        return "ok", "Cls Sync Post Hello World"


class ReqDataCheck(View):
    async def get(self):
        return "ok", self.request.GET

    async def post(self):
        return "ok", self.request.POST


class UndefinedMethod(View):
    pass


app.add_resource(ClsAsyncHelloWorld, "/cls_async_hello_world")
app.add_resource(ClsSyncHelloWorld, "/cls_sync_hello_world")
app.add_resource(ReqDataCheck, "/req_data_check")
app.add_resource(UndefinedMethod, "/undefined_method")
client = TestClient(app)  # 测试client


def test_cls_async_get():
    """
    异步get请求测试
    """
    resp = client.get("/cls_async_hello_world")
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": "Cls Async Get Hello World"
    } and resp.status_code == 200


def test_cls_async_post():
    """
    异步post请求测试
    """
    resp = client.post("/cls_async_hello_world")
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": "Cls Async Post Hello World"
    } and resp.status_code == 200


def test_cls_sync_get():
    """
    同步get请求测试
    """
    resp = client.get("cls_sync_hello_world")
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": "Cls Sync Get Hello World"
    } and resp.status_code == 200


def test_cls_sync_post():
    """
    同步post请求测试
    """
    resp = client.post("cls_sync_hello_world")
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": "Cls Sync Post Hello World"
    } and resp.status_code == 200


def test_req_params():
    """
    get请求url传参测试
    """
    resp = client.get("/req_data_check?hello=world")
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": {"hello": "world"}
    } and resp.status_code == 200


def test_req_json_body():
    """
    post请求json传参测试
    """
    resp = client.post("/req_data_check", json={"hello": "world"})
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": {"hello": "world"}
    } and resp.status_code == 200


def test_undefined_method():
    """
    测试未定义方法
    """
    resp = client.get("/undefined_method")
    assert resp.json() == {
        'err_type': '错误的请求方法',
        'errmsg': 'GET',
        'status': 'failed'
    } and resp.status_code == 200


def test_not_find_url():
    """
    测试找不到url
    """
    resp = client.get("/not_find_url")
    assert resp.json() == {
        'err_type': '未知的url请求',
        'errmsg': '/not_find_url',
        'status': 'failed'
    } and resp.status_code == 404
