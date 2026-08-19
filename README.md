# SearXNG MCP Server (Streamable HTTP)

一个基于 [FastMCP](https://gofastmcp.com) 实现的 SearXNG 搜索 MCP 服务，使用 **Streamable HTTP** 传输，支持本地运行与 Docker 部署。

## 功能

- 暴露 MCP 工具 `search(query)`：根据关键字调用 SearXNG 实例并返回搜索结果摘要。
- 通过 HTTP 端点 `http://<host>:<port>/mcp` 提供 MCP 服务，便于远程 / 跨域调用。
- 采用 **无状态（stateless）** Streamable HTTP 模式，客户端无需维护 `Mcp-Session-Id`，可直接并发调用。
- 支持通过环境变量自定义 SearXNG 实例地址，方便私有化部署。

## 环境变量

| 变量名        | 默认值               | 说明                                                  |
| ------------- | -------------------- | ----------------------------------------------------- |
| `SEARXNG_URL` | `https://searxng.abc.com` | SearXNG 实例根地址（只需填域名，无需路径）          |
| `HOST`        | `0.0.0.0`            | 服务监听地址                                          |
| `PORT`        | `9000`               | 服务监听端口                                          |

## 本地运行

```bash
# 安装依赖（建议使用虚拟环境）
pip install -r requirements.txt

# 可选：自定义 SearXNG 实例（只需填根地址）
export SEARXNG_URL="https://your-searxng-instance"

# 启动服务
python Server.py
```

启动后，MCP 端点为：

```
http://localhost:9000/mcp
```

## Docker 部署

### 构建镜像

```bash
docker build -t searxng-mcp .
```

### 运行容器

```bash
docker run -d \
  --name searxng-mcp \
  -p 9000:9000 \
  -e SEARXNG_URL="https://searxng.abc.com" \
  searxng-mcp
```

如需修改端口，可同时覆盖容器内外端口与 `PORT`：

```bash
docker run -d \
  --name searxng-mcp \
  -p 8080:8080 \
  -e PORT=8080 \
  searxng-mcp
```

### 访问地址

部署完成后，MCP 端点格式为：

```
http://<你的服务器域名或IP>:<端口>/mcp
```

例如：`http://localhost:9000/mcp` 或 `https://mcp.your-domain.com/mcp`

## 客户端配置

在支持 Streamable HTTP 的 MCP 客户端中，将服务地址填写为上面的 `/mcp` 端点即可，例如：

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://localhost:9000/mcp"
    }
  }
}
```

## 工具说明

### `search(query: str) -> str`

根据关键字调用 SearXNG 搜索，返回各结果条目的 `content` 文本，以换行拼接。

- `query`：搜索关键字。
- 返回：搜索结果的文本内容；请求失败时返回 `False`。

## 并发与性能

```
测试结果示例（局域网 / 上游 `so.xxx.cn`）：

```
总请求数      : 100
并发 worker   : 50
成功          : 100
失败          : 0
总耗时(秒)    : 67.68
吞吐(QPS)     : 1.48
平均延迟(秒)  : 27.284
最小延迟(秒)  : 7.203
最大延迟(秒)  : 44.418
```

> 注意：端到端延迟主要取决于 SearXNG 上游实例的响应速度（本例平均约 27s 来自上游 `so.xxx.cn` 较慢），服务本身可稳定承载并发且零失败。若需提升吞吐，可：
> - 换用响应更快 / 自托管的 SearXNG 实例（通过 `SEARXNG_URL` 指定）；

## 常见问题

**Q: 客户端报错 `Missing session ID`？**
A: 本服务已启用 `stateless_http=True`，无需 session。若仍报该错，请确认客户端指向的是 `/mcp` 端点。

**Q: 如何在生产环境收紧 CORS？**
A: 编辑 `Server.py` 中的 `CORSMiddleware`，将 `allow_origins=["*"]` 改为具体来源列表，如 `["https://your-domain.com"]`。
