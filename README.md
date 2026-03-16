# ТГ РАСПИСАНИЕ

## BUILD 1.3
Переделал автоопределение недели. Добавил /debug_week

## BUILD 1.4
Запись в users.json каждые 10 минут, вместо после каждого изменения.
Корректное завершение работы с сохранением файлов.

## DOCKER UPDATE
Упаковал бота в докер.


# Установка:
## Докер
```bash
git clone https://github.com/siskahui/TGBOT.git
cd TGBOT
cp .env.example > .env && nano .env
docker compose up -d --build
```

## Python
```bash
git clone https://github.com/siskahui/TGBOT.git
cd TGBOT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example > .env && nano .env
python tg.py
```
