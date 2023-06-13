import requests

url = 'http://irm.cninfo.com.cn/newircs/index/search'
headers = {
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
data = {
    'pageNo': '1',
    'pageSize': '10',
    'searchTypes': '1,11',
    'highLight': 'true'
}

response = requests.post(url, headers=headers, data=data)
results = response.json()['results']

for result in results:
    print('Question:', result['mainContent'])
    print('Answer:', result['attachedContent'])
    print('---')
