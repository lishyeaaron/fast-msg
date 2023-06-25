from fastapi import APIRouter
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.commons.redis_key import RedisKey
from app.services.chatgpt_service import ChatGptService
from app.services.ding_service import DingService
from app.common import Common
from fastapi.templating import Jinja2Templates
import json
import re

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
logger = Common.get_app_logger()


def query_keyword(question, conversation_id=None):
    redis = Common.get_global_redis()
    keywords = redis.get(RedisKey.KEYWORDS)
    if keywords:
        word = f'已经知目前的关键词列表是: {keywords}'
    else:
        word = '目前还没有关键词'
    msg = [
        {"role": "user",
         "content": "从现在开始,你需要对话语的内容进行分析，判断用户想对关键词进行哪些操作"
                    f"{word}"
                    "首先用户的命令分为两种目的，一种目的为变更目前的关键词列表，一种目的为查询目前的关键词列表"
                    "如果是查询目的或者你完全无法理解，请根据已经有信息在说出你想说的话语,不需要加上任何符号"
                    "如果用户的目的是变更关键词操作,请不要反问、不要回复其他任意除了给定格式外的内容，否则会被认为是错误的回复，根据用户的执行,返回给我变更后的关键词列表，并以#符号开头和结尾,中间用逗号,分隔"
                    "并给出符号#开头和结尾的字符串，中间用逗号分隔，比如#沙特,UFO#"
                    "举例 比如用户说了:增加英伟达、英睿达、英特尔为关键词,那么你需要返回把现有的关键词列表和用户的关键词列表合并后的关键词列表(增加、添加、新增等词都是这个效果，这里要特别注意合并操作和覆盖操作的区别，不要漏了原有关键词)，并以#符号开头和结尾,中间用逗号,分隔（注意#号只需要出现首位，重要不要出现，而且是最终的列表的首尾）"
                    "再举例 比如用户说删除英伟达 那么你需要返回把现有的关键词列表和用户的关键词列表删除后的关键词列表，并以#符号开头和结尾,中间用逗号,分隔"
                    "再举例 比如用户说把英伟达改成AMD 那么你需要返回把现有的关键词列表和用户的关键词列表修改后的关键词列表，并以#符号开头和结尾,中间用逗号,分隔"
                    ""
         },
    ]
    msg.append({"role": "user", "content": f"接下来是话语内容:{question}："})
    f"CONVERSATION_{conversation_id}"
    result = ChatGptService.query(msg)
    logger.info(f'gpt return  r:{result}')
    # 使用正则提取#开头#结尾的语句,注意不要把#也提取出来
    r = re.findall(r'#(.*?)#', result)
    if len(r) > 0:
        # 确认是关键词格式 以逗号分割
        r = r[0].split(",")
        # 去除空格
        r = [i.strip() for i in r]
        # 去除空字符串
        r = [i for i in r if i != ""]
        # 去除关键词中的空格
        r = [i.replace(" ", "") for i in r]
        # 再转换成字符串
        r = ",".join(r)
        redis.set(RedisKey.KEYWORDS, r)
    else:
        return result

    keywords = redis.get(RedisKey.KEYWORDS)
    logger.info(f'keywords:{keywords}')
    return f"已经更新关键词列表为:{keywords}"


@router.post("/api/chat")
async def task_chat(request: Request):
    """
    聊天创建任务
    :param request:
    :return:
    """
    request_params = await request.body()
    request_params = request_params.decode('utf-8')
    request_params = json.loads(request_params)
    open_conversation_id = request_params.get("conversationId")
    at_users = request_params.get("atUsers")
    user_id = request_params.get("senderStaffId")
    robot_code = request_params.get("robotCode")
    text = request_params.get("text")
    content = text.get("content")
    result = query_keyword(content)
    logger.info(
        f"open_conversation_id: {open_conversation_id}, at_users: {at_users}, user_id: {user_id},robot_code: {robot_code}, content: {content}")
    ding_api = DingService()
    ding_api.send_group_msg(result, open_conversation_id=open_conversation_id, robot_code=robot_code)
    return {"message": "ok"}


query_keyword(f"修改关键词为AMD,英伟达,沙特")