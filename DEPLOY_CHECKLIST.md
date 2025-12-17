# ✅ Чек-лист деплоя RentalAll

## 📍 **ЧАСТЬ 1: НА ЛОКАЛЬНОМ ПК (Windows)**

### ☐ **1. Инициализация Git**

Откройте PowerShell в `E:\Study\Диплом\rentalall`:

```powershell
git init
git add .
git commit -m "Initial commit: RentalAll platform"
```

---

### ☐ **2. Создание репозитория на GitHub**

1. Зайдите: https://github.com/new
2. Заполните:
   - Repository name: `rentalall`
   - Visibility: **Private** ✅
   - **НЕ добавляйте** README, .gitignore, LICENSE
3. Нажмите: **Create repository**

---

### ☐ **3. Получение Personal Access Token**

1. GitHub → **Settings** (ваш профиль)
2. **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. **Generate new token (classic)**
4. Настройки:
   - Note: `RentalAll Deploy`
   - Expiration: `90 days`
   - Scopes: ✅ `repo`
5. **Generate token**
6. **Скопируйте токен** (показывается только раз!)

---

### ☐ **4. Push на GitHub**

```powershell
# Замените YOUR_USERNAME на ваш GitHub username!
git remote add origin https://github.com/YOUR_USERNAME/rentalall.git
git branch -M main
git push -u origin main
```

При запросе:
- Username: ваш GitHub username
- Password: **вставьте Personal Access Token**

Проверьте на GitHub — все файлы должны быть загружены!

---

## 🖥️ **ЧАСТЬ 2: НА СЕРВЕРЕ**

### ☐ **5. Подключение к серверу**

```powershell
ssh root@62.192.174.91
```

Пароль: `15Y02MR8QwQr`

---

### ☐ **6. Клонирование проекта**

```bash
cd /root
git clone https://github.com/YOUR_USERNAME/rentalall.git
cd rentalall
```

Если репозиторий приватный:
- Username: ваш GitHub username
- Password: ваш Personal Access Token

---

### ☐ **7. Настройка .env файла**

```bash
cp deploy/env.production.example backend/.env
nano backend/.env
```

**Обязательно измените:**

**SECRET_KEY:**
```bash
# Генерация нового ключа (скопируйте результат)
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**DB_PASSWORD:**
Придумайте сложный пароль, например: `RentAll2024!Secure#DB`

**Остальные параметры** уже правильно заполнены.

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

---

### ☐ **8. Запуск деплоя**

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

⏱️ **Ждите 5-10 минут...**

Скрипт автоматически:
- ✅ Установит зависимости (Python, Node.js, PostgreSQL, Nginx)
- ✅ Создаст БД с паролем из .env
- ✅ Применит миграции
- ✅ Соберет React production build
- ✅ Настроит Nginx и systemd
- ✅ Запустит сервисы

---

### ☐ **9. Настройка DNS**

Зайдите в панель управления вашего регистратора доменов и создайте:

| Тип | Имя | Значение       | TTL  |
|-----|-----|----------------|------|
| A   | @   | 62.192.174.91  | 3600 |
| A   | www | 62.192.174.91  | 3600 |

**Проверка (может занять 15-30 минут):**
```bash
ping rentalall.ru
```

Должен показывать: `62.192.174.91`

---

### ☐ **10. Получение SSL сертификата**

**После того, как DNS заработает:**

```bash
certbot --nginx -d rentalall.ru -d www.rentalall.ru
```

- Введите ваш email
- Согласитесь с условиями (Y)
- Автоматическое перенаправление HTTP → HTTPS (Y)

```bash
systemctl restart nginx
```

---

### ☐ **11. Проверка работы**

Откройте в браузере:

- 🌐 **Сайт**: https://rentalall.ru
- 🔧 **Админка**: https://rentalall.ru/admin
  - Логин: `admin`
  - Пароль: `admin123`
- 📚 **API Docs**: https://rentalall.ru/swagger

**Проверьте:**
- ✅ Главная страница загружается
- ✅ Можно зарегистрироваться
- ✅ Площадки отображаются
- ✅ Карта работает
- ✅ Админка доступна

