# 服务器部署常见问题解决

## 问题：npm install 报错

### 错误信息：
```
npm ERR! notarget No matching version found for @types/react-virtualized@^9.22.5
```

### 原因：
- `@types/react-virtualized` 包版本不存在
- react-virtualized 是较老的虚拟列表库

### 解决方案：

#### 方案A：自动修复（推荐）

```bash
cd ~/guji/guji-lable
bash fix_frontend_deps.sh
```

#### 方案B：手动修复

```bash
cd ~/guji/guji-lable/frontend

# 1. 清理旧依赖
rm -rf node_modules package-lock.json

# 2. 清理npm缓存
npm cache clean --force

# 3. 重新安装（已更新package.json）
npm install
```

#### 方案C：使用国内镜像

```bash
# 设置淘宝镜像
npm config set registry https://registry.npmmirror.com

# 安装
npm install

# 或临时使用
npm install --registry=https://registry.npmmirror.com
```

---

## 更新的依赖包

我已经将 `react-virtualized` 替换为更现代的库：

| 旧包 | 新包 | 说明 |
|------|------|------|
| `react-virtualized` | `@tanstack/react-virtual` | 更现代、更轻量 |
| `@types/react-virtualized` | 移除 | 不再需要 |

**优点**：
- `@tanstack/react-virtual` 是现代虚拟列表库
- TypeScript支持更好
- 性能更优
- 维护更活跃

---

## 快速启动指南

### 1. 修复依赖
```bash
cd ~/guji/guji-lable
bash fix_frontend_deps.sh
```

### 2. 启动后端
```bash
# 开发模式（前台运行，可看日志）
bash start_dev_backend.sh

# 或生产模式（后台运行）
bash start_server.sh
```

### 3. 启动前端（新终端）
```bash
# 开发模式
bash start_dev_frontend.sh

# 或手动启动
cd frontend
npm run dev -- --host 0.0.0.0
```

---

## 验证服务

### 后端验证

```bash
curl http://localhost:8000/api/health
```

期望输出：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 前端验证

浏览器访问：http://172.23.40.162:5173

---

## 常见问题

### Q1: npm安装很慢

**解决**：使用国内镜像
```bash
npm config set registry https://registry.npmmirror.com
```

### Q2: Python包安装失败

**解决**：使用国内镜像
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 端口被占用

**解决**：检查并停止占用端口的进程
```bash
# 检查8000端口
netstat -tuln | grep 8000
lsof -i :8000

# 停止进程
kill -9 <PID>
```

### Q4: 权限不足

**解决**：
```bash
# 确保有权限访问文件目录
ls -la ~/guji/mineru_ocr/
ls -la ~/guji/shidianguji/

# 如果权限不足，联系管理员或使用正确的用户
```

---

## 完整启动流程

```bash
# 1. SSH登录
ssh maxuejiao@172.23.40.162

# 2. 进入项目目录
cd ~/guji/guji-lable

# 3. 修复依赖（首次运行）
bash fix_frontend_deps.sh

# 4. 启动后端
bash start_dev_backend.sh

# 5. 启动前端（新SSH连接）
ssh maxuejiao@172.23.40.162
cd ~/guji/guji-lable
bash start_dev_frontend.sh
```

---

## 日志查看

```bash
# 后端日志（如果使用后台模式）
tail -f ~/guji/guji-lable/logs/backend.log

# 或实时查看
cd ~/guji/guji-lable/backend
source venv/bin/activate
python main.py  # 输出会直接显示
```

---

## 停止服务

```bash
# 如果是后台运行
# 找到进程ID
ps aux | grep "python main.py"
ps aux | grep "npm run dev"

# 停止进程
kill <PID>

# 或强制停止
kill -9 <PID>
```

---

## 目录结构确认

```bash
# 确认文件目录存在
ls ~/guji/mineru_ocr/
ls ~/guji/paddleocrvl_ocr/
ls ~/guji/shidianguji/

# 确认项目目录
ls ~/guji/guji-lable/
ls ~/guji/guji-lable/backend/
ls ~/guji/guji-lable/frontend/
```

---

## 需要帮助？

如果遇到其他问题，请提供：
1. 错误信息完整输出
2. 执行的命令
3. 系统环境信息：
   ```bash
   uname -a
   python3 --version
   npm --version
   ```