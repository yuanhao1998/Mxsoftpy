# -*- coding: UTF-8 -*-
# @Create   : 2021/5/11 11:14 上午
# @Author   : yh
# @Remark   : 在此定义所有的tree数据库操作方式

#################### OpenKey flag###############################
TRDB_OPKF_CREATEMAINKEY = 0x00010000
TRDB_OPKF_DELETEMAINKEY = 0x00020000
TRDB_OPKF_RENAME = 0x00040000
TRDB_OPKF_OPENEXIST = 0x00080000

TRDB_OPKF_READONLY = 0x00000001
TRDB_OPKF_SYSTEMKEY = 0x00000002
TRDB_OPKF_HIDE = 0x00000004
TRDB_OPKF_SEARCHKEY_PARENT = 0x00000008
TDDB_OPKF_CREATEDYNKEY = 0x00000100

TRDB_OPKF_OPENCHILD = 0x00000010
TRDB_OPKF_DOTPATH = 0x00000080
#####################################################################

BS_TRDB_DOTSEPARATOR = "."
BS_TRDB_NODESEPARATOR = "\\"

BS_TRDB_MAXFILENAME = 30
BS_TRDB_MAXSUBKEYPATH = 2048

BS_TRDB_MAXMAINKYELEN = 38
BS_TRDB_MAXNODENAELEN = 800
BS_TRDB_MAXRECORDNAMELEN = 800

BS_TRDB_MAXPWD = 30

#######################Insert key#################################

# TreeDB数据库的一些标志位
# 指示使用双向链式子键
BS_TRDB_FLAG_LINKNODE = 0x00000001
# 指示使用索引子键
BS_TRDB_FLAG_INDEXNODE = 0x00000002
# 指未使用双向链式属性
BS_TRDB_FLAG_LINKRECORD = 0x00000004
# 指示使用索引式属性
BS_TRDB_FLAG_INDEXRECORD = 0x00000008
# 指示使用双向链式主键
BS_TRDB_FLAG_LINKMAINNODE = 0x00000020
# 指示使用索引式主键
BS_TRDB_FLAG_INDEXMAINNODE = 0x00000040
######################################################################


###################################键索引类型#############################
# 设置此标志指示此列所建的索引为降序，否则为升序
BS_RITF_INDEX_DESC = 0x0020
"""
c++
struct bs_recordindextype
{
	i8 name[BS_TRDB_MAXRECORDNAMELEN];
	i8 uType;
	//设置此标志指示此列所建的索引为降序，否则为升序
#define BS_RITF_INDEX_DESC			0x0020
	ui16 uFlag;

};
python
bs_recordindextypes = []
bs_recordindextype = {"name": "age", "uType": VDT_I32, "uFlag": BS_RITF_INDEX_DESC}
bs_recordindextypes.append(bs_recordindextype)

"""

BS_RDT_LEN = (3 + BS_TRDB_MAXRECORDNAMELEN)

#######################################################
"""
c++
struct bs_query_item
{
	i8 name[BS_TRDB_MAXRECORDNAMELEN];
	i8 nCondition;
	chen::VariableData vLiData;
	chen::VariableData vEnd;

};
python
bs_query_items = []
bs_query_item = {"name": "_port", "nCondition": TRDB_FMC_EQUAL, "vLiData": "161", "vEnd": ""}
bs_query_items.append(bs_query_item)
"""

###########################bs_query_item:nCondition###############################

# 按属性查询时可用的查询条件
TRDB_FMC_GREATERTHAN = 0x01
TRDB_FMC_LESSTHAN = 0x02
TRDB_FMC_EQUAL = 0x03
TRDB_FMC_EQUALORGREATERTHAN = 0x04
TRDB_FMC_EQUALORLESSTHAN = 0x05
TRDB_FMC_UNEQUAL = 0x06
# 支持字符串通配符查询
TRDB_FMC_LIKE = 0x07
# 支持通配符查询不区分大小写
TRDB_FMC_NOCASE_LIKE = 0x08
TRDB_FMC_RANGE = 0x09
TRDB_FMC_IN = 0x0A

############################################################################

TRDB_QOTT_OR = 0x2
TRDB_QOTT_AND = 0x3

###########################Calculate type####################################

TRDB_CALCTYPE_COUNT = 0x01
TRDB_CALCTYPE_SUM = 0x02
TRDB_CALCTYPE_AVERAGE = 0x03
TRDB_CALCTYPE_MAX = 0x04
TRDB_CALCTYPE_MIN = 0x05

##############################################################################
