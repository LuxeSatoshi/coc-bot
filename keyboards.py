from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Состав клана", callback_data="clan_members")],
            [InlineKeyboardButton(text="🔄 Проверить изменения", callback_data="check_updates")]
        ]
    )
    return keyboard
