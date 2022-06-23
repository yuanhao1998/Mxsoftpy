# -*- coding: UTF-8 -*-
# @Create   : 2021/5/11 11:14 上午
# @Author   : yh
# @Remark   : 在此定义所有的消息队列操作方式

# 定义所有打开方式
BSMQ_OF_OPENEXIST = 0x00000001  # 打开已存在的mq
BSMQ_OF_CREATENEW = 0x00000002  # 创建新的mq
BSMQ_OF_OPENMULTI = 0x00000004

# 定义创建mq的风格
BSMQ_OT_COMMONMQ = 0x01  # 普通队列
BSMQ_OT_PRIORITYMQ = 0x02  # 优先队列
BSMQ_OT_TEMPMQ = 0x04
BSMQ_OT_ENCRYPT = 0x08
BSMQ_OT_INDEXRECORD = 0x10

BS_MQ_MAXNAME = 100
BS_MQ_MAXPWD = 20

# 表示最多支持多少个优先级
BS_MQ_MAXPRIORITY = 9
# 普通优先级
BS_MQ_COMMONPRIORITY = (BS_MQ_MAXPRIORITY / 2 + 1)

BS_MQ_MAXRECORDID = 30

# 从mq取数的等待时间设置为无限等待
BS_TIMER_INFINITE = 0xFFFFFFFF
