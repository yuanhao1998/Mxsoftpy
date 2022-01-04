# -*- coding: utf_8 -*-
# @Create   : 2021/6/29 14:06
# @Author   : yh
# @Remark   : mx框架Model层
from pydantic import BaseModel


class Model(BaseModel):
    """
    暂时没有要添加或重写的方法，但是先预留出来
    """

    @classmethod
    def get_fields(cls):
        pass
