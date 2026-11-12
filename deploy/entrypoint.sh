#!/bin/bash
# Точка входа контейнера-лаборатории: поднимаем sshd и cron, затем живём.
set -u

mkdir -p /var/run/sshd

# sshd для заданий по SSH
if [ -x /usr/sbin/sshd ]; then
    /usr/sbin/sshd 2>/dev/null || echo "[lab] sshd не запустился"
fi

# демон cron для заданий по расписанию
if command -v cron >/dev/null 2>&1; then
    cron 2>/dev/null || echo "[lab] cron не запустился"
fi

echo "[lab] контейнер готов. Пользователь: student (sudo без пароля)."
exec sleep infinity
