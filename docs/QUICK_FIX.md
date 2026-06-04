# 快速解决问题指南

## 你遇到的问题

根据 `test_connection.py` 的输出：

✅ **SSH连接成功** - 说明网络正常
❌ **Embedding API超时** - 8180端口无法访问
❌ **文件路径不存在** - Linux路径在Windows上无效

---

## 立即解决方案（5分钟）

### 第一步：创建SSH配置

在项目根目录创建 `backend/.env` 文件：

```env
DEBUG=true

USE_SSH=true
REMOTE_SERVER_HOST=172.23.40.162
REMOTE_SERVER_USER=你的用户名
REMOTE_SERVER_PASSWORD=你的密码

EMBEDDING_API_URL=http://172.23.40.162:8180/v1
EMBEDDING_MODEL=embedding
```

**重要**: 替换 `你的用户名` 和 `你的密码` 为实际的SSH登录凭证。

### 第二步：测试配置

```bash
python test_connection.py
```

如果文件访问测试通过，说明SSH配置成功。

### 第三步：检查Embedding服务

SSH登录到服务器：

```bash
ssh 你的用户名@172.23.40.162
```

然后在服务器上执行：

```bash
# 测试服务
curl http://localhost:8180/v1/models

# 检查端口
netstat -tuln | grep 8180
```

**情况A**: 如果 `curl` 成功但显示 `127.0.0.1:8180`
- 说明服务只监听本地，需要修改服务配置为监听 `0.0.0.0`

**情况B**: 如果 `curl` 失败
- 说明服务未启动或已停止，需要启动服务

**情况C**: 如果 `curl` 成功且显示 `0.0.0.0:8180`
- 说明服务正常，可能是防火墙问题
- 执行: `sudo ufw allow 8180/tcp`

---

## 如果没有SSH账号

请联系服务器管理员 `172.23.40.162` 的负责人：

1. 申请SSH登录账号
2. 确认文件路径是否正确
3. 确认Embedding服务地址和端口

---

## 使用向导工具

我创建了三个工具帮助你：

### 1. 配置助手（交互式）
```bash
python config_helper.py
```

### 2. 快速配置向导（自动检测）
```bash
python setup_wizard.py
```

### 3. 连接测试（验证配置）
```bash
python test_connection.py
```

---

## 启动顺序

### 1. 先解决文件访问
- 配置SSH或映射网络驱动器
- 运行 `test_connection.py` 验证

### 2. 再处理Embedding服务
- SSH登录服务器检查服务状态
- 或联系管理员确认服务地址

### 3. 最后启动应用
```bash
# 后端
cd backend
python main.py

# 前端（另一个终端）
cd frontend
npm install
npm run dev
```

---

## 需要帮助？

请提供以下信息：

1. **SSH登录信息**
   - 用户名
   - 能否成功登录

2. **服务器检查结果**
   ```bash
   curl http://localhost:8180/v1/models
   netstat -tuln | grep 8180
   ```

3. **文件路径确认**
   ```bash
   ls /home/maxuejiao/guji/
   ```

提供这些信息后，我可以给出精确的配置方案。