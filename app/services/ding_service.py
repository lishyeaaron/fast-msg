# -*- coding: utf-8 -*-
import requests
import json
import hashlib
from sqlalchemy.orm import sessionmaker
from alibabacloud_dingtalk.oauth2_1_0.client import Client as dingtalkoauth2_1_0Client
from alibabacloud_dingtalk.oauth2_1_0 import models as dingtalkoauth_2__1__0_models
from alibabacloud_dingtalk.robot_1_0.client import Client as dingtalkrobot_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.robot_1_0 import models as dingtalkrobot__1__0_models
from alibabacloud_tea_util import models as util_models
from app.common import Common
from app.commons.redis_key import RedisKey
from app.models.departments_model import DepartmentsModel
from app.models.ding_users_model import DingUserModel

logger = Common.get_app_logger('ding_service')
app_key = Common.get_config(Common.DING_APP_CONFIG, 'APP_KEY')
app_secret = Common.get_config(Common.DING_APP_CONFIG, 'APP_SECRET')


class DingService:
    """
    钉钉服务
    """

    def __init__(self):
        self.access_token = DingService.get_access_token()
        self.domain = "https://oapi.dingtalk.com"
        self.redis = Common.get_global_redis()
        self.db_session = sessionmaker(bind=Common.get_global_db())()

    @staticmethod
    def create_client() -> dingtalkoauth2_1_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkoauth2_1_0Client(config)

    @staticmethod
    def get_access_token() -> str:
        """
        获取钉钉token
        :return:
        """
        redis = Common.get_global_redis()
        # 如果存在key，直接返回
        if redis.exists(RedisKey.DING_ACCESS_TOKEN):
            logger.info(f"获取钉钉token成功：{redis.get(RedisKey.DING_ACCESS_TOKEN)}")
            return redis.get(RedisKey.DING_ACCESS_TOKEN)
        client = DingService.create_client()
        get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
            app_key=app_key, app_secret=app_secret)

        try:
            token = client.get_access_token(get_access_token_request)
            logger.info(f"获取钉钉token成功：{token.body.access_token}")
            redis.set(RedisKey.DING_ACCESS_TOKEN, token.body.access_token, ex=token.body.expire_in)
            return token.body.access_token
        except Exception as err:
            logger.error(err)
            return ''

    def get_department_list(self, dept_id=1):
        """
        获取部门列表
        :param dept_id:
        :return:
        """
        url = 'https://oapi.dingtalk.com/topapi/v2/department/listsub'
        data = {
            "access_token": self.access_token,
            "dept_id": dept_id
        }
        response = requests.post(url=url, params=data).json()
        print(response)
        result = response['result']

        if not result:
            return
        for department in result:
            print(department)
            fields = {
                'name': department['name'],
                'dept_id': department['dept_id'],
                'parent_id': department['parent_id'],
            }
            DepartmentsModel.update_or_insert(self.db_session, fields)
            self.get_department_list(department['dept_id'])

    def get_department_info(self, department_id):
        """
        获取部门详情
        :param department_id:
        :return:
        """
        url = f"{self.domain}/topapi/v2/department/get"
        data = {
            "access_token": self.access_token,
            "dept_id": department_id
        }
        response = requests.post(url=url, params=data).json()
        print(response)

    def get_sub_department(self, department_id):
        """
        获取子部门id列表
        :param department_id:
        :return:
        """
        url = f"{self.domain}/topapi/v2/department/listsubid"
        data = {
            "access_token": self.access_token,
            "dept_id": department_id
        }
        response = requests.post(url=url, params=data).json()
        print(response)

    def get_department_userid_list(self, department_id):
        """
        获取部门用户id列表
        :param department_id:
        :return:
        """
        url = f"{self.domain}/topapi/user/listid"
        data = {
            "access_token": self.access_token,
            "dept_id": department_id
        }
        response = requests.post(url=url, params=data).json()
        userid_list = response.get('result', {}).get('userid_list', [])
        return userid_list

    def get_department_user_info(self, department_id):
        """
        获取部门用户详情
        :param department_id:
        :return:
        """
        url = f"{self.domain}/topapi/v2/user/list"
        data = {
            "access_token": self.access_token,
            "dept_id": department_id,
            "cursor": 0,
            "size": 100
        }
        response = requests.post(url=url, params=data).json()
        print(response)
        user_list = response.get('result', {}).get('list', [])
        return user_list

    def get_user_info(self, user_id):
        """
        获取用户详情
        :param user_id:
        :return:
        """
        url = f"{self.domain}/topapi/v2/user/get"
        data = {
            "access_token": self.access_token,
            "userid": user_id
        }
        response = requests.post(url=url, params=data).json()
        print(response)

    def send_group_msg(self, msg, open_conversation_id, robot_code):
        """
        发送群消息
        :param msg:
        :param open_conversation_id:
        :param robot_code:
        :return:
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        client = dingtalkrobot_1_0Client(config)
        org_group_send_headers = dingtalkrobot__1__0_models.OrgGroupSendHeaders()
        org_group_send_headers.x_acs_dingtalk_access_token = self.access_token
        org_group_send_request = dingtalkrobot__1__0_models.OrgGroupSendRequest(
            msg_param='{"content":"' + msg + '"}',
            msg_key='sampleText',
            open_conversation_id=open_conversation_id,
            robot_code=robot_code,
            # cool_app_code='COOLAPP-1-10231FE7E249212A84D30006',
        )
        try:
            client.org_group_send_with_options(org_group_send_request, org_group_send_headers,
                                               util_models.RuntimeOptions())
        except Exception as err:
            print(err)

    def sync_user_info(self):
        """
        更新用户信息
        :return:
        """
        db_session = self.db_session
        department_list = DepartmentsModel.get_departments(db_session)
        for dept in department_list:
            dept_id = dept.dept_id
            dept_name = dept.name
            user_list = self.get_department_user_info(dept_id)
            db = Common.get_global_db()
            db_session = sessionmaker(bind=db)()
            for user in user_list:
                fields = {
                    'name': user['name'],
                    'dept_id': dept_id,
                    'dept_name': dept_name,
                    'title': user['title'],
                    'userid': user['userid'],
                    'unionid': user['unionid'],
                    'telephone': user['telephone'],
                    'org_email': user.get('org_email', ''),
                    'email': user.get('email', ''),
                    'mobile': user.get('mobile', ''),
                    'leader': user.get('leader', ''),
                    'boss': user.get('boss', ''),
                }
                DingUserModel.update_or_insert(db_session, fields)


if __name__ == '__main__':
    ...