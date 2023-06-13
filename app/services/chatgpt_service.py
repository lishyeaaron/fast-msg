# -*- coding: utf-8 -*-
from retrying import retry
import requests
import re
from app.common import Common

logger = Common.get_app_logger('chatgpt_service')


class ChatGptService:
    openai_key = database = Common.get_config(Common.OPENAI_CONFIG, 'OPENAI_KEY')
    openai_url = Common.get_config(Common.OPENAI_CONFIG, 'OPENAI_URL')
    openai_endpoint = f"{openai_url}/v1/chat/completions"
    model = 'gpt-3.5-turbo'

    def __init__(self):
        ...

    @staticmethod
    @retry(wait_fixed=1000, stop_max_attempt_number=3)
    def query(messages):
        # Define the payload for the API request
        payload = {
            "model": ChatGptService.model,
            "temperature": 0.5,
            "max_tokens": 256,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "messages": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ChatGptService.openai_key}"
        }

        # Make the API request using the requests library
        response = requests.post(ChatGptService.openai_endpoint, json=payload, headers=headers)

        # Check the response status
        if response.status_code != 200:
            print(response.text)
            raise ValueError("Failed to request OpenAI API")

        # Extract the generated answer from the response
        response_text = response.json()["choices"][0]['message']["content"].strip()
        return response_text


class SqlGpt(ChatGptService):
    @staticmethod
    def transform_mongo_to_postgresql(mongo_sql, postgresql_table_info, strict=True):
        # 如果mongo_sql中不中不包含常见的mongo语句关键字，则直接返回非相关问题不予回答
        not_related_keywords = 'NOT_RELATED_KEYWORDS'
        if not SqlGpt.process_mongo_query:
            return not_related_keywords
        # 如果mongo_sql和postgresql_table_info加起来的长度小于10或者大于1000，则直接返回非相关问题不予回答
        if len(mongo_sql) + len(postgresql_table_info) < 10 or len(mongo_sql) + len(postgresql_table_info) > 1000:
            return not_related_keywords

        msg = [
            {"role": "user",
             "content": f"""你扮演一个输入mongo语句和postgresql信息提示，输出postgresql语句的角色，以下为mongo语句或者提示{mongo_sql}"""},
            {"role": "user",
             "content": f"""以下为postgresql中的和mongo相关关联的表sql语句或者提示:{postgresql_table_info}"""},
        ]

        if strict:
            msg.append({"role": "user", "content": f"""请你根据以上的postgresql中的表信息(如果有的话)，将mongo中的语句转化为postgresql中的语句,请严格记住
               ，不要反问，你返回的信息中不要包含除了sql语句之外的任何信息，否则会被判定为错误答案，你给的回答应该是一个使用#*#开头*#*结尾的sql语句，除此之外不要包含任何字符串，请严格遵守
               ，如果给定信息和mongo和postgresql无关，返回一个#*#非相关问题不予回答*#*字符串
               """})
            r = SqlGpt.query(msg)
            # 使用正则提取#*#开头*#*结尾的sql语句
            r = re.findall(r"#\*#(.*)\*#*", r)

        else:
            msg.append({"role": "user", "content": f"""请你根据以上的postgresql中的表信息(如果有的话)，将mongo中的语句转化为postgresql中的语句,请严格记住
               ，不要反问，返回一个#*#{not_related_keywords}*#*字符串
               """})
            r = ChatGptService.query(msg)
        logger.info(
            f"transform_mongo_to_postgresql:mongo_sql:{mongo_sql},postgresql_table_info:{postgresql_table_info},answer:{r}")
        return r


    @staticmethod
    def process_mongo_query(mongo_sql):
        common_keywords = ["find", "insert", "update", "delete", "aggregate", "sort", "distinct",
                           "mongo", "db"]
        lowercase_sql = mongo_sql.lower()
        if any(keyword in lowercase_sql for keyword in common_keywords):
            # 包含常见的MongoDB语句关键字
            return True
        else:
            # 不包含常见的MongoDB语句关键字，返回非相关问题不予回答
            return False
