"""
Простой бот: постит сообщения в Telegram-канал через случайный
интервал времени (в заданном диапазоне минут).

Настройка — через переменные окружения (см. .env.example):
  BOT_TOKEN        — токен бота от @BotFather
  CHANNEL_ID        — id канала (например -1001234567890) или @username канала
  MESSAGES_FILE     — путь к файлу messages.txt со списком сообщений (по умолчанию messages.txt)
  MIN_INTERVAL_MIN  — минимальный интервал между постами, в минутах
  MAX_INTERVAL_MIN  — максимальный интервал между постами, в минутах
  SEND_ON_START     — "1", чтобы отправить первое сообщение сразу при старте (по умолчанию "0")
"""

import asyncio
import logging
import os
import random
from pathlib import Path

from aiogram import Bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("channel_poster")


def load_messages(path: str) -> list[str]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Файл с сообщениями не найден: {path}. "
            "Создай messages.txt и впиши туда текст(ы) сообщений, "
            "каждое сообщение — на отдельной строке. "
            "Если нужны переносы строк внутри одного сообщения, "
            "раздели сообщения строкой, состоящей только из '---'."
        )
    raw = file_path.read_text(encoding="utf-8")
    # Сообщения разделяются строкой '---' (на отдельной строке),
    # это позволяет иметь многострочные сообщения.
    parts = [p.strip() for p in raw.split("\n---\n")]
    messages = [p for p in parts if p]
    if not messages:
        raise ValueError(f"Файл {path} пуст — добавь хотя бы одно сообщение.")
    return messages


async def main() -> None:
    bot_token = os.environ["BOT_TOKEN"]
    channel_id_raw = os.environ["CHANNEL_ID"]
    # channel_id может быть числом (-100...) или @username
    channel_id: int | str = channel_id_raw
    try:
        channel_id = int(channel_id_raw)
    except ValueError:
        pass  # оставляем как строку, например "@mychannel"

    messages_file = os.environ.get("MESSAGES_FILE", "messages.txt")
    min_interval = int(os.environ.get("MIN_INTERVAL_MIN", "30"))
    max_interval = int(os.environ.get("MAX_INTERVAL_MIN", "90"))
    send_on_start = os.environ.get("SEND_ON_START", "0") == "1"

    if min_interval <= 0 or max_interval <= 0 or min_interval > max_interval:
        raise ValueError(
            f"Некорректный диапазон интервалов: MIN_INTERVAL_MIN={min_interval}, "
            f"MAX_INTERVAL_MIN={max_interval}"
        )

    messages = load_messages(messages_file)
    log.info("Загружено сообщений: %d", len(messages))
    log.info("Интервал между постами: %d–%d мин", min_interval, max_interval)

    bot = Bot(token=bot_token)

    try:
        # Проверим, что токен рабочий и бот видит себя
        me = await bot.get_me()
        log.info("Бот запущен: @%s", me.username)

        if not send_on_start:
            first_delay = random.randint(min_interval, max_interval)
            log.info("Первая отправка через %d мин", first_delay)
            await asyncio.sleep(first_delay * 60)

        while True:
            text = random.choice(messages)
            try:
                await bot.send_message(chat_id=channel_id, text=text)
                log.info("Сообщение отправлено (%d симв.)", len(text))
            except Exception as e:
                log.error("Ошибка при отправке: %s", e)

            delay = random.randint(min_interval, max_interval)
            log.info("Следующая отправка через %d мин", delay)
            await asyncio.sleep(delay * 60)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
