# 🚀 Руководство по деплою RentalAll на сервер

## 📋 Предварительные требования

- ✅ Сервер: Ubuntu 20.04+ / Debian 11+
- ✅ IP: 62.192.174.91
- ✅ Домен: rentalall.ru (должен указывать на IP сервера в DNS)
- ✅ Root доступ к серверу

---

## 🔧 Шаг 1: Подключение к серверу

Откройте терминал на вашем локальном компьютере и подключитесь к серверу:

```bash
ssh root@62.192.174.91
```

Введите пароль: `15Y02MR8QwQr`

⚠️ **После деплоя обязательно смените пароль!**

---

## 📦 Шаг 2: Перенос файлов на сервер

### Вариант А: Через Git (рекомендуется)

Если проект уже в Git-репозитории:

```bash
cd /root
git clone https://github.com/your-username/rentalall.git
cd rentalall
```

### Вариант Б: Через SCP (с локального компьютера)

На вашем локальном компьютере (в папке проекта):

```bash
# Архивируем проект (исключая node_modules и venv)
cd E:\Study\Диплом
tar -czf rentalall.tar.gz \
  --exclude='rentalall/backend/venv' \
  --exclude='rentalall/frontend/node_modules' \
  --exclude='rentalall/frontend/build' \
  rentalall/

# Копируем на сервер
scp rentalall.tar.gz root@62.192.174.91:/root/

# На сервере распаковываем
ssh root@62.192.174.91
cd /root
tar -xzf rentalall.tar.gz
rm rentalall.tar.gz
```

### Вариант В: Через FileZilla/WinSCP (для Windows)

1. Скачайте WinSCP: https://winscp.net/
2. Подключитесь:
   - Протокол: SFTP
   - Хост: 62.192.174.91
   - Порт: 22
   - Пользователь: root
   - Пароль: 15Y02MR8QwQr
3. Перетащите папку `rentalall` в `/root/`

---

## ⚙️ Шаг 3: Настройка окружения

На сервере:

```bash
cd /root/rentalall

# Делаем скрипт деплоя исполняемым
chmod +x deploy/deploy.sh

# Создаем .env файл из примера
cp deploy/env.production.example backend/.env

# Редактируем .env файл
nano backend/.env
```

### Важные параметры в `.env`:

1. **SECRET_KEY**: Сгенерируйте новый:
   ```bash
   python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **DB_PASSWORD**: Придумайте сложный пароль для БД (например, `RentAll2024!Secure`)

3. **ALLOWED_HOSTS**: Уже настроены (`rentalall.ru,www.rentalall.ru,62.192.174.91`)

4. **CORS_ALLOWED_ORIGINS**: Уже настроены

Сохраните файл: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🚀 Шаг 4: Запуск скрипта деплоя

**ВНИМАНИЕ**: Скрипт установит необходимые пакеты и настроит все автоматически.

```bash
cd /root/rentalall
./deploy/deploy.sh
```

Скрипт выполнит:
- ✅ Установка зависимостей (Python, Node.js, PostgreSQL, Nginx)
- ✅ Создание БД PostgreSQL
- ✅ Установка Python и npm пакетов
- ✅ Применение миграций Django
- ✅ Сборка React production build
- ✅ Настройка systemd service
- ✅ Настройка Nginx

⏱️ Процесс займет 5-10 минут.

---

## 🌐 Шаг 5: Настройка DNS

Зайдите в панель управления вашего регистратора доменов и настройте A-записи:

| Имя       | Тип | Значение       | TTL  |
|-----------|-----|----------------|------|
| @         | A   | 62.192.174.91  | 3600 |
| www       | A   | 62.192.174.91  | 3600 |

Проверьте DNS (может занять до 24 часов):

```bash
ping rentalall.ru
```

Должен показывать IP: 62.192.174.91

---

## 🔐 Шаг 6: Получение SSL-сертификата

После того, как DNS настроен и работает:

```bash
certbot --nginx -d rentalall.ru -d www.rentalall.ru
```

Введите email для уведомлений, согласитесь с условиями.

Certbot автоматически настроит Nginx и получит бесплатный SSL от Let's Encrypt.

```bash
# Перезапустите Nginx
systemctl restart nginx
```

---

## ✅ Шаг 7: Проверка работы

Откройте в браузере:
- 🌐 **Frontend**: https://rentalall.ru
- 🔧 **Django Admin**: https://rentalall.ru/admin
- 📚 **API Docs**: https://rentalall.ru/swagger

**Данные для входа в админку:**
- Логин: `admin`
- Пароль: `admin123`

⚠️ **Обязательно смените пароль через Django Admin!**

---

## 🔧 Полезные команды

### Логи

```bash
# Логи Django (Gunicorn)
journalctl -u rentalall.service -f

