# Channel Poster Bot

Бот шлёт сообщения в Telegram-канал через случайный интервал времени
(диапазон задаётся переменными окружения).

## 1. Создать бота

1. В Telegram напиши @BotFather → `/newbot` → получишь `BOT_TOKEN`.
2. Добавь бота в свой канал **администратором** с правом "Публикация сообщений".
3. Узнай `CHANNEL_ID`:
   - Если канал публичный — можно использовать `@username_канала`.
   - Если приватный — перешли любое сообщение из канала боту
     [@userinfobot](https://t.me/userinfobot) или используй
     https://api.telegram.org/bot<TOKEN>/getUpdates после того как
     что-то напишешь/перешлёшь в канал — там будет `"chat":{"id": -100...}`.

## 2. Настроить тексты сообщений

Отредактируй `messages.txt`. Каждое сообщение — отдельным блоком,
блоки разделяются строкой `---` на отдельной строке (это позволяет
писать многострочные сообщения).

## 3. Локальный запуск (проверить, что всё работает)

```bash
pip install -r requirements.txt
cp .env.example .env
# впиши реальные BOT_TOKEN и CHANNEL_ID в .env
export $(cat .env | xargs)   # или используй python-dotenv / direnv
python bot.py
```

Для быстрой проверки поставь `SEND_ON_START=1` и маленький
`MIN_INTERVAL_MIN`/`MAX_INTERVAL_MIN` (например 1/2), чтобы не ждать
долго первого сообщения.

## 4. Деплой на Railway

1. Залей этот проект в GitHub-репозиторий (можно приватный):
   ```bash
   git init
   git add .
   git commit -m "channel poster bot"
   git remote add origin <ссылка на твой пустой репозиторий>
   git push -u origin main
   ```
2. На https://railway.app → **New Project** → **Deploy from GitHub repo**
   → выбери этот репозиторий.
3. Railway сам увидит `requirements.txt` и `Procfile` и поставит нужное.
   Важно: это **worker**-процесс (не веб-сервер), поэтому в настройках
   сервиса убедись, что Railway запускает его как worker (не ждёт, что
   на порту кто-то слушает) — обычно достаточно, что в `Procfile`
   указано `worker:`, Railway сам не будет требовать открытый порт.
4. В разделе **Variables** добавь:
   - `BOT_TOKEN`
   - `CHANNEL_ID`
   - `MIN_INTERVAL_MIN`
   - `MAX_INTERVAL_MIN`
   - (опционально) `MESSAGES_FILE`, `SEND_ON_START`
5. Деплой запустится автоматически. Смотри логи в Railway — там будут
   видны строки вида "Бот запущен: @имя_бота" и "Следующая отправка
   через N мин".

## 5. Изменить тексты сообщений после деплоя

Проще всего — отредактировать `messages.txt` локально, закоммитить и
запушить (`git add messages.txt && git commit -m "update texts" && git push`),
Railway передеплоит сам.