---

## 🔐 **ЧАСТЬ 3: БЕЗОПАСНОСТЬ (ОБЯЗАТЕЛЬНО!)**

### ☐ **12. Смена root-пароля**

```bash
passwd
```

Придумайте новый сложный пароль и **запишите его!**

---

### ☐ **13. Смена Django admin пароля**

1. Зайдите: https://rentalall.ru/admin
2. Логин: `admin`, пароль: `admin123`
3. Нажмите "admin" (справа вверху) → "Change password"
4. Установите новый пароль и **запишите его!**

---

### ☐ **14. Настройка Firewall**

```bash
apt install ufw -y
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

При вопросе подтвердите: `y`

---

### ☐ **15. Проверка автозапуска сервисов**

```bash
systemctl is-enabled rentalall.service
systemctl is-enabled nginx
```

Оба должны показывать: `enabled`

---

## 📊 **ПРОВЕРКА СТАТУСА**

```bash
# Статус Django
systemctl status rentalall.service

# Статус Nginx
systemctl status nginx

# Логи Django (последние 20 строк)
journalctl -u rentalall.service -n 20

# Логи Nginx
tail -n 20 /var/log/nginx/rentalall_error.log
```

Все должно быть **active (running)** и **без ошибок**.

---

## 🎉 **ГОТОВО!**

### ✅ **Ваш сайт работает:**
- 🌐 https://rentalall.ru
- 🔧 https://rentalall.ru/admin

### ✅ **Резервное копирование:**
- Код на GitHub
- БД на сервере (настройте регулярные бэкапы)

### ✅ **Безопасность:**
- SSL/HTTPS ✅
- Firewall ✅
- Пароли изменены ✅

---

## 🔄 **ОБНОВЛЕНИЕ ПРОЕКТА (после изменений)**

### На локальном ПК:
```powershell
cd E:\Study\Диплом\rentalall
git add .
git commit -m "Описание изменений"
git push origin main
```

### На сервере:
```bash
cd /root/rentalall
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
deactivate

# Frontend
cd ../frontend
npm install
npm run build

# Перезапуск
systemctl restart rentalall.service
systemctl restart nginx
```

---

## 📚 **ДОКУМЕНТАЦИЯ**

- 📖 **Быстрый старт**: [deploy/QUICK_START.md](deploy/QUICK_START.md)
- 📖 **Полная инструкция**: [deploy/GITHUB_DEPLOY.md](deploy/GITHUB_DEPLOY.md)
- 📖 **Troubleshooting**: [deploy/DEPLOYMENT_GUIDE.md](deploy/DEPLOYMENT_GUIDE.md)

---

## 🆘 **ПОМОЩЬ**

### Полезные команды:

```bash
# Просмотр логов в реальном времени
journalctl -u rentalall.service -f

# Перезапуск сервисов
systemctl restart rentalall.service
systemctl restart nginx

# Проверка конфигурации Nginx
nginx -t

# Подключение к БД
sudo -u postgres psql rentalall_db
```

### Если что-то не работает:
1. Проверьте логи (команды выше)
2. Проверьте .env файл: `cat /root/rentalall/backend/.env`
3. Проверьте статус сервисов: `systemctl status rentalall.service nginx`

---

## 🎓 **ДЛЯ ДИПЛОМА**

### Скриншоты для защиты:
- ✅ Главная страница сайта
- ✅ Каталог площадок
- ✅ Страница площадки с бронированием
- ✅ Карта с площадками
- ✅ Django Admin панель
- ✅ Swagger API документация
- ✅ SSL сертификат (замок в браузере)

### Данные для защиты:
- **URL**: https://rentalall.ru
- **GitHub**: https://github.com/YOUR_USERNAME/rentalall
- **Стек**: Django 4.2, React 18, PostgreSQL 15, Nginx
- **Сервер**: Ubuntu, 62.192.174.91
- **SSL**: Let's Encrypt (бесплатный, автообновляемый)

---

**✅ Отметьте все пункты по мере выполнения!**

**🎉 Удачи с защитой диплома!** 🚀

