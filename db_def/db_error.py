# -*- coding: UTF-8 -*-
# @Create   : 2021/5/11 11:14 上午
# @Author   : yh
# @Remark   : 在此定义所有的数据库错误

BS_NOERROR = 0
BS_FAILED = 1

# //////////////////common//////////////

BS_ERROR_UNKNOWN = 2
BS_ERROR_INVALIDPAGEPOOL = 3
BS_ERROR_FATALERROR = 4

BS_ERROR_AUTHFAILURE = 5
BS_ERROR_NAMELEN = 6
BS_ERROR_GETPAGE = 10
BS_ERROR_ADDDATATOPAGE = 11
BS_ERROR_INSERTBPTREE = 12
BS_ERROR_PAGEHEAD = 13
BS_ERROR_CREATEOBJECT = 14
BS_ERROR_GETFREEPAGE = 15
BS_ERROR_DATAF0RMAT = 16
BS_ERROR_BUFFERTOOSMALL = 17
BS_ERROR_COPYDATAFROMPAGE = 18
BS_ERROR_CHECKSUM = 19
BS_ERROR_OPENTREE = 20
BS_ERROR_DELETEBPTREE = 21
BS_ERROR_ALLOCMEMORY = 22
BS_ERROR_TIMEOUT = 23
BS_ERROR_INDEXTREE = 24
BS_ERROR_INDEXTREETYPE = 25
BS_ERROR_NONSUPPORT = 26
BS_ERROR_EMPTYBUFFER = 27
BS_ERROR_PARAMETER = 28
BS_ERROR_CLEARPAGEDATA = 29
BS_ERROR_DESTORYBPTREE = 30
BS_ERROR_PUSHPAGELIST = 31
BS_ERROR_POPPAGELIST = 32
BS_ERROR_PAGETOOSMALL = 33
BS_ERROR_OPENBPTREE = 34
BS_ERROR_BPTREEFIND = 35
BS_ERROR_BPTREEINSERT = 36
BS_ERROR_BPTREEDELETE = 37
BS_ERROR_BPTREEDESTORY = 38
BS_ERROR_BPTREEEDIT = 39
BS_ERROR_BPTREENOFIND = 40
BS_ERROR_BPTREEVISIT = 41
BS_ERROR_BPTREEISEMPTY = 42
BS_ERROR_OVERWRITETOPAGE = 43
BS_ERROR_SQL_SYNTAX = 44
# /////////////////////IT////////////////
BS_IT_ITEMEXISTALLREADY = 45

# ///////////////////IRST/////////////////
BS_IRST_PARSEKEYERROR = 50
BS_IRST_FINEDERROR = 51

# ////////////////////////////////////////////

BS_ERROR_STRLISTTOBUFFER = 55
BS_ERROR_BUFFERTOSTRLIST = 56
BS_ERROR_OPENTRANSACTION = 57
BS_ERROR_NOOPENTRANSACTION = 58
BS_ERROR_COMMITTRANSACTION = 59
BS_ERROR_ROLLBACKTRANSACTION = 60
BS_ERROR_TRANSACTIONALREADYBEGIN = 61
BS_ERROR_DATAPROTOCOL = 62
BS_ERROR_CONVERTDATA = 63
BS_ERROR_UNSERIALDATA = 64

# /////////////////bslist/////////////////

BS_LIST_EMPTY = 70
BS_LIST_INVALIDHEADPID = 71
BS_LIST_NOMOREITEM = 72
BS_LIST_BADITEMPAGEPOS = 73
BS_LIST_ITEMCOUNTERROR = 74
BS_LIST_PAGEDATATYPEERROR = 75

# /////////////////mq///////////////////

BS_MQ_EXISTALLREADY = 120
BS_MQ_NOEXIST = 121
BS_MQ_NOFINDPFHFLAG = 122
BS_MQ_MQHEADERROR = 123
BS_MQ_NAMEUNMATCHED = 124
BS_MQ_GETPOSTIONHEADERROR = 125
BS_MQ_MQNOINITIALIZATION = 126
BS_MQ_OPENINDEXTREE = 127
BS_MQ_INVALIDLEVEL = 128
BS_MQ_LOADLASTRECORDFAILED = 129
BS_MQ_ADDDATATOPAGEFAILED = BS_ERROR_ADDDATATOPAGE
BS_MQ_EMPTY = 131
BS_MQ_RELOADMQ = 132
BS_MQ_RELEASEMQHEAD = 134
BS_MQ_VISITMQNAMETREE = 135
BS_MQ_NOFINDMQ = 136
BS_MQ_ISNOTINDEXMQ = 137
BS_MQ_NOANYMQ = 138

