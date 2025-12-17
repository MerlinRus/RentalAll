# ⚡ Быстрый старт: Деплой через GitHub

## 📍 **НА ЛОКАЛЬНОМ ПК (Windows):**

### 1️⃣ **Инициализация Git**

```powershell
cd E:\Study\Диплом\rentalall
git init
git add .
git commit -m "Initial commit"
```

---

### 2️⃣ **Создание репозитория на GitHub**

1. Зайдите: https://github.com/new
2. Repository name: `rentalall`
3. Private ✅
4. **НЕ добавляйте** README, .gitignore, LICENSE
5. **Create repository**

---

### 3️⃣ **Push на GitHub**

```powershell
# Замените YOUR_USERNAME на ваш GitHub username!
git remote add origin https://github.com/YOUR_USERNAME/rentalall.git
git branch -M main
git push -u origin main
```

При запросе авторизации:
- Username: ваш GitHub username
- Password: используйте **Personal Access Token** (не пароль!)

**Как получить токен:**
GitHub → Settings → Developer settings → Personal access tokens → Generate new token → Выберите `repo` → Generate → Скопируйте токен

---

## 🖥️ **НА СЕРВЕРЕ:**

### 4️⃣ **Подключение к серверу**

```powershell
ssh root@62.192.174.91
```
Пароль: `15Y02MR8QwQr`

---

### 5️⃣ **Клонирование с GitHub**

```bash
cd /root
git clone https://github.com/YOUR_USERNAME/rentalall.git
cd rentalall
```

---

### 6️⃣ **Настройка .env**

```bash
cp deploy/env.production.example backend/.env
nano backend/.env
```

**Обязательно измените:**
- `SECRET_KEY` — сгенерируйте:
  ```bash
  python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- `DB_PASSWORD` — придумайте сложный пароль (например, `RentAll2024!Secure`)

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

---

### 7️⃣ **Запуск деплоя**

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

⏱️ Ждите 5-10 минут...

---

### 8️⃣ **Настройка DNS**

В панели регистратора доменов создайте A-записи:
- `rentalall.ru` → `62.192.174.91`
- `www.rentalall.ru` → `62.192.174.91`

Проверьте (может занять 15-30 минут):
```bash
ping rentalall.ru
```

---

### 9️⃣ **SSL сертификат**

После того, как DNS заработает:

```bash
certbot --nginx -d rentalall.ru -d www.rentalall.ru
systemctl restart nginx
```

---

### 🔟 **Проверка**

Откройте: https://rentalall.ru 🎉

---

## 🔐 **ВАЖНО! После деплоя:**

```bash
# 1. Смените root-пароль
passwd

# 2. Настройте firewall
apt install ufw
ufw allow 22,80,443/tcp
ufw enable
```

**3. Смените Django admin пароль:**
- Зайдите: https://rentalall.ru/admin
- Логин: `admin`, пароль: `admin123`
- Нажмите "admin" → "Change password"

---

## 🔄 **Обновление проекта:**

### На локальном ПК:
```powershell
git add .
git commit -m "Описание изменений"
git push origin main
```

### На сервере:
```bash
cd /root/rentalall
git pull origin main
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
deactivate
cd ../frontend
npm run build
systemctl restart rentalall.service
systemctl restart nginx
```

---

## 📚 **Полная документация:**

- **Подробная инструкция:** [GITHUB_DEPLOY.md](./GITHUB_DEPLOY.md)
- **Troubleshooting:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 🆘 **Если что-то не работает:**

```bash
# Логи Django
journalctl -u rentalall.service -f

# Логи Nginx
tail -f /var/log/nginx/rentalall_error.log

# Статус сервисов
systemctl status rentalall.service
systemctl status nginx
```

---

✅ **Готово! Ваш сайт работает на https://rentalall.ru** 🚀

