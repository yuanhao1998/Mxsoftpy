# @Create  : 2023/12/26 15:26
# @Author  : great
# @Remark  :
from starlette.testclient import TestClient as TestClient
from mxsoftpy import Mx, View
from mxsoftpy.view import SSEResponse

app = Mx()


class RequestHeaders(View):
    def post(self):
        return "ok", self.request.headers


class RequestCookie(View):
    def post(self):
        return "ok", self.request.cookie


class RequestSession(View):
    def post(self):
        return "ok", self.request.session_id


class RequestData(View):
    def get(self):
        return "ok", self.request.GET

    def post(self):
        return "ok", self.request.POST


class ReqeustSSE(View):
    async def post(self):
        def run():
            i = 10
            while i > 0:
                yield i
                i -= 1
        return SSEResponse(run())


app.add_resource(RequestHeaders, "/request_headers")
app.add_resource(RequestCookie, '/request_cookie')
app.add_resource(RequestSession, "/request_session")
app.add_resource(RequestData, "/request_data")
app.add_resource(ReqeustSSE, "/request_sse")
client = TestClient(app)


def test_headers():
    """
    测试请求头
    """
    resp = client.post("/request_headers", headers={"hello": "world"})
    assert resp.json().get("data", {}).get("hello") == "world" and resp.status_code == 200


def test_cookie():
    """
    测试cookie
    """
    resp = client.post("/request_cookie", cookies={"hello": "world"})
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": {"hello": "world"}
    } and resp.status_code == 200


def test_session_id():
    """
    测试session_id获取
    """
    resp = client.post("/request_session", cookies={"mxsessionid": "hello_world"})
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": "hello_world"
    } and resp.status_code == 200


def test_get():
    """
    测试Get参数获取
    """
    resp = client.get("/request_data?hello=world")
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": {"hello": "world"}
    } and resp.status_code == 200


def test_post():
    """
    测试Post参数获取
    """
    resp = client.post("/request_data", json={"hello": "world"})
    assert resp.json() == {
        "status": "success",
        "errmsg": "ok",
        "data": {"hello": "world"}
    } and resp.status_code == 200
