# **AI 闪卡生成器 - 技术设计与开发文档**

**文档版本**: 1.0
**最后更新**: 2025-11-18
**负责人**: bhc6

## 1. 项目概述

### 1.1. 项目目标

本项目旨在开发一个智能工具，能够自动化地从用户上传的各种格式文档（包括扫描件）中提取文本，并利用大语言模型（LLM）生成高质量的问答式闪卡（Flashcards）。其核心价值在于极大地提升学习效率，将非结构化的学习资料转化为结构化的、易于记忆和复习的知识卡片。

### 1.2. 核心功能

- **多格式文件上传**: 支持 `.pdf`（文本型与扫描型）、`.docx`、`.pptx`、`.txt`。
- **智能文本提取**: 自动根据文件类型选择最优的文本提取策略，包括对扫描件的 OCR 识别。
- **AI 闪卡生成**: 调用高质量 LLM API，将文本内容转化为精准的问答对。
- **异步处理**: 所有耗时操作均在后台执行，前端通过任务 ID 轮询获取结果，保证了优秀的用户体验。
- **RESTful API**: 提供清晰的前后端分离接口，便于独立开发和未来扩展。

## 2. 系统架构

本项目采用基于任务队列的微服务架构，确保系统的可扩展性、可靠性和高性能。

### 2.1. 架构图

```
+----------------+      (1) 文件上传       +-----------------+      (3) 任务入队       +-----------------+
|                | ----------------------> |                 | ---------------------> |                 |
|  Vue.js 前端   |    (POST /api/...-async)  |   Flask API     |     (Celery Task)      |  Redis (Broker) |
| (用户浏览器)   |                         |  (Web 服务器)   |                        |   (消息代理)    |
|                |      (2) 返回 task_id     |                 | <--------------------  |                 |
|                | <---------------------- |                 |     (4) 任务出队       +-----------------+
+----------------+    (HTTP 202 Accepted)   +-----------------+                        |
      ^                                                                                |
      | (7) 轮询状态                                                                   v
      | (GET /api/task-status/{id})                                            +-----------------+
      |                                                                        |                 |
      +----------------------------------------------------------------------  |  Celery Worker  |
                                      (8) 返回状态/结果                          | (后台工作进程)  |
                                                                               +-----------------+
                                                                                 |         ^
                                                                           (5) 调用     | (6) 存储结果
                                                                           外部服务     |
                                                                                 v         |
                                                                           +---------------+
                                                                           | LLM API / OCR |
                                                                           +---------------+
```

### 2.2. 组件职责

- **Vue.js 前端**: 负责用户交互界面，包括文件选择、上传、进度展示和最终闪卡结果的渲染。
- **Flask API 服务器**: 作为系统的入口，负责：
    - 接收前端的文件上传请求。
    - 对请求进行基本验证。
    - 将耗时任务（文件处理）封装成 Celery Task 并推送到 Redis。
    - 立即向前端返回一个任务 ID。
    - 提供任务状态查询接口，从 Redis 读取任务进度和结果并返回。
- **Redis**: 扮演双重角色：
    - **消息代理 (Message Broker)**: 存储 Flask 发来的任务消息，等待 Celery Worker 来领取。
    - **结果后端 (Result Backend)**: 存储 Celery Worker 执行任务的中间状态和最终结果。
- **Celery Worker**: 独立于 Flask 运行的后台工作进程，是系统的"重活执行者"。它负责：
    - 监听 Redis 任务队列。
    - 获取并执行任务，包括文本提取 (OCR) 和调用 LLM API。
    - 将任务的执行状态和结果写回 Redis。
- **外部服务**:
    - **LLM API (火山引擎)**: 接收文本内容，生成闪卡 JSON 数据。兼容 OpenAI API 协议。
    - **OCR 服务 (如 Tesseract, Google Vision)**: 从图像或扫描件中识别文本。

## 3. 技术栈

