#!/usr/bin/env bash
#
# LinuxLab v0.01 — установщик для Linux-дистрибутивов
#
# Поддерживаемые дистрибутивы: Debian/Ubuntu, RHEL/CentOS/Rocky/Alma/Fedora,
# Arch, openSUSE (zypper), Alpine (без systemd — ручной запуск).
#
# Что делает:
#   1. ставит системные зависимости (docker, nginx, python3, venv)
#   2. разворачивает код в /opt/linuxlab и создаёт venv с зависимостями
#   3. собирает docker-образ лаборатории linuxlab/lab:latest
#   4. создаёт и включает systemd-юнит linuxlab
#   5. настраивает nginx (reverse proxy + статика)
#   6. проверяет, что сервис отвечает, и печатает адрес
#
# Запуск:   sudo bash install.sh
# Удаление: sudo bash install.sh --uninstall
#
set -Eeuo pipefail

# ---------------------------------------------------------------------------
# Значения по умолчанию (переопределяются переменными окружения или флагами)
# ---------------------------------------------------------------------------
APP_DIR="${APP_DIR:-/opt/linuxlab}"
DATA_DIR="${DATA_DIR:-/var/lib/linuxlab}"
IMAGE="${IMAGE:-linuxlab/lab:latest}"
APP_PORT="${APP_PORT:-8080}"
HTTP_PORT="${HTTP_PORT:-80}"
ADMIN_PASSWORD="${LINUXLAB_ADMIN_PASSWORD:-1541685}"
UNLOCK_TTL="${LINUXLAB_UNLOCK_TTL:-28800}"
SERVICE_USER="${SERVICE_USER:-}"
LOG_PREFIX="[linuxlab]"

UNINSTALL=0
SKIP_PACKAGES=0
for arg in "$@"; do
  case "$arg" in
    --uninstall) UNINSTALL=1 ;;
    --skip-packages) SKIP_PACKAGES=1 ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "Неизвестный аргумент: $arg" >&2; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Логи и утилиты
# ---------------------------------------------------------------------------
c_ok=$'\033[32m'; c_warn=$'\033[33m'; c_err=$'\033[31m'; c_info=$'\033[36m'; c_off=$'\033[0m'
log()  { printf '%s %s\n' "$LOG_PREFIX" "$*"; }
ok()   { printf '%s ✓ %s%s\n' "$c_ok" "$*" "$c_off"; }
info() { printf '%s → %s%s\n' "$c_info" "$*" "$c_off"; }
warn() { printf '%s ! %s%s\n' "$c_warn" "$*" "$c_off"; }
die()  { printf '%s ✗ %s%s\n' "$c_err" "$*" "$c_off" >&2; exit 1; }

trap 'die "ошибка на строке $LINENO"' ERR

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -d "$SRC_DIR/app" ]; then
  die "не найден каталог app рядом с установщиком (запускать из корня проекта)"
fi

# ---------------------------------------------------------------------------
# Определение дистрибутива
# ---------------------------------------------------------------------------
ID=""; ID_LIKE=""; VERSION_ID=""; PRETTY=""
if [ -r /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  ID="${ID:-}"; ID_LIKE="${ID_LIKE:-}"; VERSION_ID="${VERSION_ID:-}"; PRETTY="${PRETTY_NAME:-$ID $VERSION_ID}"
fi
case "$ID $ID_LIKE" in
  *debian*|*ubuntu*)            PKG=apt;    PKG_UPDATE="apt-get update -qq" ;;
  *rhel*|*centos*|*fedora*|*rocky*|*almalinux*) PKG=dnf; PKG_UPDATE="dnf -y makecache" ;;
  *arch*|*manjaro*)             PKG=pacman; PKG_UPDATE="pacman -Sy --noconfirm" ;;
  *suse*|*opensuse*)            PKG=zypper; PKG_UPDATE="zypper --non-interactive refresh" ;;
  *alpine*)                     PKG=apk;    PKG_UPDATE="apk update" ;;
  *) die "дистрибутив не поддерживается: ${PRETTY:-неизвестно}. Поддерживаются Debian/Ubuntu, RHEL-семейство, Arch, openSUSE, Alpine" ;;