# Логи Nginx (ошибки)
tail -f /var/log/nginx/rentalall_error.log

# Логи Nginx (доступ)
tail -f /var/log/nginx/rentalall_access.log
```

### Управление сервисами

```bash
# Перезапуск Django
systemctl restart rentalall.service

# Статус Django
systemctl status rentalall.service

# Перезапуск Nginx
systemctl restart nginx

# Статус Nginx
systemctl status nginx
```

### Обновление кода

После изменений в коде:

```bash
cd /root/rentalall

# Backend
cd backend
source venv/bin/activate
git pull  # или обновите файлы
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
deactivate

# Frontend
cd ../frontend
git pull  # или обновите файлы
npm install
npm run build

# Перезапуск
systemctl restart rentalall.service
systemctl restart nginx
```

### База данных

```bash
# Подключение к PostgreSQL
sudo -u postgres psql rentalall_db

# Бэкап БД
sudo -u postgres pg_dump rentalall_db > backup_$(date +%Y%m%d).sql

# Восстановление из бэкапа
sudo -u postgres psql rentalall_db < backup_20240101.sql
```

---

## 🔒 Шаг 8: Безопасность (ОБЯЗАТЕЛЬНО!)

### 1. Смена root-пароля

```bash
passwd
```

### 2. Создание отдельного пользователя (не root)

```bash
# Создать пользователя
adduser deploy
usermod -aG sudo deploy

# Настроить SSH-ключи
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Отключить root-вход через SSH
nano /etc/ssh/sshd_config
# Найти и изменить: PermitRootLogin no
systemctl restart sshd
```

### 3. Настройка Firewall

```bash
# Установка UFW
apt install ufw

# Разрешить необходимые порты
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS

# Включить firewall
ufw enable
```

### 4. Настройка автообновлений безопасности

```bash
apt install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 🐛 Troubleshooting

### Проблема: Django не запускается

```bash
# Проверьте логи
journalctl -u rentalall.service -n 50

# Проверьте .env файл
cat /root/rentalall/backend/.env

# Проверьте БД
sudo -u postgres psql -l | grep rentalall
```

### Проблема: Nginx выдает 502 Bad Gateway

```bash
# Проверьте, запущен ли Django
systemctl status rentalall.service

# Если не запущен:
systemctl start rentalall.service
```

### Проблема: Статика не загружается

```bash
cd /root/rentalall/backend
source venv/bin/activate
python manage.py collectstatic --noinput
deactivate

systemctl restart nginx
```

### Проблема: SSL не работает

```bash
# Проверьте сертификаты
certbot certificates

# Обновите сертификаты
certbot renew --dry-run

# Если нужно переполучить:
certbot --nginx -d rentalall.ru -d www.rentalall.ru --force-renewal
```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи (см. раздел "Полезные команды")
2. Проверьте статус сервисов
3. Убедитесь, что DNS настроен правильно
4. Убедитесь, что .env файл корректно заполнен

---

## 🎉 Готово!

Ваш сайт RentalAll теперь доступен по адресу:
**https://rentalall.ru** 🚀

Не забудьте:
- ✅ Сменить пароль root
- ✅ Сменить пароль Django admin
- ✅ Настроить автоматические бэкапы БД
- ✅ Настроить мониторинг (опционально)