| 类别       | 技术/库                                | 用途说明                                           |
| :--------- | :------------------------------------- | :------------------------------------------------- |
| **后端**   | Python 3.12+                           | 主要开发语言                                       |
|            | Flask                                  | 轻量级 Web 框架，提供 API 接口                     |
|            | Celery                                 | 强大的分布式异步任务队列框架                       |
|            | Redis                                  | 高性能键值数据库，用作 Celery 的消息代理和结果后端 |
|            | Gunicorn (生产环境)                    | 生产级 WSGI 服务器，用于部署 Flask 应用            |
| **前端**   | Vue.js 3                               | 现代化的前端框架，用于构建用户界面                 |
|            | Vite                                   | 高性能的前端构建工具和开发服务器                   |
|            | Axios                                  | 基于 Promise 的 HTTP 客户端，用于 API 请求         |
| **数据处理** | `pypdfium2`, `python-docx`, `python-pptx` | 分别用于处理 PDF, .docx, .pptx 文件                |
|            | `pytesseract` + Tesseract              | 默认的开源 OCR 解决方案                            |
|            | `google-cloud-vision` (可选)           | 更精准的商业 OCR 方案                              |
|            | `openai`                               | OpenAI SDK，用于兼容火山引擎 API 协议              |
| **部署**   | Docker & Docker Compose                | 容器化技术，用于打包、分发和运行应用               |
|            | Nginx (生产环境)                       | 高性能反向代理、负载均衡和静态文件服务             |

## 4. 本地开发环境搭建 (WSL)

### 4.1. 环境要求

- WSL 2 (推荐 Ubuntu-22.04)
- Docker Desktop for Windows (已开启 WSL 集成)
- VS Code (已安装 Remote - WSL 扩展)
- Python 3.12, Node.js 18+ (建议通过 `pyenv` 和 `nvm` 管理)
- Tesseract OCR 引擎 (通过 `sudo apt install tesseract-ocr tesseract-ocr-chi-sim` 安装)

### 4.2. 启动流程

1.  **启动 Redis**:
    ```bash
    docker run --name my-redis -d -p 6379:6379 redis:7
    ```
2.  **启动后端**: 打开两个 WSL 终端，均进入 `backend` 目录并激活虚拟环境 (`source .venv/bin/activate`)。
    - **终端 1 (Celery)**: `celery -A app.celery_app worker --loglevel=info`
    - **终端 2 (Flask)**: `python app.py`
3.  **启动前端**: 打开第三个 WSL 终端，进入 `frontend` 目录。
    - **终端 3 (Vue)**: `npm run dev`

## 5. API 接口规范

### 5.1. `POST /api/generate-flashcards-async`

- **描述**: 接收用户上传的文件，并创建一个异步处理任务。
- **请求**:
    - **Method**: `POST`
    - **Content-Type**: `multipart/form-data`
    - **Body**: 包含一个名为 `file` 的文件字段。
- **响应**:
    - **成功 (202 Accepted)**:
        ```json
        {
          "message": "文件上传成功，正在后台处理...",
          "task_id": "a33dfaf8-1d6f-46c4-90f4-685d816d8b22",
          "status_url": "http://127.0.0.1:5000/api/task-status/a33dfaf8-1d6f-46c4-90f4-685d816d8b22"
        }
        ```
    - **失败 (400 Bad Request)**: `{"error": "错误描述，如 '没有选择文件'"}`

### 5.2. `GET /api/task-status/<task_id>`

- **描述**: 根据任务 ID 查询任务的当前状态和结果。
- **请求**:
    - **Method**: `GET`
    - **URL 参数**: `<task_id>` (字符串)
- **响应**:
    - **任务进行中 (State: `PROGRESS`)**:
        ```json
        {
          "state": "PROGRESS",
          "status": "正在调用 AI 生成闪卡...",
          "result": null
        }
        ```
    - **任务成功 (State: `SUCCESS`)**:
        ```json
        {
          "state": "SUCCESS",
          "status": "完成!",
          "result": [
            {
              "question": "生成的问题1",
              "answer": "对应的答案1"
            },
            {
              "question": "生成的问题2",
              "answer": "对应的答案2"
            }
          ]
        }
        ```
    - **任务失败 (State: `FAILURE`)**:
        ```json
        {
          "state": "FAILURE",
          "status": "具体的错误信息，如 '生成闪卡失败: ...'",
          "result": null
        }
        ```
    - **任务等待中 (State: `PENDING`)**: `{"state": "PENDING", ...}`

## 6. 环境变量与配置

所有敏感信息和可配置参数都应通过环境变量进行管理。在 `backend` 目录下创建一个 `.env` 文件。

| 变量名                       | 是否必须 | 描述                                                              | 示例值                                            |
| :--------------------------- | :------- | :---------------------------------------------------------------- | :------------------------------------------------ |
| `ARK_API_KEY`                | **是**   | 用于调用火山引擎服务的 API 密钥。详见：https://www.volcengine.com/docs/82379/1330626 | `your-ark-api-key-here`                          |
| `GOOGLE_APPLICATION_CREDENTIALS` | 否       | 指向 Google Cloud 服务账号 JSON 密钥文件的**绝对路径**，用于启用 Google Vision OCR。 | `/home/bhc6/gcp-keys/my-project-key.json` |
| `CELERY_BROKER_URL`            | 否       | Celery 消息代理地址。默认为 `redis://localhost:6379/0`。           | `redis://user:password@remote-host:6379/0`      |
| `CELERY_RESULT_BACKEND`        | 否       | Celery 结果后端地址。默认为 `redis://localhost:6379/0`。          | `redis://user:password@remote-host:6379/0`      |