esac
HAS_SYSTEMD=0
if [ -d /run/systemd/system ] && command -v systemctl >/dev/null 2>&1; then HAS_SYSTEMD=1; fi

pkg_install() {
  local pkgs="$*"
  case "$PKG" in
    apt)    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq $pkgs ;;
    dnf)    dnf install -y -q $pkgs ;;
    pacman) pacman -S --needed --noconfirm $pkgs ;;
    zypper) zypper --non-interactive install -y $pkgs ;;
    apk)    apk add --no-cache $pkgs ;;
  esac
}

# ---------------------------------------------------------------------------
# Пользователь сервиса
# ---------------------------------------------------------------------------
if [ -z "$SERVICE_USER" ]; then
  if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != "root" ] && id "$SUDO_USER" >/dev/null 2>&1; then
    SERVICE_USER="$SUDO_USER"
  else
    SERVICE_USER="linuxlab"
  fi
fi
if ! id "$SERVICE_USER" >/dev/null 2>&1; then
  log "создаю системного пользователя $SERVICE_USER"
  if [ "$PKG" = "apt" ]; then
    useradd --system --home-dir "$APP_DIR" --shell /usr/sbin/nologin "$SERVICE_USER" || true
  else
    useradd --system --home-dir "$APP_DIR" --shell /sbin/nologin "$SERVICE_USER" || true
  fi
fi

# ---------------------------------------------------------------------------
# Удаление
# ---------------------------------------------------------------------------
if [ "$UNINSTALL" = "1" ]; then
  log "останавливаю сервис"
  systemctl disable --now linuxlab 2>/dev/null || true
  rm -f /etc/systemd/system/linuxlab.service
  systemctl daemon-reload || true
  if [ -f /etc/nginx/sites-available/linuxlab ]; then
    rm -f /etc/nginx/sites-available/linuxlab /etc/nginx/sites-enabled/linuxlab
    nginx -t >/dev/null 2>&1 && systemctl reload nginx 2>/dev/null || true
  fi
  rm -rf "$APP_DIR"
  ok "служба удалена (данные в $DATA_DIR и docker-образ оставлены)"
  exit 0
fi

# ---------------------------------------------------------------------------
# 0. Проверки
# ---------------------------------------------------------------------------
[ "$(id -u)" = "0" ] || die "запускать от root: sudo bash install.sh"
command -v curl >/dev/null 2>&1 || { PKG_UPDATE; pkg_install curl ca-certificates; }

log "LinuxLab: установка на ${PRETTY}"
log "каталог: $APP_DIR | пользователь сервиса: $SERVICE_USER | образ: $IMAGE"

# ---------------------------------------------------------------------------
# 1. Зависимости
# ---------------------------------------------------------------------------
if [ "$SKIP_PACKAGES" = "0" ]; then
  info "устанавливаю системные пакеты"
  $PKG_UPDATE >/dev/null 2>&1 || true
  case "$PKG" in
    apt)    pkg_install docker.io nginx python3 python3-venv python3-pip ca-certificates ;;
    dnf)    pkg_install docker nginx python3 python3-pip procps-ng ;;
    pacman) pkg_install docker nginx python python-pip ;;
    zypper) pkg_install docker nginx python3 python3-pip ;;
    apk)    pkg_install docker nginx python3 py3-pip bash coreutils ;;
  esac
  ok "системные пакеты установлены"
fi

# nginx и python могут быть уже в системе — проверяем
command -v nginx >/dev/null 2>&1 || die "nginx не найден (установите вручную и повторите)"
command -v docker >/dev/null 2>&1 || die "docker не найден (установите вручную и повторите)"

# ---------------------------------------------------------------------------
# 2. Python >= 3.10
# ---------------------------------------------------------------------------
PY_BIN=""
for cand in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
      PY_BIN="$(command -v "$cand")"; break
    fi
  fi
