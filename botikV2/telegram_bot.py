import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router, types, F
from aiogram import Router
from aiogram import types
from database import init_db, add_user, add_review, add_purchase, add_referral, get_referrals_count  
from aiogram import Dispatcher


API_TOKEN = "8114305996:AAEH1AMwbHiCt9Rv12mSo3vsAZUVA81KAtY"

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dp.include_router(router) 

# Инициализируем базу данных при запуске бота
init_db()

launch_blum_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Launch Blum", url="https://blum.example.com")]
    ]
)

# Список котов с фото
cats = {
    "KAR": {"name": "Картезианский", "price": "1000₽", "photo": "image/6.jpg"},
    "SIA": {"name": "Сиамский", "price": "1600₽", "photo": "image/2.jpg"},
    "BEN": {"name": "Бенгальский", "price": "2700₽", "photo": "image/3.jpg"},
    "SIB": {"name": "Сибирская кошка", "price": "2800₽", "photo": "image/5.jpg"},
    "MAN": {"name": "Манчкин", "price": "3200₽", "photo": "image/4.jpg"},
    "SCO": {"name": "Шотландский", "price": "5000₽", "photo": "image/1.jpg"}
}
cat_facts = [
    "😺 Кошки спят в среднем 12-16 часов в день.",
    "🐾 У кошек на передних лапах по 5 пальцев, а на задних — только по 4.",
    "🧠 Мозг кошки по структуре на 90% похож на человеческий.",
    "👂 У кошек около 32 мышц в каждом ухе, чтобы лучше слышать.",
    "💗 Кошки мурлыкают не только от удовольствия, но и чтобы успокоиться.",
    "🎯 Кошка может прыгнуть на высоту до 5 раз превышающую её рост!",
    "🌙 Кошки видят в темноте в 6 раз лучше людей."
]

from database import add_user
# Главное меню
@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    add_user(user.id, user.username, f"{user.first_name} {user.last_name or ''}")

      # Обработка реферальных ссылок
    if len(message.text.split()) > 1 and message.text.split()[1].startswith('ref_'):
        referrer_id = int(message.text.split('_')[1])
        if referrer_id != user.id:
            add_referral(user.id, referrer_id)
            await bot.send_message(referrer_id, f"🎉 У вас новый реферал! @{user.username}")
    
    await send_main_menu(message)

# Состояния
class PurchaseState(StatesGroup):
    waiting_for_city = State()
    waiting_for_address = State()
    waiting_for_promo = State()

class ReviewState(StatesGroup):
    waiting_for_review = State()

class AdminBroadcast(StatesGroup):
    waiting_for_broadcast = State()

class CartState(StatesGroup):
    viewing = State()
    checking_out = State()

class PreorderState(StatesGroup):
    waiting_for_contacts = State()

# Функция отправки главного меню
async def send_main_menu(message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купить кота 🐱", callback_data="buy_menu")],
        [InlineKeyboardButton(text="Корзина 🛒", callback_data="view_cart")],
        [InlineKeyboardButton(text="Поддержка 🛠", callback_data="support")],
        [InlineKeyboardButton(text="Отзывы ⭐", callback_data="reviews_0")],
        [InlineKeyboardButton(text="Настройки ⚙️", callback_data="settings")],
        [InlineKeyboardButton(text="Факт о котах 📚", callback_data="cat_fact")],
        [InlineKeyboardButton(text="О магазине 🏪", callback_data="about")],
        [InlineKeyboardButton(text="Играть 🎮", callback_data="play_game")],
        [InlineKeyboardButton(text="Рефералы 👥", callback_data="referral_info")],
    ])
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)

# Меню покупки котов
@dp.callback_query(lambda c: c.data == "buy_menu")
async def buy_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=cats["KAR"]["name"], callback_data="KAR"),
            InlineKeyboardButton(text=cats["SIA"]["name"], callback_data="SIA")
        ],
        [
            InlineKeyboardButton(text=cats["BEN"]["name"], callback_data="BEN"),
            InlineKeyboardButton(text=cats["SIB"]["name"], callback_data="SIB")
        ],
        [
            InlineKeyboardButton(text=cats["MAN"]["name"], callback_data="MAN"),
            InlineKeyboardButton(text=cats["SCO"]["name"], callback_data="SCO")
        ],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    
    await callback.message.delete()
    await callback.message.answer("Выберите кота для покупки:", reply_markup=keyboard)
    await callback.answer()

# Обработка выбора кота с отправкой фото
@dp.callback_query(lambda c: c.data in cats)
async def show_cat_info(callback: types.CallbackQuery):
    cat = cats[callback.data]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купить", callback_data=f"buy_{callback.data}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="buy_menu")]  # Исправлено!
    ])

    photo_path = cat["photo"]
    photo = FSInputFile(photo_path)

    await callback.message.delete()  # Удаляем предыдущее сообщение

    # Отправляем фото с кнопками
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=photo,
        caption=f"{cat['name']} стоит {cat['price']}.\nХотите купить?",
        reply_markup=keyboard
    )
    await callback.answer()

