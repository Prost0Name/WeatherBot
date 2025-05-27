from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ Узнать больше о боте", callback_data="about_bot")]
        ]
    )

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_start")]
        ]
    )

def get_weather_keyboard(city: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Прогноз на 5 дней", callback_data=f"forecast_{city}")]
        ]
    )

def get_forecast_keyboard(city: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Подробнее", callback_data=f"detailed_forecast_{city}")],
            [InlineKeyboardButton(text="◀️ Назад к погоде", callback_data=f"back_to_weather_{city}")]
        ]
    )

def get_graph_keyboard(city: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад к прогнозу", callback_data=f"forecast_{city}")]
        ]
    )
