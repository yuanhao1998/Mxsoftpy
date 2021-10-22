# -*- coding: utf_8 -*-
# @Create   : 2021/9/18 14:22
# @Author   : yh
# @Remark   : 存放消息队列的操作方法
from .BaseDB import BaseDB
from .db_def.def_mq import BSMQ_OF_CREATENEW, BSMQ_OF_OPENEXIST, BSMQ_OT_COMMONMQ, BS_TIMER_INFINITE
from .db_def.def_type import type_map
from .exception import DBError, DataError


class MQ(BaseDB):

    def open(self, name: str, pwd: str = '', host: str = None, port: int = None,
             flag: int = None, path_flag: bool = False):
        """
        打开消息队列

        :param name: 队列名称
        :param pwd: 密码
        :param host: 主机名
        :param port: 端口号
        :param flag: 创建的队列类型，默认普通队列，如果需要创建优先队列或其他类型请自行传值
        :param path_flag: 不存在的队列是否需要自动创建（默认不自动创建）
        :return: 类对象
        """
        host = host or self.host
        port = port or self.port

        if path_flag:
            open_flag = BSMQ_OF_OPENEXIST if name in self.mq_list(host, port) else BSMQ_OF_CREATENEW
        else:
            open_flag = BSMQ_OF_OPENEXIST
        flag = flag or BSMQ_OT_COMMONMQ

        try:
            self.exec_handle('bs_mq_reopen', name, pwd, open_flag, flag, host, port)
        except (DBError, DataError):
            try:
                self.exec('bs_mq_open', name, pwd, open_flag, flag, host, port)
            except DBError as e:
                raise DBError(e.err_code, '打开消息队列[%s]失败' % name)

        return self

    def mq_list(self, host: str = None, port: str = None) -> list:
        """
        获取所有mq名称列表
        """
        host = host or self.host
        port = port or self.port

        mq_list = list()
        self.exec_handle('bs_mq_query_all_names', mq_list, host, port)
        return mq_list

    def push(self, data: str, data_type: int = None, label: str = '', level: int = 1) -> None:
        """
        推送数据到消息队列
        
        :param data: 要推送的数据
        :param data_type: 数据的类型，不传会自动获取
        :param label: 数据标识
        :param level: 优先级（仅对优先队列有效）
        :return:
        """
        if data_type:
            pass
        elif type_map.get(type(data).__name__):
            data_type = type_map[type(data).__name__]
        else:
            raise DataError('无法获取到value的类型！如果您未手动传入类型或确信传入类型正确，请于type_map中添加此类型')

        self.exec_handle('bs_mq_push', data, data_type, label, level)

    def pop(self, time_out: int = 0, is_peek: bool = False):
        """
        从消息队列中取出一条数据
        :param time_out: 如果队列为空，此变量可设置等待时间，如果设置999999则认为无限等待
        :param is_peek: 此变量为假则把接收到的消息从队列中清除，为真只取回消息的拷贝
        :return: 取到的数据类
        """
        try:
            res = self.exec_handle('bs_mq_pop', BS_TIMER_INFINITE if time_out == 999999 else time_out, is_peek)
        except DBError as e:
            if e.err_code == 131:
                res = (None, None, None, None, None)
            else:
                raise DBError(e.err_code, e.msg)

        class Data:
            def __init__(self, data: tuple):
                self.data = data[1]
                self.label = data[2]
                self.time = data[3]

            def __str__(self):
                return str({'data': self.data, 'label': self.label, 'time': self.time})

        return Data(res)

    def length(self):
        """
        获取一个打开MQ中的消息个数
        return：如果成功返回消息个数，否则返回错误码
        """
        try:
            res = self.exec_handle('bs_mq_length')
        except DBError as e:
            if e.err_code == 131:
                res = (None, None, None, None, None)
            else:
                raise DBError(e.err_code, e.msg)

        return res
