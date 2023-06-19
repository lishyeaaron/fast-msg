from fastapi import FastAPI, Request
from app.common import Common
from fastapi.responses import JSONResponse
application = FastAPI()
logger = Common.get_app_logger()


@application.route("/api/chat", methods=["GET", "POST", "PUT"])
async def chat(request: Request):
    request_method = request.method  # 获取请求方式
    request_headers = request.headers  # 获取请求头
    logger.info(request_headers)

    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.json()  # 获取请求体（仅限 POST、PUT 和 PATCH 请求）
        else:
            request_body = None
    except Exception as e:
        print("Exception occurred while parsing request body:", e)
        request_body = None

    query_params = request.query_params  # 获取查询参数

    # 打印请求信息
    print("Request Method:", request_method)
    print("Request Headers:", request_headers)
    print("Request Body:", request_body)
    print("Query Parameters:", query_params)
    logger.info(f"Request Method: {request_method}, Request Headers: {request_headers}, Request Body: {request_body}, Query Parameters: {query_params}")
    return JSONResponse(content={"message": "ok"})


__all__ = ["application"]
