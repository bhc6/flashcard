# Anki 闪卡生成器

一个基于 Vue3 + Flask 的 Anki 闪卡生成工具，支持从文本生成闪卡、AI 增强、多格式导出。

## ✨ 功能特性

- 📝 **文本输入**: 粘贴文本或 JSON 数据生成闪卡
- 🤖 **AI 生成**: 使用 AI 从文本自动生成问答闪卡
- ✏️ **在线编辑**: 添加、编辑、删除闪卡
- 🎴 **多种视图**: 列表视图、卡片预览、学习模式
- 📤 **多格式导出**: JSON、TXT、TSV、CSV
- 🎯 **学习模式**: 翻转卡片、标记掌握程度

## 📋 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

## 🚀 快速启动

### 1. 克隆项目

```bash
git clone https://github.com/bhc6/flashcard.git
cd Anki_FlashCard_Generator
```

### 2. 配置环境变量

创建 `.env` 文件并添加火山引擎 API 密钥（可选，用于 AI 功能）：

```bash
cp .env.example .env
```

### 3. 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 5. 启动服务

**终端 1 - 启动后端 API（端口 5000）：**

```bash
cd /home/bhc6/ankicard/Anki_FlashCard_Generator
source .venv/bin/activate
python api.py
```

**终端 2 - 启动前端（端口 3000）：**

```bash
cd /home/bhc6/ankicard/Anki_FlashCard_Generator/frontend
npm run dev
```

### 6. 访问应用

打开浏览器访问：**http://localhost:3000**

## 🔗 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:3000 | Vue3 用户界面 |
| 后端 API | http://localhost:5000 | Flask API 服务 |
| 健康检查 | http://localhost:5000/api/health | 检查服务状态 |

## 📖 使用说明

### 输入方式

1. **粘贴文本**: 直接粘贴文本，使用 AI 生成闪卡
2. **JSON 数据**: 粘贴 JSON 格式的闪卡数据

### JSON 格式示例

```json
[
  {"question": "什么是 Vue3?", "answer": "Vue3 是一个渐进式 JavaScript 框架"},
  {"question": "什么是 Flask?", "answer": "Flask 是一个轻量级 Python Web 框架"}
]
```

### 导出格式

- **JSON**: 标准 JSON 格式
- **TXT**: Anki 导入格式（问题;答案）
- **TSV**: 制表符分隔格式
- **CSV**: 逗号分隔格式

## 🛠️ API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/generate` | POST | AI 生成闪卡 |
| `/api/flashcards` | GET/POST | 获取/保存闪卡 |
| `/api/flashcards/<index>` | PUT/DELETE | 更新/删除闪卡 |
| `/api/flashcards/add` | POST | 添加闪卡 |
| `/api/enhance` | POST | AI 增强闪卡 |
| `/api/export` | POST | 导出闪卡 |
| `/api/import-json` | POST | 导入 JSON |
| `/api/parse-text` | POST | 解析文本 |

## 📁 项目结构

```
Anki_FlashCard_Generator/
├── api.py                      # Flask 后端 API
├── Anki_flashcards_creator.py  # 核心生成逻辑
├── Anki_flashcards_from_json.py # JSON 处理逻辑
├── requirements.txt            # Python 依赖
├── .env                        # 环境变量配置
├── frontend/                   # Vue3 前端
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── api/
│       │   └── index.js
│       └── components/
│           ├── FlashcardItem.vue
│           ├── FlashcardPreview.vue
│           └── StudyMode.vue
└── SOURCE_DOCUMENTS/           # 源文档目录
```

## ❓ 常见问题

### 后端启动失败

```bash
# 检查端口是否被占用
lsof -i :5000

# 检查 Python 环境
python --version
pip list
```

### 前端启动失败

```bash
# 清除缓存重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API 连接失败

确保后端服务正在运行，并检查 CORS 配置。

## 📄 许可证

MIT License