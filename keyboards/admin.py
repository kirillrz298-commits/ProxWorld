from typing import List, Dict, Any
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Главная панель администратора."""
    buttons = [
        [
            InlineKeyboardButton(text="📋 Открытые тикеты", callback_data="admin_tickets_open"),
            InlineKeyboardButton(text="⏳ В процессе", callback_data="admin_tickets_progress")
        ],
        [
            InlineKeyboardButton(text="📁 Все тикеты", callback_data="admin_tickets_all"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="👥 Управление операторами", callback_data="admin_operators")
        ],
        [
            InlineKeyboardButton(text="🔙 Закрыть админ-панель", callback_data="back_to_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tickets_pagination_keyboard(
    tickets: List[Dict[str, Any]], 
    status: str, 
    page: int = 0, 
    limit: int = 5
) -> InlineKeyboardMarkup:
    """Список тикетов с постраничной навигацией."""
    buttons = []
    
    # Кнопки для каждого тикета
    for t in tickets:
        status_icon = "🟢" if t["status"] == "open" else ("🟡" if t["status"] == "in_progress" else "🔴")
        nick = t.get("player_nick") or "Без ника"
        btn_text = f"{status_icon} #{t['id']} | {nick} | {t['topic'][:15]}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"admin_view_ticket_{t['id']}")])
        
    # Навигационные кнопки
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_page_{status}_{page - 1}"))
    
    # Если количество полученных элементов равно лимиту, возможно есть следующая страница
    if len(tickets) == limit:
        nav_row.append(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"admin_page_{status}_{page + 1}"))
        
    if nav_row:
        buttons.append(nav_row)
        
    buttons.append([InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_operators_menu_keyboard(operators: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
    """Клавиатура управления операторами."""
    buttons = [
        [InlineKeyboardButton(text="➕ Добавить оператора (по ID)", callback_data="admin_add_operator")],
        [InlineKeyboardButton(text="➖ Удалить оператора", callback_data="admin_remove_operator")],
        [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_admin_action_inline() -> InlineKeyboardMarkup:
    """Отмена текущего действия в админке."""
    buttons = [
        [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

