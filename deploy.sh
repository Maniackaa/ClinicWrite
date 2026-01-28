#!/bin/bash

# Скрипт развертывания Telegram бота ROYAL Clinic на сервере
# Использование: ./deploy.sh

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Переменные
PROJECT_NAME="clinic-bot"
PROJECT_DIR="/opt/$PROJECT_NAME"
SERVICE_USER="clinicbot"
PYTHON_VERSION="python3.10"
VENV_DIR="$PROJECT_DIR/venv"

echo -e "${GREEN}=== Развертывание Telegram бота ROYAL Clinic ===${NC}"

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Ошибка: Запустите скрипт с правами root (sudo ./deploy.sh)${NC}"
    exit 1
fi

# Создание пользователя для бота (если не существует)
if ! id "$SERVICE_USER" &>/dev/null; then
    echo -e "${YELLOW}Создание пользователя $SERVICE_USER...${NC}"
    useradd -r -s /bin/bash -d "$PROJECT_DIR" "$SERVICE_USER"
    echo -e "${GREEN}Пользователь $SERVICE_USER создан${NC}"
else
    echo -e "${GREEN}Пользователь $SERVICE_USER уже существует${NC}"
fi

# Создание директории проекта
echo -e "${YELLOW}Создание директории проекта...${NC}"
mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/logs"
chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"

# Копирование файлов проекта
echo -e "${YELLOW}Копирование файлов проекта...${NC}"
# Предполагается, что скрипт запускается из директории проекта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -r "$SCRIPT_DIR"/* "$PROJECT_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR"/.git "$PROJECT_DIR/" 2>/dev/null || true

# Установка Python и зависимостей
echo -e "${YELLOW}Проверка Python...${NC}"
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo -e "${RED}Ошибка: $PYTHON_VERSION не установлен${NC}"
    echo -e "${YELLOW}Установите Python 3.10: apt-get install python3.10 python3.10-venv python3-pip${NC}"
    exit 1
fi

# Создание виртуального окружения
echo -e "${YELLOW}Создание виртуального окружения...${NC}"
sudo -u "$SERVICE_USER" $PYTHON_VERSION -m venv "$VENV_DIR"

# Активация виртуального окружения и установка зависимостей
echo -e "${YELLOW}Установка зависимостей...${NC}"
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

# Проверка наличия .env файла
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${YELLOW}Создание шаблона .env файла...${NC}"
    cat > "$PROJECT_DIR/.env.example" << EOF
# Telegram Bot Settings
BOT_TOKEN='your_bot_token_here'
ADMIN_IDS='your_admin_id_here'

# PostgreSQL Database Settings (optional)
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DB_HOST=
DB_PORT=5432

# Timezone
TIMEZONE="Europe/Moscow"

# Telegram Channel ID for notifications
GROUP_ID=your_channel_id_here

# Price file ID (optional)
PRICE_FILE_ID=
EOF
    chown "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR/.env.example"
    echo -e "${RED}ВНИМАНИЕ: Файл .env не найден!${NC}"
    echo -e "${YELLOW}Создан шаблон .env.example. Скопируйте его в .env и заполните данные:${NC}"
    echo -e "${YELLOW}  cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env${NC}"
    echo -e "${YELLOW}  nano $PROJECT_DIR/.env${NC}"
else
    echo -e "${GREEN}Файл .env найден${NC}"
    chown "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR/.env"
    chmod 600 "$PROJECT_DIR/.env"
fi

# Установка systemd service
echo -e "${YELLOW}Установка systemd service...${NC}"
cat > "/etc/systemd/system/$PROJECT_NAME.service" << EOF
[Unit]
Description=ROYAL Clinic Telegram Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$PROJECT_NAME

# Ограничения ресурсов
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

# Перезагрузка systemd и включение сервиса
systemctl daemon-reload
systemctl enable "$PROJECT_NAME.service"

echo -e "${GREEN}=== Развертывание завершено! ===${NC}"
echo -e "${YELLOW}Следующие шаги:${NC}"
echo -e "1. Убедитесь, что файл .env настроен правильно:"
echo -e "   ${GREEN}nano $PROJECT_DIR/.env${NC}"
echo -e ""
echo -e "2. Запустите бота:"
echo -e "   ${GREEN}systemctl start $PROJECT_NAME${NC}"
echo -e ""
echo -e "3. Проверьте статус:"
echo -e "   ${GREEN}systemctl status $PROJECT_NAME${NC}"
echo -e ""
echo -e "4. Просмотр логов:"
echo -e "   ${GREEN}journalctl -u $PROJECT_NAME -f${NC}"
echo -e "   или"
echo -e "   ${GREEN}tail -f $PROJECT_DIR/logs/file.log${NC}"
