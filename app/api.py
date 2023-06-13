from fastapi import FastAPI
from app.api.items.items import SqlTransformItem
from app.routes.ding_route import router as ding_router
from app.routes.sentry_route import router as sentry_router
from app.services.chatgpt_service import SqlGpt
from app.common import Common
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin.settings import Settings

# create FastAPI application
app = FastAPI()

application = FastAPI()
application.include_router(ding_router)
application.include_router(sentry_router)
logger = Common.get_app_logger()
# create AdminSite instance
site = AdminSite(settings=Settings(database_url_async='sqlite+aiosqlite:///amisadmin.db'))
# mount AdminSite instance
site.mount_app(app)


@application.get("/api/chat")
async def chat():
    return {"msg": "Hello World"}


__all__ = ["application"]
