# -*- coding: utf-8 -*-
import os
import redis
import requests
import json
import configparser
from retrying import retry
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logging import handlers
import logging
from app.utils.storage import Storage
from app.utils.email_sender import EmailSender


class Common:
    WORK_PATH = os.path.dirname(os.path.abspath(__file__))
    CONFIG_FILE = 'Config.cfg'
    PROJECT_CONFIG = 'PROJECT_CONFIG'
    MYSQL_CONFIG = 'MYSQL_CONFIG'
    REDIS_CONFIG = 'REDIS_CONFIG'
    EMAIL_CONFIG = 'EMAIL_CONFIG'
    DINGDING_CONFIG = 'DINGDING_CONFIG'
    WECHAT_CONFIG = 'WECHAT_CONFIG'
    OPENAI_CONFIG = 'OPENAI_CONFIG'
    STOCK_CONFIG = 'STOCK_CONFIG'
    DING_TODO_APP_CONFIG = 'DING_TODO_APP_CONFIG'
    REDIS_CONNECTION = None
    MYSQL_ENGINE = None
    APP_LOG = {}
    SYS_LOG = None

    @staticmethod
    def get_config(section, name, default=''):
        """
        读取配置文件
        :param section:
        :param name:
        :param default
        :return:
        """
        cf = default
        Common.CONFIG_FILE = Storage.join_path(Common.WORK_PATH, Common.CONFIG_FILE)
        if not Storage.has(Common.CONFIG_FILE):
            print(Common.CONFIG_FILE)
            raise Exception('配置不存在')
        config = configparser.RawConfigParser()
        config.read(Common.CONFIG_FILE, encoding='gbk')
        # 第一个参数指定要读取的段名，第二个是要读取的选项名
        cf = config.get(section, name) if config.get(section, name) else cf
        return cf

    @staticmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2)
    def get_global_db():
        """
        获取数据库连接
        :return: connection
        """
        print('获取数据库连接')
        if Common.MYSQL_ENGINE:
            try:
                conn = Common.MYSQL_ENGINE.connect()
                conn.execute(select(1))  # 检查连接对象是否有效
            except DBAPIError:
                Common.MYSQL_ENGINE.dispose()
                Common.MYSQL_ENGINE = None
            except Exception:
                Common.MYSQL_ENGINE = None
        else:
            db_url = 'mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'
            db_url = db_url.format(
                user=Common.get_config(Common.MYSQL_CONFIG, 'MYSQL_USER'),
                password=Common.get_config(Common.MYSQL_CONFIG, 'MYSQL_PASSWORD'),
                host=Common.get_config(Common.MYSQL_CONFIG, 'MYSQL_HOST'),
                port=Common.get_config(Common.MYSQL_CONFIG, 'MYSQL_PORT'),
                database=Common.get_config(Common.MYSQL_CONFIG, 'MYSQL_DB')
            )
            print(
                db_url
            )
            Common.MYSQL_ENGINE = create_engine(db_url, pool_pre_ping=True, echo=True,pool_size=20, max_overflow=0)
            try:
                conn = Common.MYSQL_ENGINE.connect()
                print(conn.execute(select(1)))  # 检查连接对象是否有效
            except DBAPIError as e:

                Common.MYSQL_ENGINE.dispose()
                Common.MYSQL_ENGINE = None
            except Exception as e:

                Common.MYSQL_ENGINE = None

        if Common.MYSQL_ENGINE is None:
            raise Exception('无法连接到数据库')
        return Common.MYSQL_ENGINE

    @staticmethod
    def get_global_db_session():
        db = Common.get_global_db()
        db_session = sessionmaker(bind=db)()
        return db_session

    @staticmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2)
    def get_global_redis():
        if Common.REDIS_CONNECTION is None:
            print('获取redis连接')
            print(Common.get_config(Common.REDIS_CONFIG, 'REDIS_HOST'))
            print(Common.get_config(Common.REDIS_CONFIG, 'REDIS_PASSWORD'))
            Common.REDIS_CONNECTION = redis.Redis(
                host=Common.get_config(Common.REDIS_CONFIG, 'REDIS_HOST'),
                port=int(Common.get_config(Common.REDIS_CONFIG, 'REDIS_PORT')),
                password=Common.get_config(Common.REDIS_CONFIG, 'REDIS_PASSWORD'),
                db=int(Common.get_config(Common.REDIS_CONFIG, 'REDIS_DB')),
                decode_responses=True,
                retry_on_timeout=True,
            )

        try:
            Common.REDIS_CONNECTION.ping()
        except Exception as e:
            Common.REDIS_CONNECTION = None
            raise Exception('Redis连接失败{}'.format(str(e)))
        return Common.REDIS_CONNECTION

    @staticmethod
    def get_app_logger(app_name='app'):
        if isinstance(Common.APP_LOG, dict) and app_name in Common.APP_LOG.keys():
            return Common.APP_LOG[app_name]
        logger = logging.getLogger(app_name)
        logger.setLevel(logging.DEBUG)
        log_path = f"/var/log/fast-msg"
        Storage.check_or_mkdir(log_path)
        log_file = f'{log_path}/{app_name}.log'
        fh = logging.handlers.TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=7, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        Common.APP_LOG[app_name] = logger
        return logger

    @staticmethod
    def get_sys_logger():
        if Common.APP_LOG is not None:
            return Common.APP_LOG
        logger = logging.getLogger('sys')
        logger.setLevel(logging.INFO)
        log_path = f"/var/log/fast-msg"
        Storage.check_or_mkdir(log_path)
        log_file = f'{log_path}/sys.log'
        fh = logging.handlers.TimedRotatingFileHandler(log_file, when='D', interval=1, backupCount=7, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        Common.APP_LOG = logger
        return Common.APP_LOG

    @staticmethod
    def send_email(title, content, address):
        """
        发送邮件
        :param title:
        :param content:
        :param address:
        :return:
        """
        m = EmailSender(
            email_host=Common.get_config(Common.EMAIL_CONFIG, 'EMAIL_HOST'),
            username=Common.get_config(Common.EMAIL_CONFIG, 'EMAIL_USER'),
            passwd=Common.get_config(Common.EMAIL_CONFIG, 'EMAIL_PASS'),
            port=Common.get_config(Common.EMAIL_CONFIG, 'EMAIL_PORT'),
            recv=address,
            title=title,
            content=content,
            file=None,
        )
        m.send_mail()

    @staticmethod
    def send_ding_msg(content, msg_type='MSG'):
        """
        发送钉钉消息
        :param content:
        :param msg_type:
        :return:
        """
        print(f'发送钉钉消息{content} {msg_type}')
        # 通知钉钉 机器人
        url = Common.get_config(Common.DINGDING_CONFIG, 'URL')
        if msg_type == 'MSG':
            msg_header = '【资讯】'
            access_token = Common.get_config(Common.DINGDING_CONFIG, 'MSG_ACCESS_TOKEN')
        elif msg_type == 'ALERT':
            msg_header = '【告警】'
            access_token = Common.get_config(Common.DINGDING_CONFIG, 'ALARM_ACCESS_TOKEN')
        else:
            raise Exception('钉钉消息类型错误')
        # Define the URL and access token for the DingTalk robot
        url = f'{url}?access_token={access_token}'

        # Define the message content
        msg = {
            "msgtype": "text",
            "text": {
                "content": f'{msg_header}{content}'
            }
        }
        try:

            # Convert the message to a JSON string
            json_msg = json.dumps(msg)

            # Send the message to the DingTalk robot using HTTP POST request
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json_msg)

            # Check the response status code
            if response.status_code == 200 and response.json()['errcode'] == 0:
                print('Message sent successfully!')
                print(response.text)
                return True
            else:
                print(f'Error {response.status_code}: {response.text}')
                return False
        except Exception as e:
            print(e)
        return False


if __name__ == "__main__":
    r = Common.get_global_redis()
    r.ping()
