from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ℹ️ Узнать больше о боте", callback_data="about_bot")
            ]
        ]
    )

def get_back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")
            ]
        ]
    )

def get_weather_keyboard(city: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📅 Прогноз на 5 дней", callback_data=f"forecast_{city}")
            ]
        ]
    )
