#!/bin/bash
# Git卡住问题快速解决方案

echo "========================================"
echo "Git Pull 快速修复"
echo "========================================"
echo

echo "常见原因和解决方案:"
echo

echo "【方案1】删除Git锁文件"
echo "  适用: 之前的Git操作异常中断"
if [ -f ".git/index.lock" ]; then
    echo "  发现锁文件，删除中..."
    rm -f .git/index.lock
    echo "  ✓ 锁文件已删除"
else
    echo "  未发现锁文件"
fi
echo

echo "【方案2】强制终止Git进程"
echo "  适用: Git进程卡死"
echo "  查找Git进程:"
ps aux | grep git | grep -v grep
echo
read -p "是否终止所有Git进程？(y/n): " kill_git
if [ "$kill_git" = "y" ]; then
    pkill -9 git
    echo "  ✓ Git进程已终止"
fi
echo

echo "【方案3】清理Git状态"
echo "  适用: Git状态异常"
git reset --hard HEAD
git clean -fd
echo "  ✓ Git状态已清理"
echo

echo "【方案4】重新拉取"
echo "  执行: git fetch + git reset"
git fetch origin
git reset --hard origin/main  # 或 origin/master，根据你的分支名调整
echo "  ✓ 代码已更新"
echo

echo "【方案5】增加超时时间"
echo "  适用: 网络较慢"
export GIT_TIMEOUT=300  # 5分钟超时
echo "  已设置超时: 300秒"
echo

echo "========================================"
echo "修复完成，尝试重新pull"
echo "========================================"
echo

read -p "现在执行git pull？(y/n): " do_pull
if [ "$do_pull" = "y" ]; then
    timeout 60 git pull
fi