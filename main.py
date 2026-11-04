import asyncio
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TG_TOKEN, CLAN_TAG
from coc_api import get_clan_members
from database import init_db, sync_members
from keyboards import get_main_keyboard

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# Простая веб-страница для пинга от UptimeRobot
async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render передает порт через переменную окружения PORT, по умолчанию берем 8080
    import os
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# Функция периодической проверки состава клана
async def scheduled_clan_check():
    if not CLAN_TAG:
        return
    
    members = await get_clan_members()
    if members is None:
        return
        
    joined, left = sync_members(members)
    
    # Если кто-то зашел или вышел, можно слать уведомление (например, в консоль или заранее заготовленный чат)
    if joined or left:
        logging.info(f"Изменения в клане! Вошли: {joined}, Вышли: {left}")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Это бот для мониторинга клана Clash of Clans.\n"
        "Используй кнопки ниже для управления:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "clan_members")
async def cb_clan_members(callback: CallbackQuery):
    await callback.answer()
    members = await get_clan_members()
    
    if not members:
        await callback.message.answer("❌ Не удалось получить данные из API клана. Проверь токен и тег.")
        return
        
    text = f"👥 **Состав клана (всего: {len(members)}):**\n\n"
    for m in members:
        text += f"- {m['name']} ({m['role']}) [Трофеев: {m['trophies']}]\n"
        
    # Телеграм ограничивает длину сообщения, но для клана обычно хватает
    if len(text) > 4096:
        text = text[:4096]
        
    await callback.message.answer(text, parse_mode="Markdown")

@dp.callback_query(F.data == "check_updates")
async def cb_check_updates(callback: CallbackQuery):
    await callback.answer("🔄 Проверяю изменения...")
    members = await get_clan_members()
    
    if members is None:
        await callback.message.answer("❌ Ошибка при запросе к API.")
        return
        
    joined, left = sync_members(members)
    
    response_text = "📊 **Результат проверки:**\n"
    response_text += f"🟢 Новых участников: {len(joined)}\n"
    response_text += f"🔴 Выбывших участников: {len(left)}\n"
    
    if joined:
        response_text += f"\nВошли: {', '.join(joined)}"
    if left:
        response_text += f"\nВышли: {', '.join(left)}"
        
    await callback.message.answer(response_text, parse_mode="Markdown")

async def main():
    init_db()
    
    # Запуск планировщика проверки клана (например, каждые 30 минут)
    scheduler.add_job(scheduled_clan_check, "interval", minutes=30)
    scheduler.start()
    
    # Запускаем фоновый веб-сервер для Render
    asyncio.create_task(web_server())
    
    # Запуск поллинга бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
