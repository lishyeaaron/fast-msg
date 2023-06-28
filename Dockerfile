FROM python:3.9
WORKDIR /www
COPY requirements.txt .
RUN apt-get update && apt-get install -y net-tools vim iputils-ping telnet && apt-get clean
RUN pip install --upgrade pip --index-url https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
RUN pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir


