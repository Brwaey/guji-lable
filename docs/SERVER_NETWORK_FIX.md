# 服务器网络问题终极解决指南

## 问题总结

你遇到了两个网络问题：
1. **GitHub无法访问** - 无法pull代码
2. **npm超时** - 无法安装前端依赖

**根本原因**: 服务器在中国大陆，访问国外资源受限

---

## 🎯 一站式解决方案

### 步骤1: 配置所有镜像源（推荐）

在服务器上执行：

```bash
cd ~/guji/guji-lable

# 1. npm配置（前端依赖）
cd frontend
npm config set registry https://registry.npmmirror.com
npm config set puppeteer_download_host https://npmmirror.com/mirrors
npm cache clean --force

# 2. pip配置（后端依赖）
cd ../backend
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 3. Git配置（如果需要）
cd ..
# 使用SSH或等待后续解决方案
```

### 步骤2: 安装依赖

```bash
# 后端
cd ~/guji/guji-lable/backend
source venv/bin/activate
pip install -r requirements.txt

# 前端
cd ~/guji/guji-lable/frontend
npm install
```

---

## 🔧 分项解决方案

### A. npm解决方案

#### 方案A1: 淘宝镜像（最稳定）

```bash
# 设置镜像
npm config set registry https://registry.npmmirror.com

# 安装
npm install

# 临时使用（单次）
npm install --registry=https://registry.npmmirror.com
```

#### 方案A2: 其他镜像

```bash
# 华为云镜像
npm config set registry https://repo.huaweicloud.com/repository/npm/

# 官方中国镜像
npm config set registry https://registry.npm.taobao.org
```

#### 方案A3: 增加超时时间

```bash
# 增加超时到5分钟
npm config set fetchTimeout 300000

# 安装
npm install
```

---

### B. pip解决方案（Python）

```bash
# 创建pip配置
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# 安装依赖
cd ~/guji/guji-lable/backend
source venv/bin/activate
pip install -r requirements.txt
```

**其他pip镜像**：
- 清华：`https://pypi.tuna.tsinghua.edu.cn/simple`
- 阿里：`https://mirrors.aliyun.com/pypi/simple`
- 华中科大：`https://pypi.hustunique.com/simple`

---

### C. Git解决方案

#### 方案C1: SSH密钥（最可靠）

```bash
# 1. 生成密钥
ssh-keygen -t rsa -b 4096 -C "maxuejiao@服务器"
cat ~/.ssh/id_rsa.pub  # 复制这个

# 2. 添加到GitHub（在浏览器操作）
# https://github.com/settings/keys

# 3. 切换URL
cd ~/guji/guji-lable
git remote set-url origin git@github.com:Brwaey/guji-lable.git

# 4. Pull
git pull
```

#### 方案C2: 本地上传（临时）

**在本地Windows**：
```powershell
cd G:\Study\项目\智能教育\古籍\code\guji-lable

# 上传单个文件
scp frontend\package.json maxuejiao@172.23.40.162:~/guji/guji-lable/frontend/
scp fix_npm_network.sh maxuejiao@172.23.40.162:~/guji/guji-lable/

# 或上传整个目录
scp -r frontend maxuejiao@172.23.40.162:~/guji/guji-lable/frontend-new/
```

---

## 📋 完整配置脚本

### 在服务器执行这个一键脚本：

```bash
#!/bin/bash
# 完整配置脚本

cd ~/guji/guji-lable

echo "=== 配置npm镜像 ==="
cd frontend
npm config set registry https://registry.npmmirror.com
npm cache clean --force
npm install

echo "=== 配置pip镜像 ==="
cd ../backend
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
EOF
source venv/bin/activate
pip install -r requirements.txt

echo "=== 配置完成 ==="
echo "启动服务:"
echo "  bash start_dev_backend.sh"
echo "  bash start_dev_frontend.sh"
```

---

## ⚡ 立即执行（在服务器）

### 最简单的方案：

```bash
# 1. 配置npm镜像
cd ~/guji/guji-lable/frontend
npm config set registry https://registry.npmmirror.com
npm cache clean --force

# 2. 安装（现在应该快了）
npm install

# 3. 如果还慢，增加超时
npm install --fetchTimeout=300000
```

---

## 验证镜像配置

```bash
# 检查npm配置
npm config get registry
# 应显示: https://registry.npmmirror.com

# 检查pip配置
cat ~/.pip/pip.conf
# 应显示清华源

# 测试速度
time npm install react
time pip install numpy
```

---

## 镜像源对比

| 源 | npm速度 | pip速度 | 稳定性 |
|---|---------|---------|--------|
| 淘宝 | ⭐⭐⭐⭐⭐ | N/A | ⭐⭐⭐⭐⭐ |
| 清华 | N/A | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 阿里 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 华为 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 推荐配置（长期使用）

### 写入配置文件（永久生效）：

```bash
# npm配置
echo "registry=https://registry.npmmirror.com" > ~/.npmrc

# pip配置
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

# Git SSH配置（可选）
cat >> ~/.ssh/config << 'EOF'
Host github.com
  HostName ssh.github.com
  Port 443
  User git
EOF
```

---

## 快速命令汇总

```bash
# === npm ===
npm config set registry https://registry.npmmirror.com
npm cache clean --force
npm install

# === pip ===
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt

# === Git SSH ===
ssh-keygen
cat ~/.ssh/id_rsa.pub  # 添加到GitHub
git remote set-url origin git@github.com:Brwaey/guji-lable.git
```

---

## 常见问题

### Q: npm安装还是很慢？

**解决**：
```bash
# 使用cnpm（淘宝npm客户端）
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### Q: pip报SSL错误？

**解决**：
```bash
pip install --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt
```

### Q: 仍想使用官方源？

**解决**：配置代理（如果有）
```bash
npm config set proxy http://proxy-server:port
npm config set https-proxy https://proxy-server:port

pip install --proxy http://proxy-server:port -r requirements.txt
```

---

## 现在执行

```bash
cd ~/guji/guji-lable/frontend

# 一行命令解决npm问题
npm config set registry https://registry.npmmirror.com && npm cache clean --force && npm install
```

应该5分钟内完成安装！