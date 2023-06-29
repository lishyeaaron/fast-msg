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
    if 7 <= current_hour <= 23:
        logger.info(f'当前时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}, 开始执行互动易定时任务')
        HdyMsgSpider().run()
    else:
        logger.info(
            f'当前时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}, 不在7点到23点之间，不执行互动易定时任务')


def remind_task():
    """
    消息提醒定时任务
    :return:
    """
    current_hour = time.localtime().tm_hour

    if 7 <= current_hour <= 23:
        logger.info(f'当前时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}, 开始执行消息提醒定时任务')
        remind_msg()
    else:
        logger.info(
            f'当前时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}, 不在7点到23点之间，不执行消息提醒定时任务')


def run_schedule():
    # 每隔n分钟执行一次
    schedule.every(3).minutes.do(hdy_task)

    # 在6点到23点之间每n分钟执行消息提醒
    schedule.every(1).minutes.do(remind_task)

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
