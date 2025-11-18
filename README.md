# 🎓 AI 闪卡生成器

一个智能化的学习工具，能够自动从各种文档格式中提取文本，并利用 AI 生成高质量的学习闪卡。

## ✨ 核心功能

- **📁 多格式支持**: 支持 PDF、DOCX、PPTX、TXT 文件上传
- **🔍 智能文本提取**: 自动识别文档类型，支持 OCR 识别扫描件
- **🤖 AI 闪卡生成**: 使用大语言模型将文本转化为问答式闪卡
- **⚡ 异步处理**: 后台任务处理，实时状态更新
- **🎨 现代化界面**: 基于 Vue 3 的响应式用户界面

## 🏗️ 技术架构

- **前端**: Vue.js 3 + Vite + Axios
- **后端**: Flask + Celery + Redis
- **AI**: OpenAI GPT API
- **文档处理**: pypdfium2, python-docx, python-pptx
- **OCR**: Tesseract / Google Cloud Vision (可选)
- **部署**: Docker + Docker Compose + Nginx

## 📋 前置要求

### 本地开发

- Python 3.12+
- Node.js 18+
- Redis (通过 Docker)
- Tesseract OCR (可选，用于扫描件识别)

### 生产部署

- Docker
- Docker Compose

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/bhc6/flashcard.git
cd flashcard
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 OPENAI_API_KEY
```

### 3. 启动 Redis

```bash
docker run --name my-redis -d -p 6379:6379 redis:7
```

### 4. 启动后端服务

打开两个终端窗口：

**终端 1 - Celery Worker:**
```bash
cd backend
source .venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

**终端 2 - Flask API:**
```bash
cd backend
source .venv/bin/activate
python app.py
```

### 5. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 6. 访问应用

打开浏览器访问: http://localhost:3000

## 📦 生产部署

### 使用 Docker Compose

1. **准备环境变量**:
```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入生产环境的配置
```

2. **构建前端**:
```bash
cd frontend
npm install
npm run build
```

3. **启动所有服务**:
```bash
docker-compose up -d --build
```

4. **访问应用**: http://your-server-ip

服务包括：
- Nginx (端口 80/443) - 反向代理和静态文件服务
- Flask API - 后端 API 服务
- Celery Worker - 异步任务处理
- Redis - 消息队列和结果存储

## 📖 API 文档

### POST /api/generate-flashcards-async

上传文件并创建异步处理任务。

**请求**:
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF, DOCX, PPTX, TXT)

**响应** (202 Accepted):
```json
{
  "message": "文件上传成功，正在后台处理...",
  "task_id": "a33dfaf8-1d6f-46c4-90f4-685d816d8b22",
  "status_url": "http://localhost:5000/api/task-status/..."
}
```

### GET /api/task-status/<task_id>

查询任务状态和结果。

**响应示例**:
```json
{
  "state": "SUCCESS",
  "status": "完成!",
  "result": [
    {
      "question": "什么是机器学习？",
      "answer": "机器学习是人工智能的一个分支..."
    }
  ]
}
```

## 🔧 环境变量配置

在 `backend/.env` 文件中配置：

| 变量名 | 必须 | 说明 |
|--------|------|------|
| `OPENAI_API_KEY` | ✅ | OpenAI API 密钥 |
| `GOOGLE_APPLICATION_CREDENTIALS` | ❌ | Google Cloud Vision 密钥文件路径 |
| `CELERY_BROKER_URL` | ❌ | Redis 地址 (默认: redis://localhost:6379/0) |
| `CELERY_RESULT_BACKEND` | ❌ | Redis 地址 (默认: redis://localhost:6379/0) |

## 📚 项目结构

```
flashcard/
├── backend/                 # 后端代码
│   ├── services/           # 业务逻辑
│   │   ├── text_extractor.py
│   │   └── llm_service.py
│   ├── app.py              # Flask 应用入口
│   ├── requirements.txt    # Python 依赖
│   └── Dockerfile
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue 组件
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── nginx/                  # Nginx 配置
│   └── nginx.conf
├── docker-compose.yml      # Docker Compose 配置
└── TECHNICAL_DOCUMENTATION.md  # 详细技术文档
```

## 🧪 测试

```bash
# 后端单元测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

## 📝 详细文档

更多技术细节请参考 [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

bhc6

---

**注意**: 使用前请确保已配置有效的 OpenAI API Key。
