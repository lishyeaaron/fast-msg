from fastapi import FastAPI, Request
from app.common import Common
from fastapi.responses import JSONResponse
from app.routes.ding_route import router as ding_router


application = FastAPI()
logger = Common.get_app_logger()
application.include_router(ding_router)
__all__ = ["application"]
