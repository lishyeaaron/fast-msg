#!/bin/bash

mkdir -p /var/log/fast-msg
docker rm -f fast-msg
docker run -d --name fast-msg-p 50084:8080 \
  -v /www/log/fast-msg:/var/log/fast-msg \
  -v /www/fast-msg:/www/fast-msg \
  --net mynetwork \
  --name fast-msg \
  --restart unless-stopped \
  --memory 512m --memory-swap 512m \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --log-opt labels=app_logs \
  --health-cmd "python -c 'import requests; requests.get(\"http://localhost:8080\")'" \
  --health-interval 10s \
  --health-retries 3 \
  --health-timeout 5s \
  fast-msg-py \
  /bin/bash -c "cd /www/fast-msg; python main.py"

docker logs -f fast-msg

