from celery import Celery
import time
from app.common import Common

host = Common.get_config(Common.REDIS_CONFIG, 'REDIS_HOST')
port = int(Common.get_config(Common.REDIS_CONFIG, 'REDIS_PORT'))
password = Common.get_config(Common.REDIS_CONFIG, 'REDIS_PASSWORD')
db = int(Common.get_config(Common.REDIS_CONFIG, 'REDIS_DB'))
celery_app = Celery('tasks', broker=f'redis://:{password}@{host}:{port}/{db}')
task_logger = Common.get_app_logger('task')


@celery_app.task
def do_something():
    # 模拟一个耗时的任务
    time.sleep(10)