# Состояния для ввода данных
class PurchaseState(StatesGroup):
    waiting_for_city = State()
    waiting_for_address = State()

# Обработка покупки
@router.callback_query(lambda c: c.data.startswith("buy_"))
async def buy_cat(callback: types.CallbackQuery, state: FSMContext):
    cat_key = callback.data.split("_")[1]
    cat = cats.get(cat_key)

    if cat:
        await state.update_data(selected_cat=cat)

        await callback.message.delete()
        await callback.message.answer("Введите город доставки:")
        await state.set_state(PurchaseState.waiting_for_city)

    await callback.answer()

# Ввод города
@router.message(PurchaseState.waiting_for_city)
async def enter_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(PurchaseState.waiting_for_address)  # Устанавливаем следующее состояние
    await message.answer("Введите адрес доставки:")

from database import add_purchase
# Ввод адреса и завершение покупки
@router.message(PurchaseState.waiting_for_address)
async def enter_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat = data["selected_cat"]
    user = message.from_user
    city = data.get("city")
    address = message.text

    # Добавляем покупку в БД
    add_purchase(
        user_id=user.id,
        cat_name=cat['name'],
        price=cat['price'],
        city=city,
        address=address
    )

    # Кнопка для возвращения в меню
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
        ]
    )

    # Отправляем сообщение с подтверждением и адресом
    await message.answer(
        f"🎉 Вы купили {cat['name']} за {cat['price']}! Спасибо за покупку! 🚚\n"
        f"Доставка прибудет в течение недели по адресу:\n"
        f"🏙 Город: {city}\n"
        f"🏠 Адрес: {address}",
        reply_markup=keyboard
    )
    
    await state.clear()

# Обработчик кнопки "Назад", возвращающий в главное меню
@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.delete()
    await send_main_menu(callback.message)
    await callback.answer()

# Обработчик кнопки "Поддержка"
@dp.callback_query(lambda c: c.data == "support")
async def support(callback: types.CallbackQuery):
    support_username = "@Lexa_Arbuz" 
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Связаться с поддержкой", url=f"https://t.me/{support_username}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])

    await callback.message.edit_text("Если у вас возникли вопросы, свяжитесь с нашей поддержкой:", reply_markup=keyboard)
    await callback.answer()

# Создание состояний для отзыва
class ReviewState(StatesGroup):
    waiting_for_review = State()

# Обработчик кнопки "Отзывы"
@dp.callback_query(lambda c: c.data.startswith("reviews"))
async def reviews(callback: types.CallbackQuery):
    index = int(callback.data.split("_")[1]) if "_" in callback.data else 0  # Текущий индекс комментария

    # Кнопки "Назад", "Вперед" и "Написать отзыв"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[ 
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"reviews_{index-1}") if index > 0 else InlineKeyboardButton(text=" ", callback_data="none"),
            InlineKeyboardButton(text="➡️ Вперед", callback_data=f"reviews_{index+1}") if index < len(comments) - 1 else InlineKeyboardButton(text=" ", callback_data="none")
        ],
        [InlineKeyboardButton(text="📝 Написать отзыв", callback_data="leave_review")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(comments[index], reply_markup=keyboard)
    await callback.answer()

class ReviewState(StatesGroup):
    waiting_for_review = State()

# Список комментариев (можно обновить с реальными данными)
comments = [
    "Комментарий 1: Отличный магазин, котики просто супер! 😻",
    "Комментарий 2: Быстро доставили, все понравилось! 🐾",
    "Комментарий 3: Спасибо за пушистика, он чудо! ❤️",
    "Комментарий 4: Цены адекватные, сервис на высоте. 💰",
    "Комментарий 5: Долго выбирал, но доволен покупкой! 🛍",
    "Комментарий 6: Всем советую этот магазин! ⭐⭐⭐⭐⭐"
]

# Обработчик кнопки "Написать отзыв"
@dp.callback_query(lambda c: c.data == "leave_review")
async def leave_review(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите ваш отзыв:")
    await state.set_state(ReviewState.waiting_for_review)  # ✅ Устанавливаем состояние через FSMContext

from database import add_review
@dp.message(ReviewState.waiting_for_review)
async def process_review(message: types.Message, state: FSMContext):
    user_review = message.text
    user = message.from_user
    add_review(user.id, user_review)
    comments.append(f"Комментарий {len(comments) + 1}: {user_review}")  

    # Клавиатура с кнопкой выхода в меню
    keyboard = InlineKeyboardMarkup(inline_keyboard=[ 
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
    ])

    # Отправляем пользователю сообщение, что отзыв был успешно добавлен
    await message.answer("Ваш отзыв был успешно добавлен! Спасибо за ваш вклад! 🎉", reply_markup=keyboard)
    await state.clear()  # ✅ Сбрасываем состояние после завершения

# Обработчик кнопки "🔙 В главное меню"
@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    # Здесь вы должны определить, что происходит при нажатии кнопки "В главное меню"
    await callback.message.edit_text("Вы вернулись в главное меню. Выберите нужный пункт:")

    # Клавиатура для главного меню
    main_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="reviews_0")],
        [InlineKeyboardButton(text="📝 Написать отзыв", callback_data="leave_review")]
    ])
    
    await callback.message.answer("Главное меню", reply_markup=main_menu_keyboard)

