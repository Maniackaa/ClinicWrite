import asyncio
import datetime

import structlog
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InputFile, FSInputFile
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from config_data.conf import conf, BASE_DIR
from handlers import action_handlers, user_handlers
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = structlog.get_logger()
bot: Bot = Bot(token=conf.tg_bot.token)

async def send_telegram_message(chat_id: int, text: str):
    video_path = BASE_DIR / 'video.MP4'
    logger.info(f'send_telegram_message {chat_id}')
    video = FSInputFile(video_path)
    await bot.send_video(chat_id, video, caption=text, parse_mode=ParseMode.HTML)

async def main():
    logger.info('Starting bot')

    # Создаем хранилище для FSM
    storage = MemoryStorage()
    dp: Dispatcher = Dispatcher(storage=storage)
    dp.include_router(action_handlers.router)
    dp.include_router(user_handlers.router)
    scheduler = AsyncIOScheduler(
        jobstores={"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
    )
    dp['scheduler'] = scheduler
    if not scheduler.running:
        scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        admins = conf.tg_bot.admin_ids
        if admins:
            await bot.send_message(
                conf.tg_bot.admin_ids[0], f'Бот запущен.')
        await bot.send_message(chat_id=-1002732338521, text='ТЕСТ')
    except:
        logger.critical(f'Не могу отравить сообщение {conf.tg_bot.admin_ids[0]}')

    allowed_updates = [
        "message",  # Новое сообщение
        "edited_message",  # Отредактированное сообщение
        "channel_post",  # Новый пост в канале
        "edited_channel_post",  # Отредактированный пост в канале
        "inline_query",  # Inline-запрос
        "chosen_inline_result",  # Выбранный inline-результат
        "callback_query",  # Callback-кнопка (inline-кнопки)
        "shipping_query",  # Запрос по доставке (бот-платежи)
        "pre_checkout_query",  # Pre-checkout (бот-платежи)
        "poll",  # Новый опрос
        "poll_answer",  # Ответ на опрос
        "my_chat_member",  # Изменение статуса бота в чате
        "chat_member",  # Изменение статуса пользователя в чате
        "chat_join_request",  # Запрос на вступление в чат (бот — админ группы)
    ]

    await dp.start_polling(bot, allowed_updates=["message", "my_chat_member", "chat_member", "callback_query", "channel_post"])


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Bot stopped!')