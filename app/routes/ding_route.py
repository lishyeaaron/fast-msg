from fastapi import APIRouter
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.common import Common
from fastapi.templating import Jinja2Templates
import json

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
logger = Common.get_app_logger()

