"""
Бот: постит видео + текст в Telegram-канал через случайный
интервал времени (в заданном диапазоне минут).

Поддерживает шаблоны с рандомизацией:
  В messages.txt можно писать:
  {Привет|Здарова|Йо}, смотри видео!
  Бот сам выберет один вариант из каждой группы.

Также поддерживает один кастомный (премиум) эмодзи в начале сообщения.
"""

import asyncio
import logging
import os
import random
import re
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, MessageEntity

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("channel_poster")

# ID премиум-эмодзи
CUSTOM_EMOJI_ID = "5348404473129614535"


def load_messages(path: str) -> list[str]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Файл с сообщениями не найден: {path}. "
            "Создай messages.txt и впиши туда текст(ы) сообщений."
        )
    raw = file_path.read_text(encoding="utf-8")
    parts = [p.strip() for p in raw.split("\n---\n")]
    messages = [p for p in parts if p]
    if not messages:
        raise ValueError(f"Файл {path} пуст — добавь хотя бы одно сообщение.")
    return messages


def render_template(template: str) -> str:
    """Заменяет все {вариант1|вариант2|вариант3} на случайный вариант."""
    def replace_group(match: re.Match) -> str:
        options = [opt.strip() for opt in match.group(1).split("|") if opt.strip()]
        if not options:
            return ""
        return random.choice(options)

    return re.sub(r"\{([^{}]+)\}", replace_group, template)


async def main() -> None:
    bot_token = os.environ["BOT_TOKEN"]
    channel_id_raw = os.environ["CHANNEL_ID"]
    channel_id: int | str = channel_id_raw
    try:
        channel_id = int(channel_id_raw)
    except ValueError:
        pass

    messages_file = os.environ.get("MESSAGES_FILE", "messages.txt")
    video_file = os.environ.get("VIDEO_FILE", "video.mp4")
    min_interval = int(os.environ.get("MIN_INTERVAL_MIN", "30"))
    max_interval = int(os.environ.get("MAX_INTERVAL_MIN", "60"))
    send_on_start = os.environ.get("SEND_ON_START", "0") == "1"

    if min_interval <= 0 or max_interval <= 0 or min_interval > max_interval:
        raise ValueError(
            f"Некорректный диапазон интервалов: MIN_INTERVAL_MIN={min_interval}, "
            f"MAX_INTERVAL_MIN={max_interval}"
        )

    video_path = Path(video_file)
    if not video_path.exists():
        raise FileNotFoundError(
            f"Видеофайл не найден: {video_file}. "
            "Положи файл video.mp4 в папку проекта."
        )

    messages = load_messages(messages_file)
    log.info("Загружено шаблонов: %d", len(messages))
    log.info("Видео: %s", video_file)
    log.info("Интервал между постами: %d–%d мин", min_interval, max_interval)

    bot = Bot(token=bot_token)

    try:
        me = await bot.get_me()
        log.info("Бот запущен: @%s", me.username)

        if not send_on_start:
            first_delay = random.randint(min_interval, max_interval)
            log.info("Первая отправка через %d мин", first_delay)
            await asyncio.sleep(first_delay * 60)

        while True:
            template = random.choice(messages)
            text = render_template(template)

            # Placeholder для кастомного эмодзи в начале (обычный эмодзи + пробел)
            caption = "🔥 " + text

            # Entity: заменяем placeholder на кастомный эмодзи
            # "🔥 " в UTF-16 занимает 2 единицы длины
            entities = [
                MessageEntity(
                    type="custom_emoji",
                    offset=0,
                    length=2,
                    custom_emoji_id=CUSTOM_EMOJI_ID,
                )
            ]

            try:
                video = FSInputFile(video_path)
                await bot.send_video(
                    chat_id=channel_id,
                    video=video,
                    caption=caption,
                    caption_entities=entities,
                )
                log.info("Видео + текст отправлены: %s", text[:80].replace("\n", " "))
            except Exception as e:
                log.error("Ошибка при отправке: %s", e)

            delay = random.randint(min_interval, max_interval)
            log.info("Следующая отправка через %d мин", delay)
            await asyncio.sleep(delay * 60)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
