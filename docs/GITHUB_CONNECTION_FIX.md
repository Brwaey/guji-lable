# GitHub连接问题解决指南

## 问题诊断

错误信息：
```
Failed to connect to github.com port 443 after 132944 ms: Couldn't connect to server
```

**原因**：服务器无法访问GitHub（常见于中国大陆服务器）

---

## 解决方案

### 方案1: 使用SSH（最稳定）

#### 步骤1: 检查SSH密钥
```bash
# 在服务器上执行
ls -la ~/.ssh/id_rsa*
```

**情况A: 有密钥**
- 继续"步骤3"

**情况B: 没有密钥**
- 生成SSH密钥：
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# 一路回车使用默认设置
```

#### 步骤2: 添加公钥到GitHub
```bash
# 查看公钥
cat ~/.ssh/id_rsa.pub

# 复制输出的内容（以ssh-rsa开头）
```

然后：
1. 打开 https://github.com/settings/keys
2. 点击 "New SSH key"
3. 粘贴公钥内容
4. 保存

#### 步骤3: 切换到SSH
```bash
cd ~/guji/guji-lable

# 切换远程仓库到SSH
git remote set-url origin git@github.com:Brwaey/guji-lable.git

# 测试连接
ssh -T git@github.com

# 如果成功，会看到: Hi Brwaey! You've successfully authenticated...

# Pull
git pull
```

---

### 方案2: 使用GitHub镜像（快速）

```bash
cd ~/guji/guji-lable

# 使用国内镜像
git remote set-url origin https://gitclone.com/github.com/Brwaey/guji-lable.git

# Pull
git pull
```

**其他可用镜像**：
- `https://hub.fastgit.xyz/Brwaey/guji-lable.git`
- `https://github.com.cnpmjs.org/Brwaey/guji-lable.git`

---

### 方案3: 配置代理（如果有代理）

```bash
# 如果你有HTTP代理
git config --global http.proxy http://proxy-server:port
git config --global https.proxy https://proxy-server:port

# Pull
git pull
```

---

### 方案4: 直接在服务器重新克隆

如果Git仓库问题太多，直接重新克隆：

```bash
cd ~/guji

# 备份现有配置
cp guji-lable/backend/.env guji-lable-env-backup

# 删除旧仓库
rm -rf guji-lable

# 使用镜像重新克隆
git clone https://gitclone.com/github.com/Brwaey/guji-lable.git

# 恢复配置
cp guji-lable-env-backup guji-lable/backend/.env
```

---

## 推荐方案对比

| 方案 | 速度 | 稳定性 | 配置难度 | 推荐度 |
|------|------|--------|---------|--------|
| SSH | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 镜像 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 代理 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 重克隆 | N/A | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 快速操作（推荐）

### 在服务器上执行：

```bash
# 方式1: 使用脚本自动修复
cd ~/guji/guji-lable
bash fix_github_connection.sh

# 方式2: 手动切换到SSH
cd ~/guji/guji-lable
git remote set-url origin git@github.com:Brwaey/guji-lable.git
git pull

# 方式3: 使用镜像
cd ~/guji/guji-lable
git remote set-url origin https://gitclone.com/github.com/Brwaey/guji-lable.git
git pull
```

---

## 验证成功

```bash
# 测试连接
git ls-remote origin

# 应该看到类似输出：
# 从 github.com:Brwaey/guji-lable.git
# <hash>  HEAD
# <hash>  refs/heads/main
```

---

## 常见问题

### Q: SSH密钥已经添加到GitHub，但测试失败

**检查SSH配置**：
```bash
# 测试SSH连接
ssh -T git@github.com

# 如果失败，检查SSH配置
cat ~/.ssh/config

# 如果没有，创建一个
cat > ~/.ssh/config << 'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa
  TCPKeepAlive yes
  ServerAliveInterval 60
  ServerAliveCountMax 10
EOF

chmod 600 ~/.ssh/config
```

### Q: 镜像速度也慢

**尝试不同镜像**：
```bash
# 测试不同镜像的速度
time curl -I https://gitclone.com
time curl -I https://hub.fastgit.xyz
time curl -I https://github.com.cnpmjs.org

# 选择最快的
```

### Q: 公司网络限制严格

**解决方案**：
1. 在本地Windows下载ZIP包
2. 上传到服务器
3. 解压覆盖

```bash
# 在Windows本地
# 下载 https://github.com/Brwaey/guji-lable/archive/refs/heads/main.zip

# 上传到服务器
scp main.zip maxuejiao@172.23.40.162:/home/maxuejiao/

# 在服务器上
cd ~/guji
unzip main.zip
mv guji-lable-main guji-lable-new
cp guji-lable/backend/.env guji-lable-new/backend/.env
```

---

## 长期解决方案

### 配置Git使用多个远程

```bash
# 添加GitHub官方（SSH）
git remote add github git@github.com:Brwaey/guji-lable.git

# 添加镜像
git remote add mirror https://gitclone.com/github.com/Brwaey/guji-lable.git

# 拉取时选择
git pull github main  # 从GitHub拉取
git pull mirror main  # 从镜像拉取
```

---

## 立即执行（推荐）

**最快解决方案 - 使用镜像**：

```bash
cd ~/guji/guji-lable
git remote set-url origin https://gitclone.com/github.com/Brwaey/guji-lable.git
git pull
```

这应该立即解决问题！如果镜像也慢，我们再配置SSH。