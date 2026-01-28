#!/bin/bash

# Скрипт для исправления проблемы с установкой psycopg2-binary
# Использование: sudo ./fix_psycopg2.sh

set -e

PROJECT_DIR="/opt/clinic-bot"
VENV_DIR="$PROJECT_DIR/venv"

echo "=== Исправление установки psycopg2-binary ==="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "Ошибка: Запустите скрипт с правами root (sudo ./fix_psycopg2.sh)"
    exit 1
fi

# Установка системных зависимостей
echo "Установка системных зависимостей для PostgreSQL..."
apt-get update
apt-get install -y \
    libpq-dev \
    postgresql-client \
    build-essential \
    python3-dev \
    pkg-config

# Проверка наличия pg_config
if ! command -v pg_config &> /dev/null; then
    echo "ОШИБКА: pg_config не найден после установки пакетов"
    echo "Попробуйте установить полный пакет PostgreSQL:"
    echo "  apt-get install -y postgresql-server-dev-all"
    exit 1
fi

echo "pg_config найден: $(which pg_config)"

# Обновление pip и установка psycopg2-binary
if [ -d "$VENV_DIR" ]; then
    echo "Обновление pip в виртуальном окружении..."
    "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
    
    echo "Установка psycopg2-binary..."
    "$VENV_DIR/bin/pip" install --no-cache-dir "psycopg2-binary>=2.9.9"
    
    echo "Проверка установки..."
    "$VENV_DIR/bin/python" -c "import psycopg2; print('psycopg2 успешно установлен:', psycopg2.__version__)"
    
    echo "=== Проблема исправлена! ==="
else
    echo "Виртуальное окружение не найдено в $VENV_DIR"
    echo "Сначала запустите deploy.sh"
    exit 1
fi
