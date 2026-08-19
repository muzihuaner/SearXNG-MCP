# 使用官方轻量级 Python 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY Server.py .

# 暴露端口（默认 9000，可通过 docker run -e PORT=xxxx 覆盖）
EXPOSE 9000

# 启动服务，默认监听 0.0.0.0:9000，MCP 端点为 /mcp
CMD ["python", "Server.py"]
