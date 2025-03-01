FROM onlyoffice/documentserver:7.4.2

# 安装Python和相关依赖
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# 创建应用目录和临时目录
RUN mkdir -p /app/tmp
WORKDIR /app

# 复制Python依赖和代码
COPY requirements.txt .
COPY api ./api
RUN pip3 install -r requirements.txt

# 设置权限和端口
RUN chmod -R 777 /app/tmp
EXPOSE 80 5000

# 启动脚本
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
