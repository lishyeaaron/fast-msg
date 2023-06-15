# -*- coding: utf-8 -*-
from retrying import retry
import requests
from app.common import Common

logger = Common.get_app_logger('stock_service')


class StockService:
    licence = Common.get_config(Common.STOCK_CONFIG, 'LICENCE')
    base_url = 'https://ig507.com/data'

    def __init__(self):
        ...

    @staticmethod
    @retry(wait_fixed=1000, stop_max_attempt_number=3)
    def query(url, method='GET', params=None, data=None, json=None, headers=None, ignore_error=False):
        if url.startswith('/'):
            url = f"{StockService.base_url}{url}"
        else:
            url = f"{StockService.base_url}/{url}"

        try:
            if params:
                params.append(('licence', StockService.licence))
            if method == 'GET':
                response = requests.get(url=url, params=params, headers=headers)
            elif method == 'POST':
                response = requests.post(url=url, data=data, json=json, headers=headers)
            else:
                response = None
                logger.error(f'请求方式错误:{method}')
            if response.status_code == 200:
                return True, response.json()
            else:
                if ignore_error:
                    return False, response.json()
                else:
                    logger.error(f'请求失败:{response.text}')
                    raise Exception(response.json())
        except Exception as e:
            if ignore_error:
                return False, str(e)
            else:
                raise


class StockBaseService(StockService):

    def base_info(self, code):
        url = f"time/f10/info/{code}"
        return self.query(url)

    def gplist(self):
        url = 'base/gplist'
        return self.query(url)

    def gp_info(self, code):
        url = f"time/f10/info/{code}"
        return self.query(url)

    def gp_gonggao_zdsx(self, code):
        """
        股票公告重大事项
        """
        url = f"time/gonggao/zdsx/{code}"
        return self.query(url)

    def gp_gonggao_cwbg(self, code):
        """
        股票公告财务报告
        """
        url = f"time/gonggao/cwbg/{code}"
        return self.query(url)

    def gp_gonggao_rzgg(self, code):
        """
        股票公告融资公告
        """
        url = f"time/gonggao/rzgg/{code}"
        return self.query(url)

    def gp_gonggao_fxts(self, code):
        """
        股票公告风险提示
        """
        url = f"time/gonggao/fxts/{code}"
        return self.query(url)

    def gp_gonggao_zccz(self, code):
        """
        股票公告资产重组
        """
        url = f"time/gonggao/zccz/{code}"
        return self.query(url)

    def gp_gonggao_xxbg(self, code):
        """
        股票公告信息变更
        """
        url = f"time/gonggao/xxbg/{code}"
        return self.query(url)

    def gp_gonggao_cgbd(self, code):
        """
        股票公告持股变动
        """
        url = f"time/gonggao/cgbd/{code}"
        return self.query(url)

    def gp_history_gonggao(self, code):
        """
        股票历史公告
        """
        url = f"time/history/gonggao/{code}"
        return self.query(url)


if __name__ == '__main__':
    gp = StockBaseService().gp_info('000001')
    print(gp)
    gp = StockBaseService().gp_gonggao_zdsx('000001')
    print(gp)
    gp = StockBaseService().gp_gonggao_cwbg('000001')
    print(gp)
    gp = StockBaseService().gp_gonggao_rzgg('000001')
    print(gp)
    gp = StockBaseService().base_info('000001')
    print(gp)
