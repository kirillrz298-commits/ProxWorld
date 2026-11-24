from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import config
from database import register_or_update_user, is_operator_or_admin
from keyboards import get_main_reply_keyboard, get_server_info_inline

router = Router(name="common_router")

WELCOME_TEXT = f"""
👋 **Добро пожаловать в службу поддержки {config.SERVER_NAME}!**

Я ваш персональный ассистент по всем вопросам сервера.
Здесь вы можете:
• Быстро решить проблемы со входом и паролями 🔑
• Разобраться с донатом и покупками 💎
• Узнать правила и подать апелляцию на блокировку 🔨
• Получить мгновенный ответ от умного ИИ-помощника 🤖
• Создать прямое обращение к живым операторам 👨‍💻

🎮 **Информация о сервере:**
• **IP адрес:** `{config.SERVER_IP}` (Порт: `{config.SERVER_PORT}`)
• **Версии:** {config.SERVER_VERSIONS}
• **Сайт / Донат:** {config.SERVER_SITE}

*Выберите нужный раздел в меню ниже:* 👇
"""

HELP_TEXT = f"""
📖 **Справка по командам бота {config.SERVER_NAME}:**

**Для всех игроков:**
/start — Главное меню и перезапуск бота
/help — Справка и команды
/ticket — Создать обращение к операторам
/close — Закрыть ваше текущее обращение
/faq — Часто задаваемые вопросы

**Для операторов и администрации:**
/admin — Вход в панель управления тикетами
/reply `<id> <текст>` — Быстрый ответ на тикет игрока
/close `<id>` — Закрыть тикет по номеру
/stats — Просмотр статистики обращений

Нужна помощь живого человека? Нажмите кнопку **«👨‍💻 Связь с оператором»**!
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
        f"🏰 **Minecraft сервер {config.SERVER_NAME}**\n\n"
        f"🔥 **Гриферское выживание с уникальными механиками!**\n\n"
        f"• **Айпи для входа:** `{config.SERVER_IP}`\n"
        f"• **Порт:** `{config.SERVER_PORT}`\n"
        f"• **Версии:** `{config.SERVER_VERSIONS}`\n"
        f"• **Официальный сайт:** {config.SERVER_SITE}\n"
        f"• **Авто-донат:** {config.SERVER_DONATE_URL}\n\n"
        f"⚡ Присоединяйтесь к нашему дружному сообществу игроков!"
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

