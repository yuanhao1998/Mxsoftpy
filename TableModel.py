# -*- coding: utf_8 -*-
# @Author : l y w
# @Time : 2021/5/14 0014 16:41
# @Remark : Table 数据库
import datetime
import time

from superbsapi import *

from .db_def.def_table import *
from .db_def.def_type import *


class TableModel(object):

    def __init__(self, host="127.0.0.1", db_name="MXSE", post=8123):
        self.__hd = CBSHandleLoc()
        self.__host = host
        self.__db_name = db_name
        self.__post = post

    def open(self, sub_key, host=None, db_name=None, post=None):
        print(host if host else self.__host)
        open_res = self.__hd.Tabledb_Alloc(host if host else self.__host, db_name if db_name else self.__db_name,
                                           post if post else self.__post)
        assert open_res == 0, "打开数据库失败...."
        return self.__Table_Fun(self.__hd, sub_key)

    class __Table_Fun:

        def __init__(self, hd, sub_key):
            self.__hd = hd
            self.__sub_key = sub_key

        @staticmethod
        def __verify_date(date):
            try:
                time.strptime(date, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return False
            else:
                return True

        def time_range(self, **kwargs) -> tuple:
            """时间过滤"""
            end_time = datetime.datetime.now()
            start_time = end_time - datetime.timedelta(**kwargs)  # days,seconds,minutes,hours,weeks
            result = []
            ret, count = self.__hd.Tabledb_SelectRecordsByCTime(self.__sub_key, 0,
                                                                int(start_time.timestamp()),
                                                                int(end_time.timestamp()), result)
            # assert nRet == 0, "数据库不存在" if nRet in (280,) else "数据查询失败"
            print(end_time, start_time)
            print(end_time.timestamp(), start_time.timestamp())
            assert ret == 0, ret
            return result, count

        def clear_table(self):
            """清库功能"""
            return bs_tabledb_delete_record_by_ctime(self.__hd.GetConfHandle(), self.__sub_key, 0, 1, 0x02, 0x00000004)

        def get_fileds(self):
            """获取字段类型"""
            res_list = []
            res_dict = {}
            bs_tabledb_get_fields(self.__hd.GetConfHandle(), self.__sub_key, res_list)
            for i in res_list:
                res_dict[i["name"]] = i["uType"]
            return res_dict

        def condition_filter(self,count=0, **kwargs):
            """条件查询"""
            if not kwargs:
                raise AssertionError("查询条件不存在...")
            field_type = {0: [VDT_EMPTY, None], 1: [VDT_STR, "str"], 3: [VDT_I32, "int"], 4: [VDT_I64, "int"],
                          5: [VDT_I8, "int"], 6: [VDT_DOUBLE, "float"], 7: [VDT_FLOAT, "float"],
                          9: [VDT_TIME, "int"], 16: [VDT_UI8, "str"], 19: [VDT_UI64, "str"], 48: [VDT_TIMESTR, "str"]}

            python_field = {"str": [1, 48], "float": [6, 7], "int": [3, 4, 5, 9, 16, 19]}

            field_condition = {"neq": TBDB_FMC_UNEQUAL, "gt": TBDB_FMC_GREATERTHAN, "lt": TBDB_FMC_LESSTHAN,
                               "gte": TBDB_FMC_EQUALORGREATERTHAN, "lte": TBDB_FMC_EQUALORLESSTHAN, }
            query_param = {}
            query_list = []
            field_dict = self.get_fileds()
            print(field_dict)
            assert len(kwargs) <= 1, "字段不允许多个"
            for field, valve in kwargs.items():
                fields = field.rsplit("__")

                if not field_dict.get(fields[0]):
                    raise KeyError("查询的字段不存在...")
                db_field = field_dict[fields[0]]
                field_type = field_type[db_field]

                if isinstance(valve, list):
                    for val in valve:
                        if field_dict[fields[0]] not in python_field[type(val).__name__]:
                            raise ValueError("参数类型错误 请输入%s类型" % field_type[1])
                        if db_field in [16]:
                            query_list.append({"val": bytes([val]).decode(), "type": field_type[0]})
                        else:
                            query_list.append({"val": val, "type": field_type[0]})
                else:

                    if field_dict[fields[0]] not in python_field[type(valve).__name__]:
                        raise ValueError("参数类型错误 请输入%s类型" % field_type[1])
                    if db_field in [16]:
                        query_list.append({"val": bytes([valve]).decode(), "type": field_type[0]})
                    else:
                        query_list.append({"val": valve, "type": field_type[0]})

                query_param["name"] = fields[0]
                try:
                    query_param["condition"] = TBDB_FMC_EQUAL if len(fields) != 2 else field_condition[fields[1]]
                except KeyError:
                    raise KeyError("请输入正确的比较关键字: neq,gt,lt,gte,lte")
            warn_result = []
            ret, count = self.__hd.Tabledb_SelectRecordsByField(self.__sub_key, count, query_param["name"],
                                                                query_param["condition"], query_list, warn_result)

            print(ret, count)
            return warn_result

        def create_tabel(self, db_name, table):
            "创建表"
            res = bs_tabledb_create_table(self.__hd.GetConfHandle(), db_name, table, 0x00000001 | 0x00000200)

        def insert_data(self, db_name, value):
            """插入数据"""
            res = bs_tabledb_insert_record(self.__hd.GetConfHandle(), db_name, value)


if __name__ == '__main__':
    db = TableModel(host="192.168.6.158")
    # res = db.open("1.SD.16.SubMonitor.3223717").condition_filter(State__lte=3,count=1000)
    res = db.open("1.SD.16.SubMonitor.3223717").condition_filter(_CREATETIME___lte=1622014550,count=1000)
    # res = db.open("1.SD.16.SubMonitor.3223717").condition_filter(interfacestate="down",count=1000)

    for i in res:
        print(i)

