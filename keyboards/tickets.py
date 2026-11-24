from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_ticket_topics_keyboard() -> InlineKeyboardMarkup:
    """Выбор темы обращения при создании тикета."""
    buttons = [
        [InlineKeyboardButton(text="🔑 Проблемы со входом", callback_data="topic_login")],
        [InlineKeyboardButton(text="💎 Донат и покупки", callback_data="topic_donate")],
        [InlineKeyboardButton(text="🔨 Блокировки и наказания", callback_data="topic_punishment")],
        [InlineKeyboardButton(text="🐛 Баги и технические проблемы", callback_data="topic_bugs")],
        [InlineKeyboardButton(text="❓ Другой вопрос", callback_data="topic_other")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_ticket_creation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_reply_keyboard() -> ReplyKeyboardMarkup:
    """Кнопка быстрой отмены действия."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_player_ticket_controls(ticket_id: int) -> InlineKeyboardMarkup:
    """Управление тикетом для игрока."""
    buttons = [
        [InlineKeyboardButton(text="❌ Закрыть это обращение", callback_data=f"user_close_ticket_{ticket_id}")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_operator_ticket_controls(ticket_id: int, status: str = "open") -> InlineKeyboardMarkup:
    """Кнопки управления тикетом для оператора/админа."""
    buttons = [
        [
            InlineKeyboardButton(text="✍️ Ответить", callback_data=f"op_reply_{ticket_id}"),
            InlineKeyboardButton(text="🙋 Взять в работу", callback_data=f"op_take_{ticket_id}")
        ],
        [
            InlineKeyboardButton(text="📜 История сообщений", callback_data=f"op_history_{ticket_id}"),
            InlineKeyboardButton(text="❌ Закрыть тикет", callback_data=f"op_close_{ticket_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_operator_reply_cancel_inline(ticket_id: int) -> InlineKeyboardMarkup:
    """Отмена режима ввода ответа оператором."""
    buttons = [
        [InlineKeyboardButton(text="❌ Отменить ответ", callback_data=f"op_cancel_reply_{ticket_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