## 7. 生产环境部署 (上线) 策略

为了实现稳定、高效的生产部署，我们推荐采用 **Docker Compose** + **Nginx** 的方案。

### 7.1. 部署架构

```
                               +----------------+
                               |   用户请求      |
                               +-------+--------+
                                       | (80/443)
+--------------------------------------v------------------------------------------+
|  云服务器 (e.g., AWS EC2, DigitalOcean Droplet)                                  |
|                                                                                 |
|      +-------------------------------------------------------------+            |
|      | Nginx (作为反向代理，运行在宿主机或 Docker 容器中)            |            |
|      | - 处理 SSL/TLS 证书                                         |            |
|      | - 静态文件服务 (前端构建产物)                               |            |
|      | - API 请求转发到 Gunicorn                                   |            |
|      +--------------------------+----------------------------------+            |
|                                 | (/api/*)                         | (/)         |
|                                 v                                  v            |
|      +-------------------------------------------------------------+            |
|      | Docker Compose 管理的容器网络                               |            |
|      |                                                             |            |
|      |  +------------------+     +------------------+     +------------------+   |
|      |  | Flask + Gunicorn |     |  Celery Worker   |     |      Redis       |   |
|      |  | (App 容器)       | --> |  (Worker 容器)   | --> |   (Redis 容器)   |   |
|      |  +------------------+     +------------------+     +------------------+   |
|      |                                                             |            |
|      +-------------------------------------------------------------+            |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

### 7.2. `docker-compose.yml` 示例

在项目根目录创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # Redis 服务
  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data

  # 后端应用 (Flask + Gunicorn)
  backend:
    build:
      context: ./backend
    restart: always
    command: gunicorn --bind 0.0.0.0:5000 --workers 4 app:app # 使用 Gunicorn 启动
    volumes:
      - ./backend/uploads:/app/uploads # 将上传目录挂载出来
    env_file:
      - ./backend/.env # 加载环境变量
    depends_on:
      - redis

  # Celery Worker 服务
  worker:
    build:
      context: ./backend
    restart: always
    command: celery -A app.celery_app worker --loglevel=INFO
    volumes:
      - ./backend/uploads:/app/uploads
    env_file:
      - ./backend/.env
    depends_on:
      - redis
      - backend

  # Nginx 反向代理
  nginx:
    image: nginx:latest
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro # Nginx 配置文件
      - ./frontend/dist:/usr/share/nginx/html:ro     # 前端构建产物
      # - ./nginx/certs:/etc/nginx/certs:ro          # SSL 证书
    depends_on:
      - backend

volumes:
  redis_data:
```

### 7.3. 部署步骤

1.  **构建前端**: 在 `frontend` 目录运行 `npm run build`，生成 `dist` 文件夹。
2.  **准备 Nginx 配置**: 创建 `nginx/nginx.conf` 文件，配置反向代理规则。
3.  **准备 `.env` 文件**: 确保生产服务器上的 `backend/.env` 文件包含所有必需的密钥。
4.  **启动服务**: 在服务器上，项目根目录运行 `docker-compose up -d --build`。

## 8. 测试策略

- **单元测试**: 对 `text_extractor.py` 和 `llm_service.py` 中的核心函数编写单元测试，模拟输入并断言输出。
- **集成测试**: 编写测试脚本，模拟 `curl` 请求，完整地走一遍 "上传 -> 轮询 -> 获取结果" 的流程，验证整个系统的数据流转是否正确。
- **端到端测试**: 使用 Cypress 或 Playwright 等工具模拟真实用户在前端的操作。

## 9. 未来改进方向

- **WebSocket 实时通知**: 用 WebSocket 替代 HTTP 轮询，实时向前端推送任务状态，提升用户体验和系统效率。
- **高级文本分块 (Chunking)**: 对超长文档（如整本书）实现基于章节或语义的智能分块，以优化 LLM 的处理效果。
- **用户认证与数据持久化**: 引入用户系统（如 JWT），并将用户的上传历史和生成的闪卡集存入数据库（如 PostgreSQL）。
- **闪卡管理**: 在前端实现对闪卡的管理功能，如编辑、删除、分组、标记掌握程度等。
- **CI/CD**: 搭建持续集成/持续部署流水线，实现代码提交后自动测试和部署。
