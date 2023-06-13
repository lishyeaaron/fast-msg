FROM python:3.9
WORKDIR /www
COPY ops_hub .
COPY requirements.txt .
RUN pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir
CMD ["python3 main.py"]

