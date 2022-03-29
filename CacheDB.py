# @Create  : 2022/02/25 15:53
# @Author  : great
# @Remark  : 缓存操作方法，适配redis数据库

import redis
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
