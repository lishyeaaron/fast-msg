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
    # 查看当前文件夹下是否存在app.pid文件如果app.pid文件存在，且linux系统中存在该pid说明程序已经启动，则打印pid并提示程序已经启动如果app.
    # pid文件不存在，则说明程序未启动，则将当前进程号写入(覆盖)app.pid文件中
    if os.path.exists("app.pid"):
        with open("app.pid", "r") as f:
            pid = f.read()
        if os.path.exists(f"/proc/{pid}"):
            print(f"程序已经启动，pid为{pid}")
            exit(0)
        else:
            with open("app.pid", "w") as f:
                f.write(str(os.getpid()))
    else:
        with open("app.pid", "w") as f:
            f.write(str(os.getpid()))

    parser = argparse.ArgumentParser(description="Start the FastAPI application.")
    parser.add_argument("--port", type=int, default=8000, help="Port number to run the application on")
    args = parser.parse_args()

    main(args.port)