# ///////////////treedb/////////////////
BS_TRDB_NOAUTHORITY_CREATEDBFILE = 157
BS_TRDB_DBFILEALREADYEXIST = 158
BS_TRDB_INITDBFILE = 159
BS_TRDB_NOINITIALIZATION = 160
BS_TRDB_MAINKEYISEMPTY = 161
BS_TRDB_MAINKEYALREADYEXIST = 162
BS_TRDB_READMAINKEYTREEROOTFAILED = 163
BS_TRDB_WRITEMAINKEYTREEROOTFAILED = 164
BS_TRDB_NOFINDPFHFLAG = 165
BS_TRDB_TRDBHEADERROR = 166
BS_TRDB_NODENAMELENERROR = 167
BS_TRDB_NODENAMEMISMATCH = 168
BS_TRDB_MAINKEYNOEXIST = 169
BS_TRDB_NOAUTHORITY_CREATESYSTEMKEY = 170
BS_TRDB_FINDMAINKEYEXCEPTION = 171
BS_TRDB_NOFINDMAINKEY = 172
BS_TRDB_NOFINDNODEPAGEFLAG = 173
BS_TRDB_OPENINDEXTREEFAILED = 174
BS_TRDB_SUBKEYALREADYEXIST = 175
BS_TRDB_NOFINDITEM = 176
BS_TRDB_UNKNOWNSUBKEYMODE = 177
BS_TRDB_INSERTINDEXTREEFAILED = BS_ERROR_INSERTBPTREE
BS_TRDB_NAMEISEMPTY = 179
BS_TRDB_PROPERTYALREADYEXIST = 180
BS_TRDB_PROPERTYNAMEALREADYEXIST = 181
BS_TRDB_DELETEINDEXTREEFAILED = 182
BS_TRDB_INDEXTREEROOTISNULL = 183
BS_TRDB_DELETEPROPERTY = 184
BS_TRDB_VISITNODEINDEXTREE = 185
BS_TRDB_FLAGUNKNOW = 186
BS_TRDB_PARSEDOTPATHFAILED = 187
BS_TRDB_PARSENODEPATHFAILED = 188
BS_TRDB_NOFINDTREEDBFILE = 189
BS_TRDB_CANNOTRENAMEMAINKEY = 190
BS_TRDB_CANNOTDELETEMAINKEY = 191
BS_TRDB_INDEXDATATYPEERROR = 200
BS_TRDB_NOSUPPORTINDEXTYPE = 201
BS_TRDB_NOFINDSEARCHKEYPARENTFLAG = 202
BS_TRDB_NOFINDINDEXROOTKEY = 203
BS_TRDB_CONFLICTWITHSYSTEMKEY = 204
BS_TRDB_NOFINDEXPRESSION = 205
BS_TRDB_DIFREENTDATATYPE = 206
BS_TRDB_CONDITIONERROR = 207
BS_TRDB_QUERYCONDITIONTYPEERROR = 208
BS_TRDB_NOFINDINDEXNODE = 209
BS_TRDB_NOFINDINDEXKEYFLAG = 211
BS_TRDB_NOFINDINDEXRNODERECORD = 212
BS_TRDB_NOFINDRECORDROOT = 213
BS_TRDB_NOFINDINDEXVALUENODEFLAG = 214
BS_TRDB_CALCULATEEXPRDATAERROR = 215
BS_TRDB_UNKNOWOPERATOR = 216
BS_TRDB_EXPRESSIONFORMAT = 217
BS_TRDB_EXPRESSIONDATACOUNTERROR = 218
BS_TRDB_NOSUPPORTDATATYPE = 219
BS_TRDB_CONVERTEXPRESSIONERROR = 220
BS_TRDB_UNKNOWCALCULATETYPE = 221
BS_TRDB_EXPRESSIONINDEXERROR = 222
BS_TRDB_ISNOTSEARCHKEYPARENT = 223

# ///////////////tabledb////////////////////////////////////////

