# @Create  : 2024/1/24 17:04
# @Author  : great
# @Remark  :

from mxsoftpy import TreeDB

host = "127.0.0.1"
port = 8123
db = TreeDB()


def test_file_names():
    """
    测试获取数据库所有数据库名
    """

