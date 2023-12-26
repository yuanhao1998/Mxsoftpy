# -*- coding: UTF-8 -*-
# @Create   : 2021/8/3 15:14
# @Author   : yh
# @Remark   : 初始化加载
def load():
    server_config_init()  # 加载配置文件


try:
    from utils.conf.mxconfig import MxConfig
except ModuleNotFoundError:
    def load():  # 无法导包时不加载配置
        pass

_server_config = None  # 配置文件全局变量


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
            conf = type("NewConfigParser", (ConfigParser,), dict(optionxform=lambda self, optionstr: optionstr))()
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
