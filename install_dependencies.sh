#!/bin/bash

# Скрипт для установки зависимостей в виртуальное окружение
# Использование: sudo ./install_dependencies.sh

set -e

PROJECT_DIR="/opt/clinic-bot"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_USER="clinicbot"

echo "=== Установка зависимостей для бота ==="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "Ошибка: Запустите скрипт с правами root (sudo ./install_dependencies.sh)"
    exit 1
fi

# Проверка виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    sudo -u "$SERVICE_USER" python3 -m venv "$VENV_DIR"
fi

# Установка системных зависимостей для PostgreSQL
echo "Установка системных зависимостей..."
apt-get update
apt-get install -y libpq-dev postgresql-client build-essential python3-dev pkg-config || true

# Обновление pip
echo "Обновление pip..."
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel

# Установка зависимостей
echo "Установка зависимостей из requirements.txt..."
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

# Проверка установки основных модулей
echo "Проверка установки модулей..."
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/python" -c "import structlog; import aiogram; print('✅ Основные модули установлены')"

echo "=== Зависимости установлены! ==="
