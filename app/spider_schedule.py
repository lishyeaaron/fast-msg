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
    if 5 <= current_hour <= 23:
        HdyMsgSpider().run()


def run_schedule():
    # 每隔n分钟执行一次
    schedule.every(1).minutes.do(hdy_task)

    while True:
        time.sleep(3)
        try:
            schedule.run_pending()
        except KeyboardInterrupt as e:
            logger.exception(e)
            break
        except Exception as e:
            logger.exception(e)
            continue


if __name__ == '__main__':
    hdy_task()
