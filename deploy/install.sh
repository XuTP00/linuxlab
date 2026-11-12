#!/usr/bin/env bash
# Обёртка: основной установщик лежит в корне проекта (../install.sh)
set -Eeuo pipefail
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../install.sh" "$@"
