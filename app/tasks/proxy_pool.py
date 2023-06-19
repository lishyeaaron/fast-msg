import time
import requests
import re
from app.common import Common
from app.commons.redis_key import RedisKey


class ProxyIPPool:
    def __init__(self):
        self.redis = Common.get_global_redis()
        self.pool_key = RedisKey.PROXY_POOL
        self.proxy_url = 'http://www.66ip.cn/mo.php?sxb=&tqsl=10&port=&export=&ktip=&sxa=&submit=查询'

    def get_proxy_ip(self):
        ip = self.redis.srandmember(self.pool_key)
        if ip is None:
            self.update_proxy_pool()
            ip = self.redis.srandmember(self.pool_key)
        return ip

    def release_proxy_ip(self, ip):
        self.redis.srem(self.pool_key, ip)

    @staticmethod
    def test_proxy(ip):
        try:
            proxies = {
                'http': f'http://{ip}',
                'https': f'http://{ip}'
            }
            print(proxies)
            response = requests.get('http://ifconfig.me', proxies=proxies, timeout=5)
            print(response.text)
            print(response.status_code)
            print(response.content)

            return response.status_code == 200
        except (requests.exceptions.RequestException, ValueError) as e:
            print(e)
            return False

    def update_proxy_pool(self):
        response = requests.get(self.proxy_url)
        if response.status_code == 200:
            html = response.text
            proxy_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{2,5}\b')
            proxies = re.findall(proxy_pattern, html)

            for proxy in proxies:
                if self.test_proxy(proxy):
                    self.redis.sadd(self.pool_key, proxy)

        else:
            raise ValueError(f"获取代理IP失败：{response.text}")

    def maintain_min_pool_size(self, min_size=5):
        current_size = self.redis.scard(self.pool_key)
        if current_size < min_size:
            num_to_add = min_size - current_size
            for _ in range(num_to_add):
                self.update_proxy_pool()
                time.sleep(1)  # Delay between adding each proxy to avoid rate limiting


p = ProxyIPPool()
ip = p.get_proxy_ip()
test_result = p.test_proxy(ip)
print(test_result)

print(ip)
