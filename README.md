# 📅 ТГ БОТ КС ПГУТИ — Расписание

Телеграм-бот для просмотра расписания КС ПГУТИ.  
Поддерживает группы, рассылки, статистику и админ-функции.

---

## 🚀 Возможности

- 📆 Просмотр расписания (сегодня / неделя)
- 🔔 Автоматические рассылки
- 👥 Поддержка пользователей (support mode)
- 📊 Статистика использования
- 🛠️ Админ-панель
- 🐳 Поддержка Docker

---

## 📄 Документация

- [📜 Changelog](./CHANGELOG.md)

---

## ⚙️ Переменные окружения

Создай `.env` файл на основе `.env.example`:

```.env
RELEASE_TOKEN=токен бота (через @botfather)
OWNERID=твой Telegram ID (для админ-команд)
```

---

## 🛠️ Установка

### 🐳 Docker (рекомендуется)

```bash
git clone https://github.com/Sp0nge-bob/TGBOT
cd TGBOT

cp .env.example .env
nano .env

docker compose up -d --build
```

---

### 🐍 Python

```bash
git clone https://github.com/Sp0nge-bob/TGBOT
cd TGBOT

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
nano .env

python tg.py
```

---

## 📊 Основные команды

### 👤 Пользователь
- `/start` — запуск бота
- выбор группы
- просмотр расписания

### 🛠️ Админ
- `/admin` — админ панель
- `/stats` — статистика
- `/list_users` — список пользователей
- `/schedule_list` — активные рассылки
- `/broadcast` — рассылка
- `/broadtask` — редактирование рассылок

---

## 🌐 Прокси для Telegram API

Бот поддерживает подключение к Telegram через прокси (например, если сервер находится в ограниченной сети).

При этом:
- 📡 **Telegram API** работает через прокси  
- 🌍 **Запросы к сайту колледжа** идут напрямую (без прокси)

### ⚙️ Настройка

Добавь в `.env`:

```env
PROXY_URL=socks5://user:password@host:port
```

---

## 📦 Стек

- Python
- Docker
- Парсинг HTML

---

## 📌 Планы

- кнопки переключения дней
- улучшение UI
- дальнейшие оптимизации

---

## Readme update

- Найден баг с некорректным обновлением недели. Причины пока не выявлены.  
  Исправляется добавлением в crontab перезапуск бота каждый понедельник в 00:00 для переопределения недели  
  Вместо /root/TGBOT/restart.log укажите свой путь куда будут сохраняться логи перезапуска  
  `0 0 * * 1 echo "=== Перезапуск бота $(date '+%Y-%m-%d %H:%M:%S') ===" >> /root/TGBOT/restart.log 2>&1`  
  `0 0 * * 1 sleep 3 && cd /root/TGBOT && docker compose restart >> /root/TGBOT/restart.log 2>&1`  
