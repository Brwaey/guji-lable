# 古籍标注平台 - 快速开始指南

## 环境要求

### 后端
- Python 3.8+
- pip (Python包管理器)

### 前端
- Node.js 16+
- npm 或 yarn

### 网络
- 确保能访问内网服务器 `172.23.40.162`
- 确保能访问Embedding服务 `http://172.23.40.162:8180/v1`

---

## 快速启动

### 方式一：使用启动脚本（Windows）

#### 启动后端
```bash
双击运行 start-backend.bat
```

后端服务将在 http://localhost:8000 启动

#### 启动前端
```bash
双击运行 start-frontend.bat
```

前端服务将在 http://localhost:5173 启动

---

### 方式二：手动启动

#### 1. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

或使用 uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 访问地址

- **前端界面**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/api/docs
- **ReDoc文档**: http://localhost:8000/api/redoc

---

## 配置说明

### 后端配置

编辑 `backend/.env` 文件（从 `.env.example` 复制）：

```env
# 调试模式
DEBUG=true

# 远程服务器配置
REMOTE_SERVER_HOST=172.23.40.162
USE_SSH=false  # 如果使用SSH连接，设为true并配置用户名密码

# Embedding服务
EMBEDDING_API_URL=http://172.23.40.162:8180/v1
EMBEDDING_MODEL=embedding

# 文件路径（如果需要映射到本地）
# OCR_BASE_PATHS=/path/to/local/ocr
```

### 前端配置

前端配置在 `frontend/vite.config.ts` 中，默认代理到后端 `http://localhost:8000`

---

## 功能验证

### 1. 检查后端服务

访问 http://localhost:8000/api/health

应返回：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. 检查文件浏览

访问 http://localhost:8000/api/files/base-paths

应返回配置的文件路径列表。

### 3. 检查Embedding服务

访问 http://localhost:8000/api/similarity/api-status

应返回Embedding API的状态信息。

---

## 常见问题

### 1. 无法连接到远程服务器

**问题**: 文件浏览失败，提示连接错误

**解决方案**:
- 检查网络连接，确保能ping通 `172.23.40.162`
- 如果是Windows系统，可能需要映射网络驱动器或使用SSH连接
- 修改 `backend/config.py` 中的 `USE_SSH` 为 `true`，并配置SSH用户名密码

### 2. Embedding服务不可用

**问题**: 相似度计算失败

**解决方案**:
- 检查Embedding服务是否运行: 访问 http://172.23.40.162:8180/v1/models
- 检查配置中的API地址是否正确
- 检查网络连接

### 3. 前端无法访问后端API

**问题**: 前端显示网络错误

**解决方案**:
- 确保后端服务已启动
- 检查后端CORS配置（`backend/config.py` 中的 `CORS_ORIGINS`）
- 检查前端代理配置（`frontend/vite.config.ts`）

### 4. Python依赖安装失败

**问题**: pip install 报错

**解决方案**:
- 升级pip: `python -m pip install --upgrade pip`
- 使用国内镜像: `pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 单独安装失败的包

### 5. Node依赖安装失败

**问题**: npm install 报错

**解决方案**:
- 清除缓存: `npm cache clean --force`
- 删除node_modules重新安装: `rm -rf node_modules && npm install`
- 使用国内镜像: `npm install --registry=https://registry.npmmirror.com`

---

## 开发建议

### 后端开发

1. 启用调试模式（`DEBUG=true`）
2. 使用自动重载: `uvicorn main:app --reload`
3. 查看日志输出

### 前端开发

1. 使用React DevTools浏览器扩展
2. 查看控制台日志
3. 使用React Query DevTools

---

## 下一步

1. 访问前端界面
2. 选择OCR文件和参考文本
3. 开始计算相似度
4. 查看对比结果
5. 进行标注（功能开发中）

---

## 技术支持

如有问题，请查看：
1. 项目文档: `docs/project-plan.md`
2. API文档: http://localhost:8000/api/docs
3. GitHub Issues (待添加)