done
[ -n "$PY_BIN" ] || die "нужен Python 3.10+ (в системе подходящего интерпретатора нет)"
info "python: $PY_BIN ($("$PY_BIN" -V 2>&1))"

# ---------------------------------------------------------------------------
# 3. Docker
# ---------------------------------------------------------------------------
if [ "$HAS_SYSTEMD" = "1" ]; then
  systemctl enable --now docker >/dev/null 2>&1 || systemctl start docker || true
fi
docker info >/dev/null 2>&1 || die "docker не запущен: проверьте systemctl start docker"
ok "docker работает"

if ! getent group docker >/dev/null 2>&1; then
  groupadd docker 2>/dev/null || true
fi
if ! id -nG "$SERVICE_USER" | tr ' ' '\n' | grep -qx docker; then
  usermod -aG docker "$SERVICE_USER"
  warn "пользователь $SERVICE_USER добавлен в группу docker — перезайдите в систему, чтобы группа применилась"
fi

# ---------------------------------------------------------------------------
# 4. Развёртывание кода
# ---------------------------------------------------------------------------
info "разворачиваю код в $APP_DIR"
mkdir -p "$APP_DIR" "$DATA_DIR"
if [ "$(cd "$SRC_DIR" && pwd)" = "$(cd "$APP_DIR" && pwd)" ]; then
  info "код уже в $APP_DIR — копирование не требуется"
elif command -v rsync >/dev/null 2>&1; then
  rsync -a --delete \
    --exclude '.git' --exclude '__pycache__' --exclude 'venv' --exclude '*.pyc' \
    "$SRC_DIR/" "$APP_DIR/"
else
  cp -a "$SRC_DIR/." "$APP_DIR/"
  find "$APP_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  rm -rf "$APP_DIR/venv" 2>/dev/null || true
fi
ok "код развёрнут"

# ---------------------------------------------------------------------------
# 5. Python-окружение и зависимости
# ---------------------------------------------------------------------------
info "создаю venv и ставлю зависимости ($APP_DIR/venv)"
rm -rf "$APP_DIR/venv"
"$PY_BIN" -m venv "$APP_DIR/venv" || die "не удалось создать venv (нужен пакет python3-venv)"
PIP="$APP_DIR/venv/bin/pip"
[ -x "$PIP" ] || "$PY_BIN" -m ensurepip --upgrade >/dev/null 2>&1 || true
"$PIP" install -q --upgrade pip setuptools wheel
if [ -f "$APP_DIR/requirements.txt" ]; then
  "$PIP" install -q -r "$APP_DIR/requirements.txt"
else
  "$PIP" install -q "fastapi" "uvicorn[standard]"
fi
"$APP_DIR/venv/bin/python" -c "import fastapi, uvicorn" || die "не удалось установить зависимости"
ok "python-зависимости установлены"

# ---------------------------------------------------------------------------
# 6. Docker-образ лаборатории
# ---------------------------------------------------------------------------
info "собираю образ $IMAGE (несколько минут)"
docker build -f "$APP_DIR/deploy/Dockerfile.lab" -t "$IMAGE" "$APP_DIR/deploy" || die "сборка образа не удалась"
ok "образ $IMAGE готов"

# ---------------------------------------------------------------------------
# 7. systemd-юнит
# ---------------------------------------------------------------------------
if [ "$HAS_SYSTEMD" = "1" ]; then
  info "настраиваю systemd-юнит linuxlab"
  cat > /etc/systemd/system/linuxlab.service <<UNIT
[Unit]
Description=LinuxLab — практический курс по Linux (веб-сервис)
After=network-online.target docker.service
Requires=docker.service
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$APP_DIR
Environment="LINUXLAB_DATA=$DATA_DIR"
Environment="LINUXLAB_IMAGE=$IMAGE"
Environment="LINUXLAB_ADMIN_PASSWORD=$ADMIN_PASSWORD"
Environment="LINUXLAB_UNLOCK_TTL=$UNLOCK_TTL"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port $APP_PORT --workers 1 --proxy-headers
Restart=always
RestartSec=3
TimeoutStopSec=20