BS_TBDB_NOINITIALIZATION = 260
BS_TBDB_USERALREADYEXIST = 261
BS_TBDB_INSERTINDEXTREEFAILED = BS_ERROR_INSERTBPTREE
BS_TBDB_DBALREADYEXIST = 263
BS_TBDB_NOFINDDB = 264
BS_TBDB_TABLEALREADYEXIST = 265
BS_TBDB_CREATEFIELDBUFFER = 266
BS_TBDB_UNKNOWNDATATYPE = 267
BS_TBDB_PRIMARYKEYWITHOUTUNIQUE = 268
BS_TBDB_PRIMARYREPEATASSIGN = 269
BS_TBDB_READFIELDHEAD = 270
BS_TBDB_FIELDFLAGERROR = 271
BS_TBDB_FIELDPOSERROR = 272
BS_TBDB_READFIELDINFOERROR = 273
BS_TBDB_FIELDTYPEERROR = 274
BS_TBDB_UNKNOWNFIELDTYPE = 275
BS_TBDB_DATALENGTHERROR = 276
BS_TBDB_WRITEFIELDINFOERROR = 277
BS_TBDB_CREATEINDEXTYPEERROR = 278
BS_TBDB_DYNPAGEERROR = 279
BS_TBDB_NOFINDTABLE = 280
BS_TBDB_GETTABLELOCKFAILED = 281
BS_TBDB_RECORDCBLENERROR = 282
BS_TBDB_RECORDPRIMARYKEYERROR = 283
BS_TBDB_SEEKPAGEPOSERROR = 284
BS_TBDB_INDEXERROR = 285
BS_TBDB_TABLECBLENERROR = 286
BS_TBDB_TABLEWASDELETED = 287
BS_TBDB_NOFINDRECORD = 288
BS_TBDB_CONDITIONERROR = 289
BS_TBDB_UNFIXEDFIELD = 290
BS_TBDB_RECORDSIZEERROR = 291
BS_TBDB_NOFINDFIELD = 292
BS_TBDB_FIELDCOUNTERROR = 293
BS_TBDB_STRLISTTOBUFFERERROR = BS_ERROR_STRLISTTOBUFFER
BS_TBDB_BUFFERTOSTRLISTERROR = BS_ERROR_BUFFERTOSTRLIST
BS_TBDB_NOFINDDYN = 296
BS_TBDB_NOTALERTINFO = 297
BS_TBDB_FIXEDRDSIZEERROR = 298
BS_TBDB_NOSUPPORTBINARYPRIMARYKEY = 299
BS_TBDB_NOSUPPORTBINARYINDEX = 300
BS_TBDB_FIELDSIZEERROR = 301
BS_TBDB_NOSUPPORTBINCONDITION = 302
BS_TBDB_DATABUFFERERROR = 303
BS_TBDB_CONTINUE = 304
BS_TBDB_END = 305

# ///////////////////////////////////////////////////////////////////////////

BSAPI_ERROR_PARAMETER = 1000
BSAPI_ERROR_CREATEOBJECT = 1001
BSAPI_ERROR_CONNECTSERVER = 1002
BSAPI_ERROR_ALLOCMEMORY = 1003
BSAPI_ERROR_NOSUPPORT_NETIOTYPE = 1004
BSAPI_ERROR_SENDDATA = 1005
BSAPI_ERROR_RECVDATA = 1006
BSAPI_ERROR_DATACHECK = 1007
BSAPI_ERROR_INVALIDHANDLE = 1008
BSAPI_ERROR_REOPENMQ = 1009
BSAPI_ERROR_SERIALDATA = 1010
BSAPI_ERROR_UNSERIALDATA = 1011
BSAPI_ERROR_DATAFORMAT = 1012
BSAPI_ERROR_CREATESTRINGLIST = 1013
BSAPI_ERROR_CREATESTRINGLISTBUFFER = 1014
BSAPI_ERROR_NOSUPPORT_DATATYPE = 1015
BSAPI_ERROR_FIELDDATA = 1016
BSAPI_ERROR_RECORDDATA = 1017
BSAPI_ERROR_PARSERECORDDATA = 1018
BSAPI_ERROR_ERRORHANDLE = 1019
BSAPI_ERROR_RECORDSET = 1020
BSAPI_CURSOR_END = 1021
BSAPI_CURSOR_BEGIN = 1022
BSAPI_ERROR_SESSIONCLOSED = 1023
BSAPI_ERROR_TRANHANDLEABORTED = 1024

error_dict = {
    40: '打开键失败',
    176: '找不到此属性',
    1005: '发送数据失败',
    1006: '接受数据失败',
    1007: '数据校验错误',
    1008: '无效的句柄',
    185: '数据库存入的类型与查询类型不匹配',
}

# C++调用异常
CODE_SUCCESS = 0
ERROR_CODE_PARAM = 1
ERROR_CODE_COMPANY = 2
ERROR_CODE_ALLOC = 3
ERROR_CODE_DB = 4
ERROR_CODE_USER = 5
ERROR_CODE_EXIST = 6
ERROR_CODE_DATATYPE = 7
ERROR_CODE_UNINIT = 8
ERROR_CODE_UNEXIST = 9
ERROR_CODE_MOREDATA = 10
ERROR_CODE_LIBRARY = 11
ERROR_CODE_EXCEPTION = 12
ERROR_CODE_NETWORK = 13
