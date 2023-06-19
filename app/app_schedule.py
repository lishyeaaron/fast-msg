import time

import schedule
from app.tasks.hdy_msg_spider import HdyMsgSpider
from app.tasks.remind_msg import remind_msg
from app.common import Common

logger = Common.get_app_logger('schedule')


def hdy_task():
    """
    互动易定时任务
    :return:
    """
    current_hour = time.localtime().tm_hour
    if 6 <= current_hour <= 23:
        HdyMsgSpider().run()


def remind_task():
    """
    消息提醒定时任务
    :return:
    """
    current_hour = time.localtime().tm_hour
    if 6 <= current_hour <= 23:
        remind_msg()


def run_schedule():
    # 在6点到23点之间，每隔n分钟执行一次
    schedule.every(3).minutes.do(hdy_task)

    # 在6点到23点之间每n分钟执行消息提醒
    schedule.every(3).minutes.do(remind_task)

    while True:
        time.sleep(3)
        schedule.run_pending()


if __name__ == '__main__':
    hdy_task()
