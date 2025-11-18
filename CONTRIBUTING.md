# 🤝 贡献指南

感谢你对 AI 闪卡生成器项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告 Bug

如果你发现了 bug，请：

1. 检查 [Issues](https://github.com/bhc6/flashcard/issues) 确认问题是否已被报告
2. 如果没有，创建新的 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 期望的行为
   - 实际的行为
   - 截图（如果适用）
   - 环境信息（操作系统、浏览器、Python 版本等）

### 建议新功能

如果你有新功能的想法：

1. 检查 [Issues](https://github.com/bhc6/flashcard/issues) 确认是否已有类似建议
2. 创建 Feature Request Issue，说明：
   - 功能描述
   - 使用场景
   - 期望的实现方式
   - 可能的替代方案

### 提交代码

1. **Fork 项目**

```bash
# 在 GitHub 上点击 Fork 按钮
git clone https://github.com/your-username/flashcard.git
cd flashcard
```

2. **创建分支**

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

3. **进行修改**

- 遵循现有的代码风格
- 添加必要的注释
- 编写或更新测试
- 更新文档

4. **测试你的修改**

```bash
# 后端测试
cd backend
source .venv/bin/activate
pytest

# 前端测试（如果有）
cd frontend
npm run test

# 手动测试
# 启动开发服务器并验证功能
```

5. **提交更改**

```bash
git add .
git commit -m "feat: add new feature" # 或 "fix: resolve bug"
```

提交信息格式：
- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式（不影响功能）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

6. **推送到 Fork**

```bash
git push origin feature/your-feature-name
```

7. **创建 Pull Request**

- 在 GitHub 上创建 PR
- 描述你的更改
- 关联相关的 Issue
- 等待代码审查

## 代码规范

### Python (后端)

- 遵循 PEP 8
- 使用有意义的变量名
- 函数和类添加文档字符串
- 最大行长度 100 字符

示例：

```python
def extract_text(file_path: str, file_extension: str) -> str:
    """
    从文件中提取文本
    
    Args:
        file_path: 文件路径
        file_extension: 文件扩展名
    
    Returns:
        提取的文本内容
    """
    pass
```

### JavaScript/Vue (前端)

- 使用 2 空格缩进
- 使用有意义的组件和变量名
- 添加必要的注释
- 遵循 Vue 3 Composition API 风格

示例：

```vue
<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'ComponentName',
  setup() {
    const data = ref(null)
    
    const fetchData = async () => {
      // 实现逻辑
    }
    
    onMounted(() => {
      fetchData()
    })
    
    return { data, fetchData }
  }
}
</script>
```

## 开发流程

### 设置开发环境

1. 运行 `./setup.sh` 初始化项目
2. 配置 `backend/.env`
3. 启动开发服务器

### 开发工作流

1. 确保你的分支是最新的：
```bash
git checkout main
git pull origin main
git checkout your-branch
git rebase main
```

2. 进行小的、原子性的提交
3. 经常推送到你的 Fork
4. 保持 PR 的范围聚焦

## 测试

### 后端测试

```bash
cd backend
source .venv/bin/activate
pytest tests/
```

### 前端测试

```bash
cd frontend
npm run test
```

### 集成测试

启动完整的应用栈并手动测试关键流程。

## 文档

- 更新 README.md（如果影响使用方式）
- 更新 TECHNICAL_DOCUMENTATION.md（如果涉及架构变更）
- 添加代码注释和文档字符串
- 更新 CHANGELOG.md

## 许可证

提交代码即表示你同意将代码以 MIT 许可证发布。

## 社区准则

- 尊重他人
- 欢迎新手
- 建设性反馈
- 保持专业

## 问题？

有任何问题，欢迎：
- 在 Issues 中提问
- 发送邮件给维护者
- 参与 Discussions

感谢你的贡献！🎉
