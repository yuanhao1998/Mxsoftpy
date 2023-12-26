# -*- coding: UTF-8 -*-
# @Create   : 2021/6/25 16:59
# @Author   : yh
# @Remark   : mx框架Server层


class Server:

    def __init__(self):
        super().__init__()
        self.db = getattr(self, '__db__')() if hasattr(self, '__db__') else None
        self.model = getattr(self, '__model__') if hasattr(self, '__model__') else None

    def list(self, *args, **kwargs):
        """
        展示数据的base方法
        """
        return self.db.list(*args, **kwargs)

    def create(self, *args, **kwargs):
        """
        添加数据的base方法
        """
        return self.db.create(**self.model(*args, **kwargs).dict())

    def update(self, code,  *args, **kwargs):
        """
        更新数据的base方法
        :param code: 要更新的键
        """
        return self.db.update(code, **self.model(*args, **kwargs).dict())

    def delete(self, code):
        """
        删除数据的base方法
        :param code: 要删除的键
        """
        return self.db.delete(code)

    def retrieve(self, code):
        """
        获取单个数据详情的base方法
        :param code: 要获取详情的键
        """
        return self.db.retrieve(code)


class AsyncServer:

    def __init__(self):
        super().__init__()
        self.db = getattr(self, '__db__')() if hasattr(self, '__db__') else None
        self.model = getattr(self, '__model__') if hasattr(self, '__model__') else None

    async def list(self, *args, **kwargs):
        """
        展示数据的base方法
        """
        return await self.db.list(*args, **kwargs)

    async def create(self, *args, **kwargs):
        """
        添加数据的base方法
        """
        return await self.db.create(self.model(*args, **kwargs))

    async def update(self, code,  *args, **kwargs):
        """
        更新数据的base方法
        :param code: 要更新的键
        """
        return await self.db.update(code, self.model(*args, **kwargs))

    async def delete(self, code):
        """
        删除数据的base方法
        :param code: 要删除的键
        """
        return await self.db.delete(code)

    async def retrieve(self, code):
        """
        获取单个数据详情的base方法
        :param code: 要获取详情的键
        """
        return await self.db.retrieve(code)
