# Git Pull卡住问题解决指南

## 常见原因

### 1. Git锁文件未清理
**症状**: Git操作卡住，提示"Waiting for lock"
**原因**: 之前的Git操作异常中断，留下了锁文件

**解决**:
```bash
# 检查锁文件
ls -la .git/index.lock

# 删除锁文件
rm -f .git/index.lock

# 重新pull
git pull
```

### 2. Git进程卡死
**症状**: Pull命令无响应
**原因**: Git进程僵死

**解决**:
```bash
# 查找Git进程
ps aux | grep git

# 终止进程
pkill -9 git

# 或终止特定PID
kill -9 <PID>

# 重新pull
git pull
```

### 3. 网络连接问题
**症状**: 连接远程仓库超时
**原因**: 网络慢或防火墙

**解决**:
```bash
# 测试连接
git ls-remote origin

# 增加超时
export GIT_CURL_VERBOSE=1
export GIT_TRACE=1

# 使用SSH而非HTTPS
git remote set-url origin git@github.com:user/repo.git
```

### 4. 大文件传输慢
**症状**: Pull进行中但很慢
**原因**: 传输大文件（如node_modules）

**解决**:
```bash
# 检查是否包含大文件
git ls-files | xargs du -sh | sort -h

# 使用浅克隆
git pull --depth=1

# 或部分克隆
git clone --filter=blob:none --sparse origin
```

### 5. 本地有未提交更改
**症状**: Pull失败提示有更改
**原因**: 本地修改未提交

**解决**:
```bash
# 查看状态
git status

# 临时保存更改
git stash

# Pull
git pull

# 恢复更改
git stash pop

# 或强制覆盖本地
git reset --hard HEAD
git pull
```

---

## 快速诊断步骤

### 在服务器上执行：

```bash
cd ~/guji/guji-lable

# 1. 检查Git进程
ps aux | grep git

# 2. 检查锁文件
ls -la .git/index.lock

# 3. 测试远程连接
git ls-remote origin

# 4. 查看Git状态
git status

# 5. 查看网络连接
netstat -tuln | grep 443  # HTTPS
netstat -tuln | grep 22   # SSH
```

---

## 根据症状选择方案

### 症状A: "Waiting for lock" 或完全无响应

```bash
# 诊断脚本
bash diagnose_git.sh

# 或手动检查
rm -f .git/index.lock
pkill -9 git
git pull
```

### 症状B: 有进度但很慢

```bash
# 查看详细输出
GIT_TRACE=1 git pull

# 检查是否传输大文件
git ls-files | grep -E "node_modules|\.pyc|venv"
```

### 症状C: "error: Your local changes..."

```bash
# 查看更改
git status
git diff

# 保存或丢弃更改
git stash      # 保存
git reset --hard  # 丢弃
```

---

## 推荐的Git配置

### 本地和服务器都应该配置：

```bash
# 推送时自动设置上游
git config --global push.autoSetupRemote true

# 使用SSH而非HTTPS
git remote set-url origin git@github.com:user/repo.git

# 配置超时
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

# 配置SSH超时
echo "Host github.com
  TCPKeepAlive yes
  ServerAliveInterval 60
  ServerAliveCountMax 10" >> ~/.ssh/config
```

---

## 预防措施

### 在推送前（本地）

```bash
# 1. 确认要推送的内容
git status
git diff

# 2. 确认不包含敏感文件
cat backend/.env  # 应该是模板，不是实际配置

# 3. 确认.gitignore生效
git check-ignore backend/.env frontend/node_modules

# 4. 推送
git add .
git commit -m "Update package.json"
git push
```

### 在pull前（服务器）

```bash
# 1. 确认没有未提交的重要更改
git status

# 2. 如果有更改，先保存
git stash

# 3. Pull
git pull

# 4. 检查是否有冲突
git status

# 5. 如果需要，恢复保存的更改
git stash pop
```

---

## 使用诊断脚本

我创建了两个诊断脚本：

### 1. diagnose_git.sh - 诊断问题
```bash
cd ~/guji/guji-lable
bash diagnose_git.sh
```

输出会告诉你：
- Git状态
- 是否有锁文件
- 是否有未提交更改
- 远程连接是否正常

### 2. fix_git_pull.sh - 自动修复
```bash
cd ~/guji/guji-lable
bash fix_git_pull.sh
```

会自动：
- 删除锁文件
- 终止卡死的进程
- 清理Git状态
- 重新拉取代码

---

## 最佳实践

### 推荐的工作流程：

```bash
# 本地开发
git add .
git commit -m "描述"
git push

# 服务器部署
cd ~/guji/guji-lable
git stash            # 如果有本地配置更改
git pull
git stash pop        # 恢复服务器特定配置
```

### 需要在服务器上保留的文件：

- `backend/.env` - 服务器配置（已在.gitignore）
- `backend/venv/` - Python虚拟环境（已在.gitignore）
- `frontend/node_modules/` - Node依赖（已在.gitignore）
- `logs/` - 日志文件（已在.gitignore）

这些文件不会通过Git传输，避免冲突。

---

## 紧急情况处理

### 如果Git完全无法使用：

```bash
# 重新克隆
cd ~
mv guji/guji-lable guji/guji-lable-backup
git clone git@github.com:user/guji-lable.git guji/guji-lable

# 恢复服务器配置
cp guji/guji-lable-backup/backend/.env guji/guji-lable/backend/.env
```

---

## 常见问题FAQ

### Q: 为什么本地能push但服务器pull卡住？

A: 可能原因：
1. 服务器网络慢（国内访问GitHub慢）
2. 服务器防火墙限制
3. SSH密钥问题

**解决**: 使用国内镜像或VPN，或检查SSH配置

### Q: Pull时提示"cannot lock ref"

A: Git引用损坏
```bash
git update-ref -d refs/heads/main
git fetch origin
```

### Q: 如何查看Git在做什么？

A: 使用详细输出
```bash
GIT_TRACE=1 GIT_CURL_VERBOSE=1 git pull
```

---

## 需要帮助？

如果问题仍未解决，请提供：

1. 诊断脚本输出：
   ```bash
   bash diagnose_git.sh > git_diagnosis.txt
   cat git_diagnosis.txt
   ```

2. Git详细信息：
   ```bash
   git status
   git remote -v
   ps aux | grep git
   ls -la .git/
   ```

3. 网络状态：
   ```bash
   ping github.com
   curl -I https://github.com
   ```