# 服务器部署指南

## 你的问题回答

### 1. 项目迁移到服务器能正常运行吗？

**完全可以！而且更简单。**

#### 在服务器上部署的优势：

| 项目 | Windows本地 | Linux服务器 |
|------|------------|------------|
| **文件路径** | ❌ 需要SSH/映射 | ✅ 直接访问 |
| **Embedding API** | ❌ 内网限制 | ✅ 直接访问 |
| **网络延迟** | ❌ 网络开销 | ✅ 本地调用 |
| **权限问题** | ⚠️ 可能遇到 | ✅ 通常已解决 |

#### 在服务器上部署的配置：

```env
# backend/.env (服务器版本)
DEBUG=true

# 文件直接访问（不需要SSH）
USE_SSH=false

# Embedding API内网地址
EMBEDDING_API_URL=http://172.23.40.162:8180/v1
# 或者使用localhost（如果在同一台机器）
# EMBEDDING_API_URL=http://localhost:8180/v1
EMBEDDING_MODEL=embedding

# 文件路径（保持原配置即可）
# OCR_BASE_PATHS和REFERENCE_BASE_PATH已经在config.py中配置正确
```

---

## 服务器部署步骤

### 方案A：完整部署（推荐）

#### 1. 上传项目到服务器

```bash
# 方式1: 使用scp
scp -r G:\Study\项目\智能教育\古籍\code\guji-lable maxuejiao@172.23.40.162:/home/maxuejiao/guji-lable

# 方式2: 使用rsync（推荐，可增量同步）
rsync -avz --progress G:\Study\项目\智能教育\古籍\code\guji-lable maxuejiao@172.23.40.162:/home/maxuejiao/

# 方式3: 使用Git（如果项目已推送到仓库）
ssh maxuejiao@172.23.40.162
cd /home/maxuejiao
git clone <你的仓库地址>
```

#### 2. 安装依赖

```bash
ssh maxuejiao@172.23.40.162
cd /home/maxuejiao/guji-lable

# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

#### 3. 配置环境

```bash
# 创建.env文件
cat > backend/.env << 'EOF'
DEBUG=true
USE_SSH=false
EMBEDDING_API_URL=http://172.23.40.162:8180/v1
EMBEDDING_MODEL=embedding
EOF

# 或者使用localhost（如果Embedding服务在同一台机器）
# EMBEDDING_API_URL=http://localhost:8180/v1
```

#### 4. 测试连接

```bash
python test_connection.py
```

#### 5. 启动服务

**开发模式：**
```bash
# 后端
cd backend
source venv/bin/activate
python main.py

# 前端（另一个终端）
cd frontend
npm run dev -- --host 0.0.0.0
```

**生产模式：**
```bash
# 后端（使用gunicorn或uvicorn）
cd backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &

# 前端（构建后使用nginx或直接托管）
cd frontend
npm run build
# 将dist目录配置到nginx
```

---

### 方案B：本地开发+服务器部署混合

#### 架构：
- **前端**: 部署在服务器，供内网用户访问
- **后端**: 部署在服务器，访问本地文件和Embedding服务
- **文件**: 直接访问服务器本地路径

#### 配置步骤：

1. **修改 `frontend/vite.config.ts`**：
```typescript
server: {
  port: 5173,
  host: '0.0.0.0',  // 允许外网访问
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
},
```

2. **修改 `backend/config.py`**：
```python
# 允许所有内网IP访问
CORS_ORIGINS: List[str] = ["*"]  # 或者指定具体的内网IP段
```

---

## 配置文件管理

### 关于 `.env.template` 文件

#### 是否应该gitignore？

**不应该！** 模板文件应该提交到git：

| 文件 | 是否提交git | 原因 |
|------|-----------|------|
| `.env` | ❌ 不提交 | 包含敏感信息（密码等） |
| `.env.template` | ✅ 提交 | 模板，不含敏感信息 |
| `.env.example` | ✅ 提交 | 示例配置 |

#### 正确的管理方式：

```
.gitignore 内容：
.env           # 忽略实际配置
.env.local     # 忽略本地配置
!.env.template # 不忽略模板
!.env.example  # 不忽略示例
```

#### 使用流程：

1. **开发者克隆项目**
2. **复制模板文件**：
   ```bash
   cp backend/.env.template backend/.env
   ```
3. **编辑 `.env` 填入实际配置**
4. **`.env` 不会被提交到git**

---

## 快速迁移脚本

创建 `deploy_to_server.sh`：

```bash
#!/bin/bash
# 部署脚本 - 在Windows Git Bash或Linux上运行

SERVER_USER="maxuejiao"
SERVER_HOST="172.23.40.162"
REMOTE_DIR="/home/maxuejiao/guji-lable"

echo "=== 部署古籍标注平台到服务器 ==="

# 1. 同步代码
echo "1. 同步代码..."
rsync -avz --exclude='*.pyc' --exclude='__pycache__' --exclude='node_modules' --exclude='.env' --exclude='venv' ./ ${SERVER_USER}@${SERVER_HOST}:${REMOTE_DIR}

# 2. 安装依赖
echo "2. 安装后端依赖..."
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${REMOTE_DIR}/backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

echo "3. 安装前端依赖..."
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${REMOTE_DIR}/frontend && npm install"

# 4. 创建配置
echo "4. 创建配置文件..."
ssh ${SERVER_USER}@${SERVER_HOST} "cat > ${REMOTE_DIR}/backend/.env << 'EOF'
DEBUG=true
USE_SSH=false
EMBEDDING_API_URL=http://localhost:8180/v1
EMBEDDING_MODEL=embedding
EOF"

# 5. 测试
echo "5. 测试连接..."
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${REMOTE_DIR} && python test_connection.py"

echo "=== 部署完成 ==="
echo "启动服务:"
echo "  后端: ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${REMOTE_DIR}/backend && source venv/bin/activate && python main.py'"
echo "  前端: ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${REMOTE_DIR}/frontend && npm run dev -- --host 0.0.0.0'"
```

---

## 部署检查清单

### 服务器环境要求

- [ ] Python 3.8+
- [ ] Node.js 16+
- [ ] 访问文件路径权限
- [ ] 访问Embedding服务权限

### 验证步骤

1. **文件访问**
   ```bash
   ls /home/maxuejiao/guji/mineru_ocr/
   ls /home/maxuejiao/guji/shidianguji/
   ```

2. **Embedding服务**
   ```bash
   curl http://localhost:8180/v1/models
   # 或
   curl http://172.23.40.162:8180/v1/models
   ```

3. **运行测试**
   ```bash
   python test_connection.py
   ```

---

## 推荐方案

**我的建议：直接部署到服务器**

理由：
1. **更简单** - 不需要SSH配置，直接访问文件
2. **更快** - Embedding API本地调用，无网络延迟
3. **更稳定** - 没有网络连接问题
4. **更安全** - 敏感信息不暴露到外网

立即执行：
```bash
# 1. 上传项目
scp -r G:\Study\项目\智能教育\古籍\code\guji-lable maxuejiao@172.23.40.162:/home/maxuejiao/

# 2. SSH登录
ssh maxuejiao@172.23.40.162

# 3. 进入目录
cd /home/maxuejiao/guji-lable

# 4. 创建配置
cat > backend/.env << 'EOF'
DEBUG=true
USE_SSH=false
EMBEDDING_API_URL=http://localhost:8180/v1
EMBEDDING_MODEL=embedding
EOF

# 5. 安装并运行
cd backend && pip install -r requirements.txt && python main.py
```