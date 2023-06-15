from fastapi import FastAPI
from app.common import Common

application = FastAPI()
logger = Common.get_app_logger()


@application.get("/api/chat")
async def chat():
    return {"msg": "Hello World"}


__all__ = ["application"]
