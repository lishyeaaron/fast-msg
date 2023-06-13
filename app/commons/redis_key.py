# -*- coding: utf-8 -*-


class RedisKey(object):
    TASK_LIST = ''  # 任务列表
    EVENT_STAT = 'event_stat:%s%s'  # 事件状态
    DING_ACCESS_TOKEN = 'ding_access_token'  # 钉钉token
    DING_TASK = 'ding_task:%s'  # 钉钉任务
    UPDATED_DING_TASKID_SET = 'updated_ding_task_set'  # 更新过的钉钉任务id集合
    SSH_SWITCH = 'ssh_switch:%s'  # ssh开关
