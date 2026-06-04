# 紧急方案 - 本地打包上传

由于GitHub访问问题严重，最可靠的方式是从本地上传代码到服务器。

## 方案A: 使用SCP上传（推荐）

### 步骤1: 在本地Windows打包

在本地Windows PowerShell执行：

```powershell
# 进入项目目录
cd G:\Study\项目\智能教育\古籍\code\guji-lable

# 打包（排除不需要的文件）
# 方法1: 使用PowerShell压缩
$exclude = @("node_modules", "venv", "__pycache__", ".git", "*.pyc", ".env", "logs", "annotations", "embedding_cache")
Get-ChildItem -Path . -Exclude $exclude | Compress-Archive -DestinationPath guji-lable.zip -Force

# 方法2: 使用tar（如果有Git Bash）
# tar --exclude='node_modules' --exclude='venv' --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' --exclude='logs' --exclude='annotations' --exclude='embedding_cache' -czf guji-lable.tar.gz .
```

### 步骤2: 上传到服务器

```powershell
# 上传ZIP文件
scp guji-lable.zip maxuejiao@172.23.40.162:/home/maxuejiao/

# 或使用WinSCP等图形工具上传
```

### 步骤3: 在服务器上解压

```bash
# SSH登录服务器
ssh maxuejiao@172.23.40.162

# 进入目录
cd ~/guji

# 备份现有配置
cp guji-lable/backend/.env guji-lable-env-backup 2>/dev/null

# 删除旧文件
rm -rf guji-lable

# 解压
unzip guji-lable.zip -d guji-lable

# 或如果是tar.gz
# tar -xzf guji-lable.tar.gz -C guji-lable/

# 恢复配置
cp guji-lable-env-backup guji-lable/backend/.env
```

---

## 方案B: 直接复制文件

如果不想打包，可以逐个上传关键文件：

### 只上传修改的文件

在本地Windows：
```powershell
# 使用scp上传特定文件
cd G:\Study\项目\智能教育\古籍\code\guji-lable

# 上传package.json
scp frontend\package.json maxuejiao@172.23.40.162:/home/maxuejiao/guji/guji-lable/frontend/

# 上传修复脚本
scp fix_frontend_deps.sh maxuejiao@172.23.40.162:/home/maxuejiao/guji/guji-lable/
scp start_dev_backend.sh maxuejiao@172.23.40.162:/home/maxuejiao/guji/guji-lable/
scp start_dev_frontend.sh maxuejiao@172.23.40.162:/home/maxuejiao/guji/guji-lable/
```

---

## 方案C: 配置SSH密钥（长期方案）

这是最稳定的方式，一次配置，永久使用。

### 步骤1: 在服务器生成SSH密钥

```bash
# SSH登录服务器
ssh maxuejiao@172.23.40.162

# 生成密钥（如果还没有）
ssh-keygen -t rsa -b 4096 -C "maxuejiao@skill-accessment-prod1"
# 一路回车使用默认设置

# 查看公钥
cat ~/.ssh/id_rsa.pub
# 复制整个输出（从ssh-rsa开始到邮箱结束）
```

### 步骤2: 添加到GitHub

1. 浏览器打开 https://github.com/settings/keys
2. 点击 "New SSH key"
3. Title: 填写 "Skill-Assessment-Server" 或任意名称
4. Key type: 选择 "Authentication Key"
5. Key: 粘贴刚才复制的公钥
6. 点击 "Add SSH key"

### 步骤3: 测试并使用

```bash
# 在服务器上测试
ssh -T git@github.com

# 如果看到: Hi Brwaey! You've successfully authenticated...
# 说明成功

# 切换到SSH
cd ~/guji/guji-lable
git remote set-url origin git@github.com:Brwaey/guji-lable.git

# Pull
git pull
```

---

## 快速命令汇总

### 如果你有SSH密钥，直接执行：

```bash
# 在服务器上执行
cd ~/guji/guji-lable
git remote set-url origin git@github.com:Brwaey/guji-lable.git
git pull
```

### 如果要从本地上传：

```bash
# 本地Windows PowerShell
cd G:\Study\项目\智能教育\古籍\code\guji-lable
scp -r . maxuejiao@172.23.40.162:/home/maxuejiao/guji/guji-lable-new/
```

---

## 推荐方案

**立即执行**: 方案C（配置SSH）

原因：
1. 一次配置，永久使用
2. 最稳定，不受镜像影响
3. GitHub官方支持，不会失效

**临时方案**: 方案A（本地打包）

如果急需更新代码，先用这个，然后配置SSH。

---

## 检查清单

### 在执行前确认：

- [ ] 服务器能SSH登录
- [ ] 知道GitHub用户名和密码
- [ ] 有权限添加SSH Key到GitHub
- [ ] 本地代码是最新的

### 执行后验证：

```bash
# 检查文件是否更新
cd ~/guji/guji-lable
ls -la frontend/package.json
cat frontend/package.json | grep react-virtual

# 应该看到 @tanstack/react-virtual
```