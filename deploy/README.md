# 🚀 Деплой RentalAll на сервер

## Быстрый старт

### 1. Подключитесь к серверу:
```bash
ssh root@62.192.174.91
```

### 2. Перенесите проект в `/root/rentalall`

### 3. Настройте `.env`:
```bash
cp deploy/env.production.example backend/.env
nano backend/.env
# Заполните все параметры (SECRET_KEY, DB_PASSWORD, и т.д.)
```

### 4. Запустите деплой:
```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### 5. Настройте DNS:
- Создайте A-запись: `rentalall.ru` → `62.192.174.91`
- Создайте A-запись: `www.rentalall.ru` → `62.192.174.91`

### 6. Получите SSL:
```bash
certbot --nginx -d rentalall.ru -d www.rentalall.ru
systemctl restart nginx
```

### 7. Откройте в браузере:
https://rentalall.ru

---

## 📚 Полная документация

См. файл [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) для подробных инструкций.

---

## 📂 Файлы в этой папке:

- `nginx_rentalall.conf` - конфигурация Nginx
- `rentalall.service` - systemd service для автозапуска Django
- `env.production.example` - пример .env файла для production
- `deploy.sh` - автоматический скрипт деплоя
- `DEPLOYMENT_GUIDE.md` - полное руководство по деплою

---

## ⚙️ Структура на сервере:

```
/root/rentalall/
├── backend/
│   ├── venv/                  # Python виртуальное окружение
│   ├── .env                   # Настройки (НЕ в Git!)
│   ├── manage.py
│   ├── requirements.txt
│   ├── staticfiles/           # Django static (создается автоматически)
│   └── media/                 # Загруженные фото площадок
├── frontend/
│   ├── build/                 # Production build React
│   ├── node_modules/
│   └── package.json
└── deploy/
    └── (эти файлы)
```

---

## 🔧 Управление после деплоя:

```bash
# Перезапуск Django
systemctl restart rentalall.service

# Перезапуск Nginx
systemctl restart nginx

# Логи Django
journalctl -u rentalall.service -f

# Логи Nginx
tail -f /var/log/nginx/rentalall_error.log
```

---

## 🔒 Безопасность (ОБЯЗАТЕЛЬНО после деплоя!):

1. Смените root-пароль: `passwd`
2. Смените Django admin пароль через https://rentalall.ru/admin
3. Настройте firewall: `ufw allow 22,80,443/tcp && ufw enable`
4. Отключите root SSH-вход (создайте отдельного пользователя)

---

## 🐛 Если что-то не работает:

```bash
# Проверьте статус сервисов
systemctl status rentalall.service
systemctl status nginx

# Проверьте логи
journalctl -u rentalall.service -n 50
tail -n 50 /var/log/nginx/rentalall_error.log

# Проверьте .env
cat /root/rentalall/backend/.env

# Проверьте БД
sudo -u postgres psql -l | grep rentalall
```

---

## 📞 Поддержка

Подробные инструкции и troubleshooting: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

