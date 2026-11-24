from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import config
from database import register_or_update_user, is_operator_or_admin
from keyboards import get_main_reply_keyboard, get_server_info_inline

router = Router(name="common_router")

WELCOME_TEXT = f"""
╭━━━━━━━━━━━━━━━━━━━━╮
│   ⚡️ **PROXWORLD SUPPORT**   │
╰━━━━━━━━━━━━━━━━━━━━╯

👋 **Добро пожаловать в службу поддержки ProxWorld!**

Я ваш персональный ассистент по всем вопросам сервера.
Здесь вы можете:
• Быстро решить проблемы со входом и паролями 🔑
• Разобраться с донатом и покупками 💎
• Узнать правила и подать апелляцию на блокировку 🔨
• Получить мгновенный ответ от умного ИИ-помощника 🤖
• Создать прямое обращение к живым операторам 👨‍💻

╭ 🎮 **Информация о сервере:**
┊ • **IP адрес:** `{config.SERVER_IP}` *(в разработке)*
┊ • **Версии:** {config.SERVER_VERSIONS}
╰ • **Сайт / Донат:** {config.SERVER_SITE}

👇 *Выберите нужный раздел в меню ниже:*
"""

HELP_TEXT = f"""
╭━━━━━━━━━━━━━━━━━━━━╮
│    📖 **СПРАВКА И КОМАНДЫ**   │
╰━━━━━━━━━━━━━━━━━━━━╯

🎮 **Команды для игроков:**
▸ `/start` — Главное меню и перезапуск бота
▸ `/ticket` — Создать обращение к операторам
▸ `/close` — Закрыть текущее обращение
▸ `/help` — Справка по командам бота

⚡️ **Команды для персонала:**
▸ `/admin` — Панель управления тикетами
▸ `/stats` — Просмотр статистики обращений
▸ `/reply <id> <текст>` — Быстрый ответ на тикет игрока

💬 *Нужна помощь живого человека? Нажмите кнопку* **«👨‍💻 Связь с оператором»**!
"""

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    is_op = await is_operator_or_admin(user.id, config.ADMIN_IDS)
    
    # Регистрация пользователя в БД
    role = "admin" if user.id in config.ADMIN_IDS else ("operator" if is_op else "user")
    await register_or_update_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name or "Пользователь",
        role=role
    )
    
    await message.answer(
        WELCOME_TEXT,
        reply_markup=get_main_reply_keyboard(is_operator=is_op),
        parse_mode="Markdown"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="Markdown")


@router.message(F.text == "🌐 О сервере")
async def show_server_info(message: Message):
    text = (
        f"╭━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│   🏰 **О СЕРВЕРЕ PROXWORLD**  │\n"
        f"╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"🔥 **Гриферское выживание нового поколения!**\n\n"
        f"╭ 📌 **Информация о подключении:**\n"
        f"┊ ✦ **IP адрес:** `{config.SERVER_IP}` *(в разработке)*\n"
        f"┊ ✦ **Версии:** {config.SERVER_VERSIONS}\n"
        f"╰ ✦ **Сайт / Донат:** {config.SERVER_SITE}\n\n"
        f"⚡ *Нажмите на IP, чтобы скопировать его в буфер обмена!*"
    )
    await message.answer(text, reply_markup=get_server_info_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    is_op = await is_operator_or_admin(callback.from_user.id, config.ADMIN_IDS)
    await callback.message.edit_text(
        "Вы вернулись в главное меню. Выберите интересующий вас раздел:",
        parse_mode="Markdown"
    )
    await callback.message.answer(
        "👇 Меню управления доступно на клавиатуре ниже:",
        reply_markup=get_main_reply_keyboard(is_operator=is_op)
    )
    await callback.answer()

