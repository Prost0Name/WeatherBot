import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from weather import get_weather, get_weather_by_coords, get_weather_forecast, create_temperature_graph, get_weather_forecast_by_coords
from notifications import send_weather_notifications
from database.users import add_user, update_user_city, update_user_notification_time, delete_user_notifications
from keyboards import get_start_keyboard, get_back_keyboard, get_weather_keyboard, get_forecast_keyboard, get_graph_keyboard, get_main_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Status(StatesGroup):
    waiting_for_city = State()
    waiting_for_time = State()
    waiting_moment_city = State()
    waiting_manual_city = State()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await add_user(                          
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    # Отправляем приветственное сообщение с инлайн-кнопкой
    await message.answer("""
👋 Привет! Я покажу погоду сейчас и на неделю вперёд — по городу или геолокации.

📍 Отправь локацию или
🏙 Введи название города

🔔 Можно включить ежедневную рассылку прогноза.
❌ Отключить её — тоже легко.

Выбери нужную кнопку ниже 👇
""",
        reply_markup=get_start_keyboard()
    )

    # Отправляем сообщение с основной клавиатурой
    await message.answer(
        "Используйте кнопки ниже для навигации:",
        reply_markup=get_main_keyboard()
    )
    
    await state.set_state(Status.waiting_moment_city)


@dp.callback_query(F.data == "about_bot")
async def process_about_callback(callback: CallbackQuery):
    about_text = ("""
🌤 Погодный бот
Узнай актуальную погоду и прогноз на неделю в один клик!

📍 Определяет погоду по геолокации или выбранному городу
📅 Прогноз на 7 дней вперёд
📊 Удобные графики температуры, осадков и других показателей

Просто отправь свою геолокацию или введи название города — бот сделает всё сам!

🛠 Команды и кнопки:
/start — начать работу с ботом
🏙 Ввести город — задать любой населённый пункт
📍 Отправить геолокацию — узнать погоду по текущему местоположению
🔔 Ежедневное уведомление — настрой ежедневную рассылку прогноза в удобное время
❌ Удалить ежедневное уведомление — отключи рассылку в любой момент    
    """)
    
    await callback.message.edit_text(about_text, reply_markup=get_back_keyboard())
    await callback.answer()


@dp.callback_query(lambda c: c.data == "back_to_start")
async def process_back_callback(callback_query: types.CallbackQuery):
    start_text = """
👋 Привет! Я покажу погоду сейчас и на неделю вперёд — по городу или геолокации.

📍 Отправь локацию или
🏙 Введи название города

🔔 Можно включить ежедневную рассылку прогноза.
❌ Отключить её — тоже легко.

Выбери нужную кнопку ниже 👇
"""
    
    await callback_query.message.edit_text(start_text, reply_markup=get_start_keyboard())
    await callback_query.answer()


@dp.message(
    StateFilter(Status.waiting_moment_city),
    F.text == '🏙 Ввести город'
)
async def setting_manual_city(message: Message, state: FSMContext):
    await message.answer('Введите город')
    await state.clear()                            #Switch to next step handler
    await state.set_state(Status.waiting_manual_city)


@dp.message(
    StateFilter(Status.waiting_manual_city))
async def process_manual_city(message: Message, state: FSMContext):
    city = message.text.strip()

    try:                                       
        weather_data = await get_weather(city)
        await message.answer(weather_data, reply_markup=get_weather_keyboard(city))
        await state.clear()
        await state.set_state(Status.waiting_moment_city)

    except Exception as e:
        await message.answer(f"🚫 Город {city} не найден. Попробуйте еще раз:")
        await state.clear()
        await state.set_state(Status.waiting_moment_city)


@dp.message(
    F.content_type == 'location',
    StateFilter(Status.waiting_moment_city)
)
async def handle_location(message: Message, state: FSMContext):
    lat = message.location.latitude        
    lon = message.location.longitude      

    try:
        # Сохраняем координаты в состоянии
        await state.update_data(lat=lat, lon=lon)
        logger.info(f"Сохранены координаты: lat={lat}, lon={lon}")
        
        weather_text = await get_weather_by_coords(lat, lon)
        # Сохраняем название города из ответа API
        city_name = weather_text.split('(')[1].split(')')[0]
        await state.update_data(city_name=city_name)
        logger.info(f"Сохранено название города: {city_name}")
        
        await message.answer(weather_text, reply_markup=get_weather_keyboard("вашем городе"))
        await state.set_state(Status.waiting_moment_city)
    except Exception as e:
        logger.error(f"Ошибка при обработке геолокации: {e}")
        await message.answer("😢 Не смог получить погоду для этой точки")
        await state.clear()
        await state.set_state(Status.waiting_moment_city)


@dp.message(F.text == '🔔 Ежедневное уведомление')
async def cmd_setup(message: Message, state: FSMContext):
    await message.answer(
        "Давайте настроим ежедневные уведомления о погоде. В каком населенном пункте вы хотите получать прогноз?"
    )
    await state.clear()
    await state.set_state(Status.waiting_for_city)


@dp.message(StateFilter(Status.waiting_for_city))
async def process_city(message: Message, state: FSMContext):
    city = message.text
    try:
        await get_weather(city)                    
        await state.update_data(city=city)        
        await update_user_city(                   
            message.from_user.id, city
        )

        await message.answer(
            f"Отлично! Город {city} установлен."
            "Теперь укажите время для ежедневных уведомлений в формате ЧЧ:ММ (например, 08:00)"
        )
        await state.set_state(Status.waiting_for_time)
    except Exception as e:
        await message.answer(f"Не удалось найти город {city}. Пожалуйста, проверьте название и попробуйте снова.")


@dp.message(StateFilter(Status.waiting_for_time))
async def process_time(message: Message, state: FSMContext):
    time_text = message.text
    if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', time_text):
        await message.answer("Пожалуйста, укажите время в формате ЧЧ:ММ (например, 08:00)")
        return

    data = await state.get_data()                 
    city = data.get('city')
    await update_user_notification_time(message.from_user.id, time_text)
    await message.answer(
        f"Настройка завершена! Вы будете получать прогноз погоды для города {city} каждый день в {time_text}.\n\n",
        reply_markup=get_start_keyboard())
    await state.clear()
    await state.set_state(Status.waiting_moment_city)


@dp.message(F.text == '❌ Удалить ежедневное уведомление')
async def cmd_delete_notifications(message: Message, state: FSMContext):
    try:                                        
        await delete_user_notifications(message.from_user.id)
        await message.answer(
            "Ваши ежедневные уведомления о погоде были успешно удалены.\n",
            reply_markup=get_start_keyboard()
        )
        await state.clear()
        await state.set_state(Status.waiting_moment_city)
    except Exception as e:
        await message.answer("Произошла ошибка при удалении уведомлений. Пожалуйста, попробуйте позже.",
            reply_markup = get_start_keyboard())
        await state.clear()
        await state.set_state(Status.waiting_moment_city)


@dp.callback_query(lambda c: c.data.startswith('forecast_'))
async def process_forecast_callback(callback_query: types.CallbackQuery, state: FSMContext):
    city = callback_query.data.split('_')[1]
    try:
        if city == "вашем городе":
            # Получаем данные из состояния
            data = await state.get_data()
            lat = data.get('lat')
            lon = data.get('lon')
            city_name = data.get('city_name')
            
            logger.info(f"Получены данные из состояния: lat={lat}, lon={lon}, city_name={city_name}")
            
            if lat and lon:
                forecast = await get_weather_forecast_by_coords(lat, lon)
                # Обновляем клавиатуру с правильным названием города
                keyboard = get_forecast_keyboard(city_name)
            else:
                raise Exception("Не удалось получить координаты")
        else:
            forecast = await get_weather_forecast(city)
            keyboard = get_forecast_keyboard(city)
            
        # Удаляем предыдущее сообщение
        await callback_query.message.delete()
        # Отправляем новое сообщение с прогнозом
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=forecast,
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка при получении прогноза: {e}")
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Не удалось получить прогноз погоды: {str(e)}",
            reply_markup=get_back_keyboard()
        )


