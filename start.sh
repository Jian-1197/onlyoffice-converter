#!/bin/bash

# 启动OnlyOffice服务
service postgresql start
service nginx start
/usr/bin/documentserver/documentserver.sh &

# 等待服务初始化
sleep 15

# 启动Python API
python3 /app/api/app.py
