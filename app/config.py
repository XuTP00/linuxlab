"""Конфигурация LinuxLab."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
DATA_DIR = os.environ.get("LINUXLAB_DATA", "/var/lib/linuxlab")
DB_PATH = os.path.join(DATA_DIR, "progress.db")

DOCKER_IMAGE = os.environ.get("LINUXLAB_IMAGE", "linuxlab/lab:latest")
CONTAINER_PREFIX = "linuxlab-sess-"
HOME_DIR = "/home/student"

# Таймауты
IDLE_SESSION_TTL = int(os.environ.get("LINUXLAB_IDLE_TTL", "1800"))  # 30 минут
CHECK_TIMEOUT = 60