@dp.callback_query(lambda c: c.data.startswith('detailed_forecast_'))
async def process_detailed_forecast_callback(callback_query: types.CallbackQuery):
    city = callback_query.data.split('_')[2]
    try:
        # Создаем график
        graph_bytes = await create_temperature_graph(city)
        
        # Удаляем предыдущее сообщение
        await callback_query.message.delete()
        
        # Отправляем график как фото
        await callback_query.message.answer_photo(
            photo=types.BufferedInputFile(graph_bytes, filename="temperature_graph.png"),
            caption=f"📊 График температуры в городе {city}",
            reply_markup=get_graph_keyboard(city)
        )
    except Exception as e:
        await callback_query.message.edit_text(
            text=f"Не удалось создать график: {str(e)}",
            reply_markup=get_forecast_keyboard(city)
        )


@dp.callback_query(lambda c: c.data.startswith('back_to_weather_'))
async def process_back_to_weather_callback(callback_query: types.CallbackQuery):
    city = callback_query.data.split('_')[3]
    try:
        weather_data = await get_weather(city)
        # Удаляем предыдущее сообщение
        await callback_query.message.delete()
        # Отправляем новое сообщение с погодой
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=weather_data,
            reply_markup=get_weather_keyboard(city)
        )
    except Exception as e:
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"Не удалось получить погоду: {str(e)}",
            reply_markup=get_back_keyboard()
        )


async def setup():
    asyncio.create_task(send_weather_notifications(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(setup())