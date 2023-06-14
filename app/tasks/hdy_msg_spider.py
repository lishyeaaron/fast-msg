import requests
import datetime
import pytz
import hashlib
from app.common import Common
from app.commons.redis_key import RedisKey
from app.models.stock_messages_model import StockMessageModel


class HdyMsgSpider:
    def __init__(self):
        self.keywords = ['CPO', '光模块', 'AMD', '英伟达']  # 关键字列表
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
            '749951152@qq.com',
            # '410317001@qq.com',
            # 'lishiye112233@163.com'
        ]
        self.content_type = 1  # 互动易平台
        self.redis = Common.get_global_redis()
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
                print(result)
                continue
            update_date = self.transform_timestamp_to_datetime(result['updateDate'])
            update_date = datetime.datetime.strptime(update_date, '%Y-%m-%d %H:%M:%S')
            if (datetime.datetime.now() - update_date).days > 0.5:
                print(f'更新时间超过24小时，不处理：{result}')
                # continue

            print(f'更新时间：{update_date}')

            # msg = f"【{result['companyShortName']}】\n提问:{result['mainContent']}\n回答:{result['attachedContent']}\n更新时间:{update_date}"
            msg = f"【{result['companyShortName']}】\n提问:{result['mainContent']}\n回答:{result['attachedContent']}"
            # print(msg)
            keyword = self.check_keywords(result['attachedContent'])
            if keyword:
                print(f'检测到关键字【{keyword}】')
                print('Question:', result['mainContent'])
                print('Answer:', result['attachedContent'])
                print('updateDate:', self.transform_timestamp_to_datetime(result['updateDate']))
                print('pubDate:', self.transform_timestamp_to_datetime(result['pubDate']))
                print('companyShortName:', result['companyShortName'])

                Common.send_email(f'【互动易】{keyword}相关消息提示', msg, self.email)
                print('-----------------------------------')

    def check_keywords(self, answer):
        for keyword in self.keywords:
            if keyword in answer:
                return keyword
        return False

    def get_data(self):
        data = {
            'pageNo': '1',
            'pageSize': '50',
            'searchTypes': '1,11',
            'highLight': 'true'
        }
        response = requests.post(self.url, headers=self.headers, data=data)
        data = response.json()['results']
        return data

    def handle_msg(self, msg, keyword):
        content = f"【{msg['companyShortName']}】\n提问:{msg['mainContent']}\n回答:{msg['attachedContent']}"
        # unkey 为唯一标识，用于去重，将self.content_type和msg['indexId'] 取16位

        m = hashlib.md5()
        m.update(f"{self.content_type}{msg['indexId']}".encode('utf-8'))
        unkey = m.hexdigest()

        # 使用redis bitmap去重，如果已经存在，则返回1，否则返回0并写入
        if self.redis.getbit(RedisKey.CNINFO_MSG, unkey):
            return
        self.redis.setbit(RedisKey.CNINFO_MSG, unkey, 1)


        # self.redis.lpush('cninfo', content)
        msg_item = {
            'unkey': unkey,
            'content_type': self.content_type,
            'trade': msg['trade'],
            'main_content': content,
            'attached_content': '',
            'stock_code': msg['stockCode'],
            'sec_id': msg['secId'],
            'company': msg['companyShortName'],
            'board_type': msg['boardType'],
            'key_word': keyword,
            'update_date': msg['updateDate'],
            'pub_date': msg['pubDate'],
            'remind_status': 1
        }
        StockMessageModel.update_or_insert(msg_item)


def main():
    spider = HdyMsgSpider()
    r = spider.get_data()
    spider.process_results(r)


if __name__ == '__main__':
    main()