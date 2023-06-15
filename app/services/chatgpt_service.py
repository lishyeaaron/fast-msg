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


prompts = {
    '扮演股票分析师': "请你扮演以为中国A股金融股票分析师，根据以下一段投资者和企业的问答，来给我买入或者卖出的建议",
    '严格遵守规则': "请你根据以上,请严格记住不要反问，返回一个#*#x*#*字符串",
}


class StockGpt(ChatGptService):
    @staticmethod
    def get_answer(stock_msg):
        msg = [
            {"role": "user",
             "content": f"""请你扮演以为中国A股金融股票分析师，根据以下一段投资者和企业的问答，来给我买入或者卖出的建议
             {stock_msg}"""},
        ]

        # 使用正则提取#*#开头*#*结尾的sql语句
        # r = re.findall(r"#\*#(.*)\*#*", r)

        r = ChatGptService.query(msg)
        return r


if __name__ == '__main__':
    r = StockGpt.get_answer("""
    提问:您好，公司代销及自产光模块产品销量如何？
    回答:投资者您好，感谢您对公司的关心与支持！公司下属子公司有工控光模块相关的研发及产品，目前市场占有率低，推广进程较为缓慢。""")
    print(r)