# Обработчик кнопки "О магазине"
@dp.callback_query(lambda c: c.data == "about")
async def about(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Создатель", callback_data="creator")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])

    about_text = (
        "🏪 *Добро пожаловать в наш магазин котиков!* 🐱\n\n"
        "🔹 Мы предлагаем самых милых и здоровых котов.\n"
        "🔹 Гарантия качества и документы на питомца.\n"
        "🔹 Доставка по всему миру! 🌍\n"
        "🔹 Поддержка 24/7 для всех клиентов.\n\n"
        "Нажмите *'Создатель'*, чтобы узнать, кто стоит за этим проектом! 👤"
    )

    await callback.message.edit_text(about_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

# Обработчик кнопки "Создатель"
@dp.callback_query(lambda c: c.data == "creator")
async def creator(callback: types.CallbackQuery):
    # Удаляем старое сообщение с информацией о магазине
    if callback.message.reply_to_message:
        await callback.message.reply_to_message.delete()

    # Путь к фото создателя
    photo_path = "image/creator.jpg"

    # Кнопка "Назад"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="about")]
    ])

    # Отправляем фото с подписью
    await bot.send_photo(callback.message.chat.id, types.FSInputFile(photo_path), caption="👤 *Создатель этого магазина!*", parse_mode="Markdown")
    await callback.message.answer("⬅ Вернуться в меню 'О магазине'", reply_markup=keyboard)
    await callback.answer()

    await callback.message.edit_text(photo_path, reply_markup=keyboard, parse_mode="Markdown")
    await callback.message.delete()
    await callback.answer()

# факты о котах
@dp.callback_query(lambda c: c.data == "cat_fact")
async def send_cat_fact(callback: types.CallbackQuery):
    fact = random.choice(cat_facts)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Новый факт", callback_data="cat_fact")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
    ])
    await callback.message.edit_text(f"Вот факт о котах:\n\n{fact}", reply_markup=keyboard)
    await callback.answer()

# Состояния для настройки языка
class SettingsState(StatesGroup):
    waiting_for_language = State()

# Обработка кнопки "Настройки"
@dp.callback_query(lambda c: c.data == "settings")
async def settings_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="language_ru")],
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="language_en")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    
    await callback.message.edit_text("Выберите язык:", reply_markup=keyboard)
    await callback.answer()

# Обработка выбора русского языка
@dp.callback_query(lambda c: c.data == "language_ru")
async def set_language_ru(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(language="ru")  # Сохраняем выбор языка
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купить кота 🐱", callback_data="buy_menu")],
            [InlineKeyboardButton(text="Корзина 🛒", callback_data="view_cart")],
            [InlineKeyboardButton(text="Поддержка 🛠", callback_data="support")],
            [InlineKeyboardButton(text="Отзывы ⭐", callback_data="reviews_0")],
            [InlineKeyboardButton(text="Настройки ⚙️", callback_data="settings")],
            [InlineKeyboardButton(text="Факт о котах 📚", callback_data="cat_fact")],
            [InlineKeyboardButton(text="О магазине 🏪", callback_data="about")],
            [InlineKeyboardButton(text="Играть 🎮", callback_data="play_game")],
            [InlineKeyboardButton(text="Рефералы 👥", callback_data="referral_info")]
    ])
    
    await callback.message.edit_text("Язык изменен на Русский 🇷🇺", reply_markup=keyboard)
    await callback.answer()

# Обработка выбора английского языка
@dp.callback_query(lambda c: c.data == "language_en")
async def set_language_en(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(language="en")  # Сохраняем выбор языка
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Buy a cat 🐱", callback_data="buy_menu")],
            [InlineKeyboardButton(text="Basket 🛒", callback_data="view_cart")],
            [InlineKeyboardButton(text="Support 🛠", callback_data="support")],
            [InlineKeyboardButton(text="Reviews ⭐", callback_data="reviews_0")],
            [InlineKeyboardButton(text="Settings ⚙️", callback_data="settings")],
            [InlineKeyboardButton(text="Cat Fact 📚", callback_data="cat_fact")],
            [InlineKeyboardButton(text="About the store 🏪", callback_data="about")],
            [InlineKeyboardButton(text="Play 🎮", callback_data="play_game")],
            [InlineKeyboardButton(text="Refs 👥", callback_data="referral_info")] 
    ])
    
    await callback.message.edit_text("Language changed to English 🇬🇧", reply_markup=keyboard)
    await callback.answer()

