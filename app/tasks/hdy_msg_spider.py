import time

import requests
import datetime
import pytz
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
        for result in results:
            if not result.get('attachedContent'):
                self.logger.debug(f'attachedContent为空，不处理：{result}')
                self.counts['no_answer'] += 1
                continue
            update_date = self.transform_timestamp_to_datetime(result['updateDate'])
            update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d %H:%M:%S')
            if (datetime.datetime.now() - update_date).days >= 1:
                self.counts['expired'] += 1
                self.logger.debug(f'更新时间超过48小时，不处理：{result}')
                continue

            self.logger.debug(f'更新时间：{update_date}')
            self.handle_msg(result)
        self.logger.info(f'总数：{self.counts["total"]}')
        self.logger.info(f'未回复：{self.counts["no_answer"]}')
        self.logger.info(f'过期：{self.counts["expired"]}')
        self.logger.info(f'命中关键字总数：{self.counts["target_amount"]}')
        self.logger.info(f'命中关键字新消息数：{self.counts["target_new"]}')
        self.logger.info(f'重复消息数redis记录：{self.counts["repeat_redis"]}')
        self.logger.info(f'重复消息数db记录：{self.counts["repeat_db"]}')

    def check_keywords(self, answer):
        for keyword in self.keywords:
            if keyword in answer:
                return keyword
        return False

    def get_data(self):
        data = {
            'pageNo': '1',
            'pageSize': '100',
            'searchTypes': '1,11',
            'highLight': 'true'
        }
        response = requests.post(self.url, headers=self.headers, data=data)
        data = response.json()['results']
        self.counts['total'] = len(data)
        return data

    def check_and_add_msg(self, msg):
        """
        使用redis bitmap去重，如果已经存在，则返回1，否则返回0并写入
        """
        # 将消息转换为bitmap索引
        index = int(msg) % 2 ** 32
        # 检查索引是否存在
        if self.redis.getbit(self.pool_key, index) == 1:
            self.logger.debug(f'redis中消息已存在，不处理：{msg}')
            return 1
        # 如果索引不存在，则将其写入bitmap并返回0
        self.redis.setbit(self.pool_key, index, 1)
        # 设置过期时间
        self.redis.expire(self.pool_key, 60 * 60 * 24 * 7)
        return 0

    def handle_msg(self, msg):
        keyword = self.check_keywords(msg['attachedContent'])
        if keyword:
            self.counts['target_amount'] += 1

            unkey = f"{self.content_type}_{msg['indexId']}"

            # 使用redis bitmap去重，如果已经存在，则返回1，否则返回0并写入
            if not self.check_and_add_msg(unkey):
                self.counts['repeat_redis'] += 1
                db_session = Common.get_global_db_session()
                item = StockMessageModel.find_by_unkey(db_session, unkey)
                if item:
                    self.counts['repeat_db'] += 1
                    self.logger.info(f'数据库消息已存在，不处理：{unkey}')
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
                StockMessageModel.update_or_insert(db_session, msg_item)

                # 发送邮件
                email_content = f"【{msg['companyShortName']}】" \
                                f"\n行业:{msg['trade']}" \
                                f"\n提问:{msg['mainContent']}" \
                                f"\n回答:{msg['attachedContent']}"
                Common.send_email(f'【互动易】《{keyword}》相关消息提示', email_content, self.email)


def main():
    spider = HdyMsgSpider()
    r = spider.get_data()
    spider.process_results(r)
    print(spider.counts)


if __name__ == '__main__':
    main()
