from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import requests

import os

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "9000"))
os.environ.setdefault("FASTMCP_PORT", str(PORT))

# SearXNG 实例根地址，只需填写实例域名=
# 可通过环境变量 SEARXNG_URL 覆盖（容器化部署更方便）
SEARXNG_BASE = os.environ.get("SEARXNG_URL", "https://searxng.abc.com").rstrip("/")

# 拼接完整搜索接口地址，%s 为查询占位符
SEARXNG_URL = f"{SEARXNG_BASE}/search?q=%s&format=json"

# HTTP (Streamable HTTP) 传输需要手动注入 CORS 头，方便浏览器/客户端跨域调用
cors_middleware = Middleware(
    CORSMiddleware,
    allow_origins=["*"],            # 允许所有来源；生产环境建议改为具体来源，如 ["http://localhost:8080"]
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

mcp = FastMCP("searxng")

@mcp.tool()
def search(query: str) -> str:
    """
    搜索关键字
    """
    # API URL
    url = SEARXNG_URL % query

    try:
        # 发送GET请求
        response = requests.get(url)

        # 检查请求是否成功
        if response.status_code == 200:
            # 将响应内容解析为JSON
            data = response.json()
            # print("JSON内容:")
            # print(data,type(data))
            result_list=[]
            for i in data["results"]:
                # print(i["content"])
                result_list.append(i["content"])
            content="\n".join(result_list)
            # print(content)
            return content
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"请求过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    # transport="streamable-http" 会在 /mcp 暴露端点，例如 http://localhost:9000/mcp
    # stateless_http=True：无状态模式，每个请求独立、无需维护 Mcp-Session-Id，
    # 避免客户端出现 "Missing session ID" 错误（适合此类无状态搜索服务）
    mcp.run(
        transport="streamable-http",
        host=HOST,
        port=PORT,
        path="/mcp",
        middleware=[cors_middleware],
        stateless_http=True,
    )