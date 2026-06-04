# 连接问题诊断与解决方案

## 问题分析

根据测试结果，你遇到了以下问题：

### 1. Embedding API超时
```
❌ 请求超时
http://172.23.40.162:8180/v1
```

**可能原因**：
- 8180端口服务未启动
- 防火墙阻止了8180端口
- 服务监听地址配置问题

### 2. 文件路径无法访问
```
❌ 路径不存在
/home/maxuejiao/guji/mineru_ocr/...
```

**根本原因**：
你在Windows系统上运行，但配置的是Linux服务器路径。Windows无法直接访问Linux路径。

---

## 解决方案

### 方案一：使用SSH访问（推荐）

#### 步骤1：获取SSH登录凭证

联系服务器管理员，获取：
- 用户名
- 密码 或 SSH密钥

#### 步骤2：修改配置

编辑 `backend/.env` 文件：

```env
# 启用SSH连接
USE_SSH=true
REMOTE_SERVER_USER=你的用户名
REMOTE_SERVER_PASSWORD=你的密码
```

或者修改 `backend/config.py`：

```python
USE_SSH: bool = True
REMOTE_SERVER_USER: str = "your_username"
REMOTE_SERVER_PASSWORD: str = "your_password"
```

#### 步骤3：测试SSH连接

```bash
# 在Windows PowerShell中测试
ssh 用户名@172.23.40.162
```

如果能登录，SSH配置正确。

---

### 方案二：映射网络驱动器（仅适用于SMB共享）

如果服务器配置了SMB共享：

#### 步骤1：映射网络驱动器

1. 打开"此电脑"
2. 点击"映射网络驱动器"
3. 输入：`\\172.23.40.162\共享名`
4. 输入用户名密码

#### 步骤2：修改配置使用映射路径

假设映射到 `Z:` 盘：

```python
OCR_BASE_PATHS: List[str] = [
    "Z:\\mineru_ocr\\二十四史附清史稿_ocr",
    # ...
]
```

---

### 方案三：验证Embedding API

#### 步骤1：检查服务是否运行

SSH登录到服务器后执行：

```bash
# 检查8180端口
netstat -tuln | grep 8180

# 或者
ss -tuln | grep 8180

# 检查进程
ps aux | grep 8180
```

#### 步骤2：检查服务监听地址

服务可能只监听在localhost，需要修改为 `0.0.0.0`

#### 步骤3：检查防火墙

```bash
# 检查防火墙状态
sudo ufw status

# 如果启用了防火墙，开放8180端口
sudo ufw allow 8180/tcp
```

#### 步骤4：测试API

在服务器上直接测试：

```bash
curl http://localhost:8180/v1/models
```

如果能访问，说明服务正常，只是网络/防火墙问题。

---

## 快速测试方案

### 修改配置以使用SSH

创建 `backend/.env` 文件：

```env
DEBUG=true
USE_SSH=true
REMOTE_SERVER_HOST=172.23.40.162
REMOTE_SERVER_USER=maxuejiao
REMOTE_SERVER_PASSWORD=你的密码
```

**注意**：请替换为实际的密码。

### 验证配置

再次运行测试：

```bash
python test_connection.py
```

如果SSH配置正确，应该能看到文件访问测试通过。

---

## Embedding API的替代方案

如果8180端口的Embedding服务确实无法访问，可以考虑：

### 选项1：使用其他Embedding服务

修改 `backend/config.py`：

```python
# 使用OpenAI API
EMBEDDING_API_URL: str = "https://api.openai.com/v1"
EMBEDDING_MODEL: str = "text-embedding-ada-002"
```

需要在 `.env` 中添加OpenAI API Key。

### 选项2：部署本地Embedding服务

在本地部署一个Embedding服务（如使用sentence-transformers）。

### 选项3：跳过Embedding测试

暂时跳过Embedding功能，先使用文件浏览和标注功能。

修改 `test_connection.py`，注释掉Embedding测试部分。

---

## 推荐的诊断步骤

### 1. 先测试SSH连接

```bash
ssh maxuejiao@172.23.40.162
```

如果能登录，记录用户名，配置到 `.env`。

### 2. 登录后检查文件

```bash
ls -la /home/maxuejiao/guji/mineru_ocr/
```

确认路径是否存在。

### 3. 检查Embedding服务

```bash
curl http://localhost:8180/v1/models
curl http://172.23.40.162:8180/v1/models
```

对比结果，判断是服务问题还是网络问题。

### 4. 检查端口

```bash
netstat -tuln | grep 8180
```

如果显示 `127.0.0.1:8180`，说明只监听本地，需要修改服务配置。

---

## 需要的信息

请提供以下信息以便进一步诊断：

1. **SSH登录信息**
   - 是否能SSH登录到172.23.40.162？
   - 用户名是什么？
   
2. **Embedding服务状态**
   - 在服务器上执行 `curl http://localhost:8180/v1/models` 的结果
   - 在服务器上执行 `netstat -tuln | grep 8180` 的结果
   
3. **文件路径确认**
   - 在服务器上执行 `ls /home/maxuejiao/guji/` 的结果

提供这些信息后，我可以给出更精确的配置方案。