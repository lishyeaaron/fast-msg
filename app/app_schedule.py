# 定时任务模块 schedule.py
import time

import schedule
from app.common import Common

logger = Common.get_app_logger('schedule')


def sentry_undo_report():
    """
    未完成任务汇总
    :return:
    """
    ...


def run_schedule():
    schedule.every(20).minute.do(sentry_undo_report)

    while True:
        time.sleep(10)
        schedule.run_pending()


if __name__ == '__main__':
    sentry_undo_report()
