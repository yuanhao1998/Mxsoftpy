# @Create  : 2022/02/25 15:53
# @Author  : great
# @Remark  : 缓存操作方法，适配redis数据库
from typing import Union, List, Any

import redis
from superbsapi import *
from mxsoftpy import Model
from mxsoftpy.db_def.db_error import BS_NOERROR
from mxsoftpy.db_def.def_type import type_map
from mxsoftpy.BaseDB import BaseDB
from mxsoftpy.exception import DBError
from mxsoftpy.globals import redis_pool


class RedisDB(redis.Redis):

    def __init__(self):
        super().__init__()
        self.__conn: redis.Redis = None

    def open(self, file: int = 0, decode_responses: bool = True) -> redis.Redis:
        """
        打开数据库
        :param file: 数据库
        :param decode_responses: 取出的结果是否解码， False 返回字节、True 返回decode的数据
        """
        self.__conn = redis.Redis(connection_pool=redis_pool().get(file), db=file, decode_responses=decode_responses)
        return self.__conn

    def __getattribute__(self, name: str):
        if name.startswith("_"):
            return super().__getattribute__(name)
        else:
            try:
                return self.__conn.__getattribute__(name)
            except BaseException:
                return super().__getattribute__(name)


class CacheDB(BaseDB):

    def return_value(self, res: tuple) -> Union[int, str, tuple, None]:
        """
        用于直接返回结果集的函数，处理其返回值

        :param res: 错误信息及函数返回的数据
        :return: 返回信息
        """

        if isinstance(res, tuple):
            if len(res) == 2:
                res, self._handle = res
                data = None
            elif len(res) == 3:
                res, self._handle, data = res
            else:
                res, self._handle, data = res[0], res[1], res[2:]
        else:
            data = None

        if res != BS_NOERROR:
            raise DBError(res)

        return data

    def exec_bs(self, operate: str, *args: Any, **kwargs: Any) -> Union[int, str, tuple, None]:
        """
        执行bs函数
        """

        res = eval(operate)(self._handle, *args, **kwargs)
        return self.return_value(res)

    def insert_file(self, file_name: str, config_name: str = 'memdb.ini', host: str = None, port: int = None) -> int:
        """
        插入数据库
        eg: TreeDB.insert_file('test', host='127.0.0.1', port=8123)

        :param file_name: 数据库名称
        :param config_name: 数据库名称
        :param host: 主机ip
        :param port: 端口
        """

        _host, _port = self._get_host_port(file_name)
        return self.exec2('bs_memdb_create_newfile', file_name, config_name, host or _host, port or _port)

    def open(self, file: str = None, host: str = None, port: int = None) -> "CacheDB":
        """
        打开数据库
        """

        _host, _port = self._get_host_port(file)
        file = 'Cache_' + (file or self._get_file())
        self.exec('bs_memdb_open', file, host or _host, port or _port)
        return self

    def set(self, key: str, value: str, value_type=None, expire: int = -1, create=False, update=False) -> int:
        """
        设置一个String缓存

        :param key: key
        :param value: value
        :param value_type: value类型
        :param expire: 过期时间 -1 为永不失效
        :param create: 如果设置为True,则只有name不存在时,当前set操作才执行(新建)
        :param update: 如果设置为True，则只有name存在时，当前set操作才执行（修改）
        """
        value_type = type_map.get(value_type) or type_map.get(type(value).__name__)
        return self.exec_bs('bs_memdb_set', key, value, value_type, expire, create, update)

    def get(self, key: str) -> str:
        """
        取一个String数据的值

        :param key: 要获取的key
        """
        return self.exec_bs('bs_memdb_get', key)

    def delete(self, key: str) -> int:
        """
        删除一个String数据的值

        :param key: 要删除的key
        """
        return self.exec_bs('bs_memdb_delete_key', key)

    def mset(self, items: Union[List[tuple], dict, Model]) -> int:
        """
        批量插入String类型的数据

        :param items: 插入的数据
        """
        return self.exec_bs('bs_memdb_mset', self._generation_items(items)) if items else 0

    def mget(self, keys: List[str]) -> dict:
        """
        批量取出String类型的数据

        :param keys: 要查询的key
        """
        res = dict()
        self.exec_bs('bs_memdb_mget', keys, res)
        return res

    def hset(self, name: str, key: str, value: Any, value_type=None) -> int:
        """
        设置一个Hash缓存

        :param name: hash名称
        :param key: key
        :param value: value
        :param value_type: 数据类型，不传字段获取
        """
        value_type = type_map.get(value_type) or type_map.get(type(value).__name__)
        return self.exec_bs('bs_memdb_hset', name, key, value, value_type)

    def hget(self, name: str, key: str) -> Any:
        """
        取一个Hash缓存key的数据

        :param name: hash名称
        :param key: key
        """
        return self.exec_bs('bs_memdb_hget', name, key)

    def hmset(self, name: str, items: Union[List[tuple], dict, Model]) -> int:
        """
        批量插入Hash类型的数据

        :param name: hash名称
        :param items: 插入的数据
        """
        return self.exec_bs('bs_memdb_hmset', name, self._generation_items(items)) if items else 0

    def hmget(self, name: str, keys: List[str] = None) -> dict:
        """
        批量取出Hash类型的数据

        :param name: hash名称
        :param keys: 要查询的key, 不传获取所有
        """
        res = dict()
        self.exec_bs('bs_memdb_hmget', name, keys or [], res)
        return res

    def hdel_key(self, name: str, key: str) -> int:
        """
        删除一个Hash缓存的key

        :param name: hash名称
        :param key: key
        """
        return self.exec_bs('bs_memdb_delete_hkey', name, key)

    def hmdel_key(self, name: str, keys: List[str]) -> int:
        """
        批量删除Hash缓存的key
        
        :param name: Hash名称
        :param keys: key
        """
        return self.exec_bs('bs_memdb_delete_hmkey', name, keys)

    def hdel(self, name: str) -> int:
        """
        删除一个Hash
        
        :param name: hash名称
        """
        return self.exec_bs('bs_memdb_delete_hash', name)
