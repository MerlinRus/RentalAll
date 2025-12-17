#!/bin/bash

# Скрипт деплоя RentalAll на сервер
# Запускать из директории /root/rentalall/

set -e  # Остановка при ошибке

echo "🚀 Начинаем деплой RentalAll..."

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Проверка, что мы в правильной директории
if [ ! -d "/root/rentalall" ]; then
    echo -e "${RED}❌ Директория /root/rentalall не найдена!${NC}"
    exit 1
fi

cd /root/rentalall

# 1. Обновление системных пакетов
echo -e "${YELLOW}📦 Обновление системных пакетов...${NC}"
apt update

# 2. Установка необходимых пакетов (если еще не установлены)
echo -e "${YELLOW}📦 Проверка необходимых пакетов...${NC}"
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx nodejs npm

# 3. Проверка .env файла
echo -e "${YELLOW}⚙️  Проверка .env файла...${NC}"
if [ ! -f "/root/rentalall/backend/.env" ]; then
    echo -e "${RED}❌ ОШИБКА: Файл .env не найден!${NC}"
    echo -e "${YELLOW}Создайте его командой:${NC}"
    echo -e "  cp /root/rentalall/deploy/env.production.example /root/rentalall/backend/.env"
    echo -e "  nano /root/rentalall/backend/.env"
    echo -e "${YELLOW}Заполните SECRET_KEY и DB_PASSWORD, затем запустите скрипт снова.${NC}"
    exit 1
fi

# Чтение пароля БД из .env
DB_PASSWORD=$(grep "^DB_PASSWORD=" /root/rentalall/backend/.env | cut -d '=' -f2)
if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" == "your-strong-db-password-here" ]; then
    echo -e "${RED}❌ ОШИБКА: DB_PASSWORD не установлен в .env файле!${NC}"
    echo -e "${YELLOW}Отредактируйте файл: nano /root/rentalall/backend/.env${NC}"
    echo -e "${YELLOW}Установите безопасный пароль для DB_PASSWORD${NC}"
    exit 1
fi

# 4. Настройка PostgreSQL
echo -e "${YELLOW}🐘 Настройка PostgreSQL...${NC}"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'rentalall_db'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE rentalall_db;"

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = 'rentalall_user'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER rentalall_user WITH PASSWORD '$DB_PASSWORD';"

sudo -u postgres psql -c "ALTER USER rentalall_user WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rentalall_db TO rentalall_user;"

# 5. Создание виртуального окружения Python
echo -e "${YELLOW}🐍 Создание Python виртуального окружения...${NC}"
cd /root/rentalall/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 6. Установка Python зависимостей
echo -e "${YELLOW}📚 Установка Python зависимостей...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Для production

# 6. Копирование .env файла
echo -e "${YELLOW}⚙️  Настройка .env файла...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}⚠️  Файл .env не найден! Создайте его из deploy/env.production.example${NC}"
    echo -e "${YELLOW}Команда: cp /root/rentalall/deploy/env.production.example /root/rentalall/backend/.env${NC}"
    echo -e "${YELLOW}Затем отредактируйте файл: nano /root/rentalall/backend/.env${NC}"
    exit 1
fi

# 7. Миграции Django
echo -e "${YELLOW}🗃️  Применение миграций Django...${NC}"
python manage.py makemigrations
python manage.py migrate

# 8. Сбор статики Django
echo -e "${YELLOW}📁 Сбор статики Django...${NC}"
python manage.py collectstatic --noinput

# 9. Создание суперпользователя (если еще нет)
echo -e "${YELLOW}👤 Проверка суперпользователя...${NC}"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@rentalall.ru', 'admin123')" | python manage.py shell

deactivate

# 10. Сборка React frontend
echo -e "${YELLOW}⚛️  Сборка React frontend...${NC}"
cd /root/rentalall/frontend

# Проверка наличия node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Установка npm зависимостей...${NC}"
    npm install
fi

# Создание .env для production
if [ ! -f ".env.production" ]; then
    echo "REACT_APP_API_URL=https://rentalall.ru/api" > .env.production
fi

# Production build
echo -e "${YELLOW}🔨 Сборка production версии...${NC}"
npm run build

# 11. Создание директорий для логов
echo -e "${YELLOW}📝 Создание директорий для логов...${NC}"
mkdir -p /var/log/rentalall

# 12. Настройка systemd service
echo -e "${YELLOW}⚙️  Настройка systemd service...${NC}"
cp /root/rentalall/deploy/rentalall.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable rentalall.service
systemctl restart rentalall.service

# 13. Настройка Nginx
echo -e "${YELLOW}🌐 Настройка Nginx...${NC}"
cp /root/rentalall/deploy/nginx_rentalall.conf /etc/nginx/sites-available/rentalall.ru

# Создание симлинка
if [ ! -L "/etc/nginx/sites-enabled/rentalall.ru" ]; then
    ln -s /etc/nginx/sites-available/rentalall.ru /etc/nginx/sites-enabled/
fi

# Проверка конфигурации Nginx
nginx -t

# 14. Получение SSL сертификата
echo -e "${YELLOW}🔐 Настройка SSL сертификата...${NC}"
echo -e "${YELLOW}Запустите вручную после проверки DNS:${NC}"
echo -e "${GREEN}certbot --nginx -d rentalall.ru -d www.rentalall.ru${NC}"

# 15. Перезапуск Nginx
echo -e "${YELLOW}🔄 Перезапуск Nginx...${NC}"
systemctl restart nginx

# 16. Проверка статуса сервисов
echo -e "${GREEN}✅ Проверка статуса сервисов...${NC}"
echo -e "${YELLOW}Django (Gunicorn):${NC}"
systemctl status rentalall.service --no-pager | head -n 10

echo -e "${YELLOW}Nginx:${NC}"
systemctl status nginx --no-pager | head -n 10

echo ""
echo -e "${GREEN}✅ Деплой завершен!${NC}"
echo ""
echo -e "${YELLOW}📋 Следующие шаги:${NC}"
echo "1. Проверьте DNS: rentalall.ru должен указывать на 62.192.174.91"
echo "2. Получите SSL сертификат: certbot --nginx -d rentalall.ru -d www.rentalall.ru"
echo "3. Перезапустите Nginx: systemctl restart nginx"
echo "4. Откройте https://rentalall.ru в браузере"
echo ""
echo -e "${YELLOW}🔧 Полезные команды:${NC}"
echo "  Логи Django: journalctl -u rentalall.service -f"
echo "  Логи Nginx: tail -f /var/log/nginx/rentalall_error.log"
echo "  Перезапуск Django: systemctl restart rentalall.service"
echo "  Перезапуск Nginx: systemctl restart nginx"
echo ""
echo -e "${GREEN}🎉 Готово!${NC}"

