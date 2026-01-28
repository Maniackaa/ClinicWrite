#!/bin/bash

# Упрощенный скрипт установки systemd service
# Использование: sudo ./install.sh

set -e

PROJECT_NAME="clinic-bot"
PROJECT_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="clinicbot"
VENV_DIR="$PROJECT_DIR/venv"

echo "=== Установка systemd service для $PROJECT_NAME ==="

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "Ошибка: Запустите скрипт с правами root (sudo ./install.sh)"
    exit 1
fi

# Проверка существования директории проекта
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Ошибка: Директория проекта $PROJECT_DIR не найдена"
    echo "Сначала запустите deploy.sh для развертывания проекта"
    exit 1
fi

# Проверка существования пользователя
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Создание пользователя $SERVICE_USER..."
    useradd -r -s /bin/bash -d "$PROJECT_DIR" "$SERVICE_USER"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"
fi

# Копирование service файла
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp "$SCRIPT_DIR/clinic-bot.service" "/etc/systemd/system/$PROJECT_NAME.service"

# Обновление путей в service файле (если нужно)
sed -i "s|/opt/clinic-bot|$PROJECT_DIR|g" "/etc/systemd/system/$PROJECT_NAME.service"
sed -i "s|clinicbot|$SERVICE_USER|g" "/etc/systemd/system/$PROJECT_NAME.service"

# Перезагрузка systemd
systemctl daemon-reload

echo "=== Service установлен! ==="
echo ""
echo "Команды для управления:"
echo "  Запуск:   sudo systemctl start $PROJECT_NAME"
echo "  Остановка: sudo systemctl stop $PROJECT_NAME"
echo "  Статус:   sudo systemctl status $PROJECT_NAME"
echo "  Логи:     sudo journalctl -u $PROJECT_NAME -f"
echo "  Автозапуск: sudo systemctl enable $PROJECT_NAME"
