from app.spider_schedule import run_schedule


def main():
    try:
        # 启动FastAPI应用程序
        run_schedule()
    except KeyboardInterrupt:
        # 当收到键盘中断信号时，停止定时任务线程
        exit()


if __name__ == "__main__":
    # 把占用8080端口的进程杀掉

    main()