user_languages = {}  # Словарь для хранения языков пользователей (user_id: language)

# Функция отправки главного меню с учетом языка
user_languages = {}  # Словарь (user_id: language)

async def send_main_menu(message: types.Message):
    user_id = message.from_user.id
    language = user_languages.get(user_id, "ru")

    if language == "ru":
        text = "Привет! Выберите действие:"
        buttons = [
            [InlineKeyboardButton(text="Купить кота 🐱", callback_data="buy_menu")],
            [InlineKeyboardButton(text="Корзина 🛒", callback_data="view_cart")],
            [InlineKeyboardButton(text="Поддержка 🛠", callback_data="support")],
            [InlineKeyboardButton(text="Отзывы ⭐", callback_data="reviews_0")],
            [InlineKeyboardButton(text="Настройки ⚙️", callback_data="settings")],
            [InlineKeyboardButton(text="Факт о котах 📚", callback_data="cat_fact")],
            [InlineKeyboardButton(text="О магазине 🏪", callback_data="about")],
            [InlineKeyboardButton(text="Играть 🎮", callback_data="play_game")],
            [InlineKeyboardButton(text="Рефералы 👥", callback_data="referral_info")]
        ]
    else:
        text = "Hello! Choose an action:"
        buttons = [
            [InlineKeyboardButton(text="Buy a cat 🐱", callback_data="buy_menu")],
            [InlineKeyboardButton(text="Basket 🛒", callback_data="view_cart")],
            [InlineKeyboardButton(text="Support 🛠", callback_data="support")],
            [InlineKeyboardButton(text="Reviews ⭐", callback_data="reviews_0")],
            [InlineKeyboardButton(text="Settings ⚙️", callback_data="settings")],
            [InlineKeyboardButton(text="Cat Fact 📚", callback_data="cat_fact")],
            [InlineKeyboardButton(text="About the store 🏪", callback_data="about")],
            [InlineKeyboardButton(text="Play 🎮", callback_data="play_game")],
            [InlineKeyboardButton(text="Refs 👥", callback_data="referral_info")] 
        ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard)

# Игрулька
@dp.callback_query(lambda c: c.data == "play_game")
async def start_game(callback: types.CallbackQuery):
    cat_id = random.choice(list(cats.keys()))
    photo_path = cats[cat_id]["photo"]
    photo = FSInputFile(photo_path)
    options_ids = [cat_id]
    options_ids += random.sample([cid for cid in cats if cid != cat_id], 2)
    random.shuffle(options_ids)
    buttons = []
    for cid in options_ids:
        buttons.append(InlineKeyboardButton(text=cats[cid]["name"], callback_data=f"guess_{cid}_{cat_id}"))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [buttons[0], buttons[1]],
        [buttons[2]],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    await callback.message.delete()
    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=photo,
        caption="Угадай породу этого кота!",
        reply_markup=keyboard
    )
    await callback.answer()
    await callback.message.delete()

# Обработчик игры
@dp.callback_query(lambda c: c.data.startswith("guess_"))
async def handle_guess(callback: types.CallbackQuery):
    data_parts = callback.data.split('_')
    guessed_id = data_parts[1]
    correct_id = data_parts[2]

    if guessed_id == correct_id:
        await callback.answer("✅ Правильно! Ты настоящий знаток котов!", show_alert=True)
    else:
        await callback.answer(f"❌ Неверно! Это {cats[correct_id]['name']}", show_alert=True)

    await asyncio.sleep(1)
    await callback.message.delete()
    
    await callback.message.answer(
        "Игра завершена!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ])
    )
    await callback.answer()

# Реферальная система
@dp.callback_query(lambda c: c.data == "referral_info")
async def referral_info(callback: types.CallbackQuery):
    ref_count = get_referrals_count(callback.from_user.id)
    ref_link = f"https://t.me/{(await bot.get_me()).username}?start=ref_{callback.from_user.id}"

    msg = await callback.message.answer(
        f"👥 Реферальная программа:\n"
        f"• Приглашено друзей: {ref_count}\n"
        f"• Ваша ссылка: {ref_link}\n\n"
        f"За каждого приглашённого друга вы получаете бонусы!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ])
    )
    await callback.message.delete()


# Функция для запуска бота
async def main():
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
