# -*- coding: utf_8 -*-
# @Create   : 2021/8/3 15:14
# @Author   : yh
# @Remark   : 读取配置文件的基类
from mxsoftpy.exception import FileError


class ConfBase:

    def __init__(self):
        self._conf_path = None
        self._conf = None

    @property
    def conf_path(self):
        """
        配置文件的路径
        :return:
        """
        return self._conf_path

    @conf_path.setter
    def conf_path(self, value):
        import os
        self._conf_path = os.path.join(__file__.split('webexpress')[0], 'python', 'python_review', 'utils', 'conf',
                                       'module_conf', '%s.ini' % value)

    @property
    def conf(self):
        if self._conf:
            return self._conf
        elif self.conf_path:
            from configparser import ConfigParser
            conf = ConfigParser()
            try:
                conf.read(self.conf_path, encoding='gbk')
            except UnicodeDecodeError:
                try:
                    conf.read(self.conf_path, encoding='utf-8')
                except UnicodeDecodeError:
                    conf.read(self.conf_path, encoding='gb2312')
                except Exception:
                    raise FileError('读取文件失败')
        else:
            raise FileError('没有指定文件名')
