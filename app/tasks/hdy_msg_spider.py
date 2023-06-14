import requests
import datetime
import pytz
import hashlib
from app.common import Common
from app.commons.redis_key import RedisKey
from app.models.stock_messages_model import StockMessageModel


class HdyMsgSpider:
    def __init__(self):
        self.keywords = ['CPO', '光模块', 'AMD', '英伟达', '公司']  # 关键字列表
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
        self.email = [
            # '749951152@qq.com',
            # '410317001@qq.com',
            # 'lishiye112233@163.com'
        ]
        self.content_type = 1  # 互动易平台
        self.redis = Common.get_global_redis()
        self.pool_key = RedisKey.MSG_POOL.format(self.content_type)
        self.logger = Common.get_app_logger('spider')

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
        for result in results:
            if not result.get('attachedContent'):
                self.logger.info(f'attachedContent为空，不处理：{result}')
                continue
            update_date = self.transform_timestamp_to_datetime(result['updateDate'])
            update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d %H:%M:%S')
            if (datetime.datetime.now() - update_date).days > 2:
                self.logger.info(f'更新时间超过48小时，不处理：{result}')
                continue

            self.logger.info(f'更新时间：{update_date}')
            self.handle_msg(result)

    def check_keywords(self, answer):
        for keyword in self.keywords:
            if keyword in answer:
                return keyword
        return False

    def get_data(self):
        data = {
            'pageNo': '1',
            'pageSize': '10',
            'searchTypes': '1,11',
            'highLight': 'true'
        }
        response = requests.post(self.url, headers=self.headers, data=data)
        data = response.json()['results']
        return data

    def check_and_add_msg(self, msg):
        """
        使用redis bitmap去重，如果已经存在，则返回1，否则返回0并写入
        """
        # 将消息转换为bitmap索引
        index = int(msg) % 2 ** 32
        # 检查索引是否存在
        if self.redis.getbit(self.pool_key, index) == 1:
            return 1
        # 如果索引不存在，则将其写入bitmap并返回0
        self.redis.setbit(self.pool_key, index, 1)
        return 0

    def handle_msg(self, msg):
        keyword = self.check_keywords(msg['attachedContent'])
        if keyword:
            self.logger.info(f'检测到关键字【{keyword}】')
            self.logger.info(f"Question: {msg['mainContent']}")
            self.logger.info(f"Answer: {msg['attachedContent']}")
            self.logger.info(f"updateDate: {self.transform_timestamp_to_datetime(msg['updateDate'])}")
            self.logger.info(f"pubDate:, {self.transform_timestamp_to_datetime(msg['pubDate'])}")
            self.logger.info(f"companyShortName: {msg['companyShortName']}")

            Common.send_email(f'【互动易】{keyword}相关消息提示', msg, self.email)
            self.logger.info('-----------------------------------')
            unkey = f"{self.content_type}_{msg['indexId']}"

            # 使用redis bitmap去重，如果已经存在，则返回1，否则返回0并写入
            if self.check_and_add_msg(unkey):
                self.logger.info(f'消息已存在，不处理：{unkey}')
                return

            msg_item = {
                'unkey': unkey,
                'content_type': self.content_type,
                'trade': msg['trade'],
                'main_content': f"【{msg['companyShortName']}】提问:{msg['mainContent']}回答:{msg['attachedContent']}".replace(
                    '\n', ''),
                'attached_content': '',
                'stock_code': msg.get('stockCode', ''),
                'sec_id': msg.get('secid', ''),
                'company': msg['companyShortName'],
                'board_type': msg['boardType'],
                'key_word': keyword,
                'update_date': self.transform_timestamp_to_datetime(msg['updateDate']),
                'pub_date': self.transform_timestamp_to_datetime(msg['pubDate']),
                'remind_status': 1
            }
            StockMessageModel.update_or_insert(Common.get_global_db_session(), msg_item)

            # 发送邮件
            email_content = f"【{msg['companyShortName']}】" \
                            f"\n行业:{msg['trade']}" \
                            f"\n提问:{msg['mainContent']}" \
                            f"\n提问:{msg['mainContent']}" \
                            f"\n回答:{msg['attachedContent']}"
            Common.send_email(f'【互动易】{keyword}相关消息提示', msg, self.email)


def main():
    spider = HdyMsgSpider()
    r = spider.get_data()
    spider.process_results(r)


if __name__ == '__main__':
    main()
