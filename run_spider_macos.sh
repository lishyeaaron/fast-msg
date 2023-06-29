#!/bin/bash

mkdir -p /var/www/log/fast-msg-spider
mkdir -p /var/www/fast-msg-spider
docker rm -f fast-msg-spider
docker run -d --name fast-msg-spider \
  -e TZ=Asia/Shanghai \
  -v /var/www/log/fast-msg-spider:/var/log/fast-msg \
  -v /var/www/fast-msg-spider:/www/fast-msg \
  --net mynetwork \
  --name fast-msg-spider \
  --restart unless-stopped \
  --memory 512m --memory-swap 512m \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --log-opt labels=app_logs \
  fast-msg-py \
  /bin/bash -c "cd /www/fast-msg; python run_spider.py"

docker logs -f fast-msg-spider