[Install]
WantedBy=multi-user.target
UNIT
  systemctl daemon-reload
  systemctl enable linuxlab >/dev/null
  systemctl restart linuxlab
  ok "юнит linuxlab установлен и запущен"
else
  warn "systemd недоступен — запускаю сервис вручную (nohup)"
  nohup "$APP_DIR/venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port "$APP_PORT" \
        >"$DATA_DIR/linuxlab.log" 2>&1 &
  echo $! > "$DATA_DIR/linuxlab.pid"
fi

# ---------------------------------------------------------------------------
# 8. nginx
# ---------------------------------------------------------------------------
info "настраиваю nginx"
cat > /etc/nginx/sites-available/linuxlab <<NGINX
upstream linuxlab_app {
    server 127.0.0.1:$APP_PORT;
    keepalive 16;
}

server {
    listen $HTTP_PORT default_server;
    listen [::]:$HTTP_PORT default_server;
    server_name _;

    access_log /var/log/nginx/linuxlab.access.log;
    error_log  /var/log/nginx/linuxlab.error.log;

    client_max_body_size 4m;

    location /static/ {
        alias $APP_DIR/app/static/;
        expires 1h;
        access_log off;
    }

    location / {
        root $APP_DIR/app/static;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://linuxlab_app;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    location /ws/ {
        proxy_pass http://linuxlab_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
NGINX

if [ -d /etc/nginx/sites-enabled ]; then
  ln -sf /etc/nginx/sites-available/linuxlab /etc/nginx/sites-enabled/linuxlab
  rm -f /etc/nginx/sites-enabled/default
else
  # openSUSE/Alpine: конфиг лежит в conf.d
  cp /etc/nginx/sites-available/linuxlab /etc/nginx/conf.d/linuxlab.conf
fi
nginx -t || die "ошибка в конфигурации nginx"
if [ "$HAS_SYSTEMD" = "1" ]; then
  systemctl enable nginx >/dev/null 2>&1 || true
  systemctl reload nginx 2>/dev/null || systemctl restart nginx
else
  nginx -s reload 2>/dev/null || nginx
fi
ok "nginx настроен"

# ---------------------------------------------------------------------------
# 9. Права и проверка
# ---------------------------------------------------------------------------
chown -R "$SERVICE_USER":"$SERVICE_USER" "$APP_DIR" 2>/dev/null || true
chown -R "$SERVICE_USER":"$SERVICE_USER" "$DATA_DIR" 2>/dev/null || true
chmod 0755 "$APP_DIR/venv/bin/python" 2>/dev/null || true

info "проверяю запуск"
HEALTH=""
for _ in $(seq 1 30); do
  sleep 2
  HEALTH="$(curl -fsS "http://127.0.0.1:$APP_PORT/api/health" 2>/dev/null || true)"
  [ -n "$HEALTH" ] && break
done
[ -n "$HEALTH" ] || die "сервис не отвечает на http://127.0.0.1:$APP_PORT/api/health — смотрите: journalctl -u linuxlab"

IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
[ -n "$IP" ] || IP="<ip-сервера>"
URL="http://$IP"
[ "$HTTP_PORT" = "80" ] || URL="http://$IP:$HTTP_PORT"

cat <<EOF

$(printf '%s' "$c_ok")────────────────────────────────────────────────────────$(printf '%s' "$c_off")
$(printf '%s' "$c_ok") LinuxLab установлен и работает$(printf '%s' "$c_off")

  Веб-интерфейс : $URL/
  API            : http://127.0.0.1:$APP_PORT/api/health
  Ответ         : $HEALTH

  Код           : $APP_DIR
  Данные        : $DATA_DIR
  Образ         : $IMAGE
  Юнит          : linuxlab.service (systemctl status linuxlab)
  Пароль копир. : $ADMIN_PASSWORD (переменная LINUXLAB_ADMIN_PASSWORD)

  Перезапуск    : systemctl restart linuxlab
  Обновление    : cd $APP_DIR && sudo bash install.sh
EOF
