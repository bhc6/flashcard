# 🚀 部署指南

本文档提供详细的生产环境部署步骤。

## 部署方式

### 方式 1: Docker Compose 部署（推荐）

最简单的部署方式，适合大多数场景。

#### 前置要求

- 一台云服务器（Ubuntu 20.04+, 2GB+ RAM）
- Docker 和 Docker Compose
- 域名（可选，用于 HTTPS）

#### 步骤

1. **在服务器上克隆项目**

```bash
git clone https://github.com/bhc6/flashcard.git
cd flashcard
```

2. **配置环境变量**

```bash
cd backend
cp .env.example .env
nano .env  # 编辑并设置 ARK_API_KEY
cd ..
```

3. **构建前端**

```bash
cd frontend
npm install
npm run build
cd ..
```

4. **启动服务**

```bash
docker-compose up -d --build
```

5. **验证部署**

```bash
# 检查所有容器是否运行
docker-compose ps

# 查看日志
docker-compose logs -f
```

6. **访问应用**

- HTTP: `http://your-server-ip`
- 如果配置了域名和 SSL：`https://your-domain.com`

#### 管理命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service-name]

# 更新代码后重新部署
git pull
cd frontend && npm run build && cd ..
docker-compose up -d --build
```

### 方式 2: 手动部署

如果你想要更多的控制权或不使用 Docker。

#### 后端部署

1. **安装系统依赖**

```bash
sudo apt update
sudo apt install python3.12 python3-pip python3-venv redis-server tesseract-ocr tesseract-ocr-chi-sim nginx
```

2. **设置 Python 环境**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

3. **配置环境变量**

```bash
cp .env.example .env
nano .env  # 设置 ARK_API_KEY
```

4. **使用 systemd 管理服务**

创建 `/etc/systemd/system/flashcard-api.service`:

```ini
[Unit]
Description=Flashcard API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/flashcard/backend
Environment="PATH=/path/to/flashcard/backend/.venv/bin"
ExecStart=/path/to/flashcard/backend/.venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 app:app

[Install]
WantedBy=multi-user.target
```

创建 `/etc/systemd/system/flashcard-worker.service`:

```ini
[Unit]
Description=Flashcard Celery Worker
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/flashcard/backend
Environment="PATH=/path/to/flashcard/backend/.venv/bin"
ExecStart=/path/to/flashcard/backend/.venv/bin/celery -A app.celery_app worker --loglevel=INFO

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flashcard-api flashcard-worker
sudo systemctl start flashcard-api flashcard-worker
```

#### 前端部署

1. **构建前端**

```bash
cd frontend
npm install
npm run build
```

2. **配置 Nginx**

编辑 `/etc/nginx/sites-available/flashcard`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/flashcard/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300;
    }
}
```

启用站点:

```bash
sudo ln -s /etc/nginx/sites-available/flashcard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## HTTPS 配置

使用 Let's Encrypt 免费 SSL 证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 性能优化

### 1. 增加 Worker 数量

编辑 `docker-compose.yml`，增加 worker 副本：

```yaml
worker:
  deploy:
    replicas: 3
```

### 2. Redis 持久化

确保 Redis 数据持久化，避免任务丢失。

### 3. 文件上传限制

在 Nginx 配置中增加：

```nginx
client_max_body_size 50M;
```

## 监控和日志

### 查看应用日志

```bash
# Docker 部署
docker-compose logs -f backend
docker-compose logs -f worker

# 手动部署
sudo journalctl -u flashcard-api -f
sudo journalctl -u flashcard-worker -f
```

### 性能监控

考虑使用：
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- New Relic / Datadog

## 故障排查

### 问题：容器无法启动

```bash
# 查看详细日志
docker-compose logs

# 检查端口占用
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :6379
```

### 问题：任务处理失败

1. 检查 Redis 连接
2. 验证 ARK_API_KEY
3. 查看 Celery Worker 日志

### 问题：上传文件失败

1. 检查磁盘空间
2. 验证文件大小限制
3. 检查 uploads 目录权限

## 备份策略

定期备份重要数据：

```bash
# 备份 Redis 数据
docker-compose exec redis redis-cli BGSAVE

# 备份上传文件
tar -czf uploads-backup-$(date +%Y%m%d).tar.gz backend/uploads/

# 备份环境变量
cp backend/.env backend/.env.backup
```

## 扩展部署

对于高流量应用，考虑：

1. **负载均衡**: 使用多个 backend 实例 + Nginx 负载均衡
2. **Redis 集群**: 使用 Redis Sentinel 或 Redis Cluster
3. **对象存储**: 使用 AWS S3 或 MinIO 存储上传文件
4. **CDN**: 使用 CloudFlare 或 AWS CloudFront

## 安全建议

1. ✅ 使用 HTTPS
2. ✅ 定期更新依赖
3. ✅ 使用防火墙限制端口访问
4. ✅ 设置强密码和密钥
5. ✅ 定期备份数据
6. ✅ 监控异常活动
7. ✅ 限制上传文件大小和类型

## 成本估算

基础部署（小型应用）：

- VPS (2GB RAM, 1 CPU): $5-10/月
- 域名: $10-15/年
- SSL 证书: 免费 (Let's Encrypt)
- OpenAI API: 按使用量付费

总计: 约 $10/月 + API 费用

## 联系支持

遇到问题？

1. 查看 [GitHub Issues](https://github.com/bhc6/flashcard/issues)
2. 阅读 [技术文档](./TECHNICAL_DOCUMENTATION.md)
3. 提交新的 Issue
