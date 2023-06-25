import argparse
from app.api import application
from app.app_schedule import run_schedule
import threading
import uvicorn
import os


def main(port):
    # 创建一个新的线程，运行定时任务
    t = threading.Thread(target=run_schedule)
    t.start()
    uvicorn.run(application, host="0.0.0.0", port=port, log_config="app/logging.conf")


if __name__ == "__main__":
    # 把占用8080端口的进程杀掉
    os.system("kill -9 $(lsof -i:8080 -t)")

    parser = argparse.ArgumentParser(description="Start the FastAPI application.")
    parser.add_argument("--port", type=int, default=8080, help="Port number to run the application on")
    args = parser.parse_args()

    main(args.port)
