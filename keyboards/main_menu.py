from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import config

def get_main_reply_keyboard(is_operator: bool = False) -> ReplyKeyboardMarkup:
    """Главная клавиатура бота."""
    keyboard = [
        [
            KeyboardButton(text="🔑 Проблемы со входом"),
            KeyboardButton(text="💎 Донат и покупки")
        ],
        [
            KeyboardButton(text="🔨 Блокировки и наказания"),
            KeyboardButton(text="❓ Частые вопросы")
        ],
        [
            KeyboardButton(text="👨‍💻 Связь с оператором"),
            KeyboardButton(text="🤖 Задать вопрос ИИ")
        ],
        [
            KeyboardButton(text="🎫 Мой тикет"),
            KeyboardButton(text="🌐 О сервере")
        ]
    ]
    if is_operator:
        keyboard.append([KeyboardButton(text="⚡ Админ-панель")])
        
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_login_issues_inline() -> InlineKeyboardMarkup:
    """Клавиатура для проблем со входом."""
    buttons = [
        [InlineKeyboardButton(text="🔐 Забыл пароль / Сброс", callback_data="issue_password")],
        [InlineKeyboardButton(text="🚫 Неверная сессия / Ошибка клиента", callback_data="issue_session")],
        [InlineKeyboardButton(text="📡 Сервер не пингуется / Не виден", callback_data="issue_ping")],
        [InlineKeyboardButton(text="👨‍💻 Создать тикет оператору", callback_data="create_ticket_login")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_donate_issues_inline() -> InlineKeyboardMarkup:
    """Клавиатура для вопросов по донату."""
    buttons = [
        [InlineKeyboardButton(text="🛒 Написать по поводу доната (@DesTrooyda)", url="https://t.me/DesTrooyda")],
        [InlineKeyboardButton(text="⏳ Донат не пришел вовремя", callback_data="donate_delayed")],
        [InlineKeyboardButton(text="🔄 Перенос привилегии", callback_data="donate_transfer")],
        [InlineKeyboardButton(text="👨‍💻 Связаться с оператором", callback_data="create_ticket_donate")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_punishment_issues_inline() -> InlineKeyboardMarkup:
    """Клавиатура для блокировок и наказаний."""
    buttons = [
        [InlineKeyboardButton(text="🛡️ Бан античитом / Консолью", callback_data="ban_anticheat")],
        [InlineKeyboardButton(text="👮 Бан модератором", callback_data="ban_moderator")],
        [InlineKeyboardButton(text="📜 Правила сервера", url=config.SERVER_RULES_URL)],
        [InlineKeyboardButton(text="⚖️ Подать апелляцию (Тикет)", callback_data="create_ticket_ban")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_faq_inline() -> InlineKeyboardMarkup:
    """Клавиатура для раздела FAQ."""
    buttons = [
        [InlineKeyboardButton(text="🎮 Как начать играть?", callback_data="faq_start")],
        [InlineKeyboardButton(text="⚔️ Правила грифа и приватов", callback_data="faq_rules")],
        [InlineKeyboardButton(text="⌨️ Полезные команды сервера", callback_data="faq_commands")],
        [InlineKeyboardButton(text="🤖 Спросить у ИИ-помощника", callback_data="start_ai_dialog")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_server_info_inline() -> InlineKeyboardMarkup:
    """Ссылки на ресурсы сервера."""
    buttons = [
        [InlineKeyboardButton(text="💎 Донат / Покупки (@DesTrooyda)", url="https://t.me/DesTrooyda")],
        [InlineKeyboardButton(text="👨‍💻 Связь с оператором", callback_data="start_ticket_creation")],
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ai_dialog_inline() -> InlineKeyboardMarkup:
    """Кнопки в режиме диалога с ИИ."""
    buttons = [
        [InlineKeyboardButton(text="👨‍💻 Связаться с оператором", callback_data="start_ticket_creation")],
        [InlineKeyboardButton(text="❌ Завершить диалог с ИИ", callback_data="exit_ai_dialog")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

