# -*- coding: utf_8 -*-
# @Create   : 2021/9/10 17:24
# @Author   : yh
# @Remark   : 所有的数据库类型

VDT_EMPTY = 0x00
VDT_STR = 0x01
VDT_I32 = 0x03
VDT_I64 = 0x04
VDT_I8 = 0x05
VDT_DOUBLE = 0x06
VDT_FLOAT = 0x07
VDT_TIME = 0x09
VDT_UI8 = 0x10
VDT_UI64 = 0x13
VDT_TIMESTR = 0x30

I32 = type('i32', (int, ), {})
double = type('double', (int, ), {})
int8 = type('int8', (int, ), {})
int64 = type('int64', (int, ), {})
ui8 = type('ui8', (int, ), {})
ui64 = type('ui64', (int, ), {})
time = type('time', (int, ), {})
timestr = type('timestr', (int, ), {})
empty = type('empty', (int, ), {})

type_map = {
    'str': VDT_STR,
    'float': VDT_FLOAT,
    'double': VDT_DOUBLE,
    'int': VDT_I32,
    'int8': VDT_I8,
    'int64': VDT_I64,
    'ui8': VDT_UI8,
    'ui64': VDT_UI64,
    'time': VDT_TIME,
    'timestr': VDT_TIMESTR,
    'empty': VDT_EMPTY,

    'ConstrainedIntValue': VDT_I32,
    'ConstrainedFloatValue': VDT_FLOAT,
    'ConstrainedStrValue': VDT_STR,
    'ConstrainedDecimalValue': VDT_TIME
    # 其他的类型，以后用到了再添加
}

type_c_python = {
    VDT_STR: 'str',
    VDT_FLOAT: 'float',
    VDT_DOUBLE: 'float',
    VDT_I8: 'int',
    VDT_I32: 'int',
    VDT_I64: 'int',
    VDT_UI8: 'int',
    VDT_UI64: 'int',
    VDT_TIME: 'int',
    VDT_TIMESTR: 'str',
    VDT_EMPTY: 'NoneType'
}

type_c_str = {
    VDT_EMPTY: 'VDT_EMPTY',
    VDT_STR: 'VDT_STR',
    VDT_I32: 'VDT_I32',
    VDT_I64: 'VDT_I64',
    VDT_I8: 'VDT_I8',
    VDT_DOUBLE: 'VDT_DOUBLE',
    VDT_FLOAT: 'VDT_FLOAT',
    VDT_TIME: 'VDT_TIME',
    VDT_UI8: 'VDT_UI8',
    VDT_UI64: 'VDT_UI64',
    VDT_TIMESTR: 'VDT_TIMESTR'
}
