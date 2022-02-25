# -*- coding: utf_8 -*-
# @Create   : 2021/8/3 15:14
# @Author   : yh
# @Remark   : 初始化加载
# from redis import StrictRedis

from utils.conf.mxconfig import MxConfig

_server_config: object  # 配置文件全局变量
# _redis: StrictRedis  # redis连接配置


def load():
    server_config()  # 加载配置
    # redis_init()  # 加载配置


def redis_init():
    """
    初始化redis连接
    """
    global _redis

    _redis = StrictRedis(host=MxConfig.REDIS_HOST, port=MxConfig.REDIS_PORT, db=0)


def server_config():
    global _server_config

    class ServerConfig:
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

    _server_config = ServerConfig(MxConfig.CONFIG_PATH)
