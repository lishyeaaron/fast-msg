import time

import schedule
from app.tasks.hdy_msg_spider import HdyMsgSpider
from app.common import Common

logger = Common.get_app_logger('schedule')


def hdy_task():
    """
    互动易定时任务
    :return:
    """
    HdyMsgSpider().run()


def run_schedule():
    # 在6点到23点之间，每隔1分钟执行一次
    schedule.every().day.at("06:00").until("23:00").minutes.do(hdy_task)

    while True:
        time.sleep(10)
        schedule.run_pending()


if __name__ == '__main__':
    hdy_task()
