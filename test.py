# -*- coding: utf_8 -*-
# @Create   : 2021/9/13 14:16
# @Author   : yh
# @Remark   :
from sqlalchemy import Column, Integer, String, inspect
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CompanyOrm(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True, nullable=False)
    public_key = Column(String(20), index=True, nullable=False, unique=True)
    name = Column(String(63), unique=True)
    domains = Column(ARRAY(String(255)))


fields = inspect(CompanyOrm)
for i in fields.columns:
    pass
