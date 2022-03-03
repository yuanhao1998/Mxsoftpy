# -*- coding: utf_8 -*-
# @Create   : 2021/8/3 15:14
# @Author   : yh
# @Remark   : 初始化加载
from redis import ConnectionPool

from utils.conf.mxconfig import MxConfig

_server_config = None  # 配置文件全局变量
_redis_conn_pool = None  # redis连接池


def load():
    server_config_init()  # 加载配置文件
    redis_init()  # 初始化redis


def redis_init():
    """
    初始化redis连接池
    """
    global _redis_conn_pool

    _redis_conn_pool = RedisInit()


class RedisInit:
    def __init__(self):
        self.__redis_conn_pool = {}

    @staticmethod
    def __get_redis_conf() -> dict:
        """
        获取redis配置
        """
        try:
            from utils.conf.mxconfig import MxConfig
            host = MxConfig.REDIS_HOST
            port = MxConfig.REDIS_PORT
            max_connections = MxConfig.REDIS_CONN_MAX_NUM
            socket_connect_timeout = MxConfig.REDIS_CONN_TIMEOUT
        except (ModuleNotFoundError, ImportError, AttributeError):
            host = '127.0.0.1'
            port = 8123
            max_connections = 10
            socket_connect_timeout = 3
        return {"host": host, "port": port, "max_connections": max_connections,
                "socket_connect_timeout": socket_connect_timeout}

    def get(self, db):
        if self.__redis_conn_pool.get(db):
            return self.__redis_conn_pool.get(db)
        else:
            self.__redis_conn_pool[db] = ConnectionPool(**self.__get_redis_conf(), db=db)
            return self.__redis_conn_pool[db]


def server_config_init():
    global _server_config

    _server_config = __LoadServerConfig(MxConfig.CONFIG_PATH)


class __LoadServerConfig:
    """
    读取配置
    """

    def __init__(self, config_path):
        from configparser import ConfigParser
        from os.path import basename, isfile
        for config in config_path:

            if not isfile(config):
                continue
            conf = ConfigParser()
            try:
                conf.read(config, encoding='gbk')
            except UnicodeDecodeError:
                try:
                    conf.read(config, encoding='utf-8')
                except UnicodeDecodeError:
                    conf.read(config, encoding='gb2312')
            conf_name = basename(config).split(".")[0]
            if hasattr(self, conf_name):
                conf_name = conf_name + "_1"
            self.__setattr__(conf_name, self.__new_cls(conf_name, conf))

    def __new_cls(self, conf_name, conf):
        type_attr = {}
        for k, v in conf.items():

            if not isinstance(v, str):
                v = self.__new_cls(k, v)
            type_attr[k] = v

        return type(conf_name, (), type_attr)
