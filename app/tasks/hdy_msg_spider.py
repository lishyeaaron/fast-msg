import time
import random
import requests
import datetime
import pytz
from app.common import Common
from app.commons.redis_key import RedisKey
from app.models.stock_messages_model import StockMessageModel

logger = Common.get_app_logger('spider')


class HdyMsgSpider:
    def __init__(self):
        self.keywords = ['CPO', '光模块', 'AMD', '英伟达', '沙特']  # 关键字列表
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Pragma': 'no-cache',
            'sendType': 'formdata',
            'Origin': 'http://irm.cninfo.com.cn',
            'Connection': 'keep-alive',
            'Referer': 'http://irm.cninfo.com.cn/views/interactiveAnswer',
        }
        self.url = 'http://irm.cninfo.com.cn/newircs/index/search'

        self.content_type = 1  # 互动易平台
        self.redis = Common.get_global_redis()
        self.pool_key = RedisKey.MSG_POOL + str(self.content_type)
        self.logger = logger
        self.counts = {
            'total': 0,  # 总数
            'no_answer': 0,  # 未回复
            'expired': 0,  # 过期
            'target_amount': 0,  # 命中关键字总数
            'target_new': 0,  # 命中关键字新消息数
            'repeat_redis': 0,  # 重复消息数redis记录
            'repeat_db': 0,  # 重复消息数db记录
        }

    @staticmethod
    def transform_timestamp_to_datetime(timestamp):
        if isinstance(timestamp, int):
            timestamp = str(timestamp)
        if len(timestamp) == 13:
            timestamp = int(timestamp) / 1000
        elif len(timestamp) == 10:
            timestamp = int(timestamp)
        else:
            raise ValueError(f"timestamp格式错误：{timestamp}")

        dt = datetime.datetime.fromtimestamp(timestamp, pytz.timezone('Asia/Shanghai'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def process_results(self, results):
        if not results:
            return
        for result in results:
            if not result.get('attachedContent'):
                self.logger.debug(f'attachedContent为空，不处理：{result}')
                self.counts['no_answer'] += 1
                continue
            update_date = self.transform_timestamp_to_datetime(result['updateDate'])
            update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d %H:%M:%S')
            # print(f'日期差距为{(datetime.datetime.now() - update_date).days}')
            if (datetime.datetime.now() - update_date).days >= 1:
                self.counts['expired'] += 1
                self.logger.debug(f'更新时间超过48小时，不处理：{result}')
                continue

            self.logger.debug(f'更新时间：{update_date}')
            self.handle_msg(result)

    def check_keywords(self, answer):
        for keyword in self.keywords:
            if keyword in answer:
                return keyword
        return False

    def run(self):
        params = {
            'pageNo': '1',
            'pageSize': '50',
            'searchTypes': '1,11',
        }
        for i in range(1, 50):
            params['pageNo'] = str(i)
            response = requests.post(self.url, headers=self.headers, data=params)

            try:
                data = response.json()['results']
                self.counts['total'] = len(data)
                self.process_results(data)

            except (Exception,) as e:
                self.logger.error(f"状态码：{response.status_code}")
                self.logger.error(f"返回内容：{response.text}")
                self.logger.error(f'获取数据失败：{e}')
                return []
            self.logger.debug(self.counts)
            self.counts = {
                'total': 0,  # 总数
                'no_answer': 0,  # 未回复
                'expired': 0,  # 过期
                'target_amount': 0,  # 命中关键字总数
                'target_new': 0,  # 命中关键字新消息数
                'repeat_redis': 0,  # 重复消息数redis记录
                'repeat_db': 0,  # 重复消息数db记录
            }
            time.sleep(random.randint(1, 3))

    def check_and_add_msg(self, msg):
        """
        使用 Redis Sorted Set 进行去重和清理，如果已经存在，则返回1，否则返回0并写入
        """
        # 使用 Redis 的事务机制优化多个命令的执行
        pipeline = self.redis.pipeline()

        # 将时间戳转换为整数形式的字符串
        timestamp = str(int(time.time()))

        # 检查消息是否存在于 Sorted Set 中
        pipeline.zscore(self.pool_key, msg)

        # 将消息写入 Sorted Set，使用当前时间作为分数
        pipeline.zadd(self.pool_key, {msg: timestamp})

        # 获取当前 Sorted Set 中的元素数量
        pipeline.zcard(self.pool_key)

        # 执行事务
        results = pipeline.execute()

        if results[0] is not None:
            self.logger.debug(f'Redis中消息已存在，不处理：{msg}')
            return 1

        if results[2] > 2000:
            # 清理三天前的数据并修剪 Sorted Set
            pipeline.zremrangebyscore(self.pool_key, '-inf', time.time() - (3 * 24 * 60 * 60))
            pipeline.zremrangebyrank(self.pool_key, 0, -2000)

        # 设置过期时间
        pipeline.expire(self.pool_key, 60 * 60 * 24 * 3)

        # 执行事务
        pipeline.execute()

        return 0

    def handle_msg(self, msg):
        keyword = self.check_keywords(msg['attachedContent'])
        if keyword:
            self.counts['target_amount'] += 1
            unkey = f"{self.content_type}_{msg['indexId']}"

            # 使用redis bitmap去重，如果已经存在，则返回1，否则返回0并写入
            if self.check_and_add_msg(unkey):
                self.counts['repeat_redis'] += 1
                return

            db_session = Common.get_global_db_session()
            item = StockMessageModel.find_by_unkey(db_session, unkey)
            if item:
                self.counts['repeat_db'] += 1
                self.logger.debug(f'数据库消息已存在，不处理：{unkey}')
                return
            self.logger.debug(f'检测到关键字【{keyword}】')
            self.logger.debug(f"Question: {msg['mainContent']}")
            self.logger.debug(f"Answer: {msg['attachedContent']}")
            self.logger.debug(f"updateDate: {self.transform_timestamp_to_datetime(msg['updateDate'])}")
            self.logger.debug(f"pubDate:, {self.transform_timestamp_to_datetime(msg['pubDate'])}")
            self.logger.debug(f"companyShortName: {msg['companyShortName']}")
            self.logger.debug('-----------------------------------')
            self.counts['target_new'] += 1
            msg_item = {
                'unkey': unkey,
                'content_type': self.content_type,
                'trade': msg['trade'],
                'main_content': msg['mainContent'],
                'attached_content': msg['attachedContent'],
                'stock_code': msg.get('stockCode', ''),
                'sec_id': msg.get('secid', ''),
                'company': msg['companyShortName'],
                'board_type': msg['boardType'],
                'key_word': keyword,
                'update_date': self.transform_timestamp_to_datetime(msg['updateDate']),
                'pub_date': self.transform_timestamp_to_datetime(msg['pubDate']),
                'remind_status': 0
            }
            StockMessageModel.update_or_insert(db_session, msg_item)


if __name__ == '__main__':
    while True:
        spider = HdyMsgSpider()
        spider.run()
        time.sleep(10)
