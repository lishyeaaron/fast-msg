from fastapi import FastAPI, Request
from app.common import Common
from fastapi.responses import JSONResponse
from app.routes.ding_route import router as ding_router
redis = Common.get_global_redis()
redis.ping()

application = FastAPI()
logger = Common.get_app_logger()
application.include_router(ding_router)
__all__ = ["application"]
