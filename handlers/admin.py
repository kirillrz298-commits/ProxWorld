import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import config
from database import (
    is_operator_or_admin,
    get_tickets,
    get_ticket,
    get_stats,
    get_operators,
    set_user_role,
    get_user,
    register_or_update_user
)
from keyboards import (
    get_admin_panel_keyboard,
    get_tickets_pagination_keyboard,
    get_operators_menu_keyboard,
    get_cancel_admin_action_inline,
    get_operator_ticket_controls
)
from states import AdminStates

logger = logging.getLogger(__name__)
router = Router(name="admin_router")

PAGE_LIMIT = 5

# ==========================================
# ВХОД В АДМИН-ПАНЕЛЬ
# ==========================================

@router.message(Command("admin"))
@router.message(F.text == "⚡ Админ-панель")
async def open_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    is_op = await is_operator_or_admin(message.from_user.id, config.ADMIN_IDS)
    if not is_op:
        await message.answer("⛔ У вас нет доступа к панели администратора.")
        return

    text = (
        f"⚡ **Панель управления поддержкой {config.SERVER_NAME}**\n\n"
        f"👤 Оператор: **{message.from_user.full_name}**\n"
        f"🔑 Статус: {'Главный администратор' if message.from_user.id in config.ADMIN_IDS else 'Оператор'}\n\n"
        f"Выберите нужное действие ниже:"
    )
    await message.answer(text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")


@router.callback_query(F.data == "admin_main")
async def cb_admin_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    is_op = await is_operator_or_admin(callback.from_user.id, config.ADMIN_IDS)
    if not is_op:
        await callback.answer("⛔ Нет доступа!", show_alert=True)
        return

    text = (
        f"⚡ **Панель управления поддержкой {config.SERVER_NAME}**\n\n"
        f"Выберите раздел:"
    )
    await callback.message.edit_text(text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")
    await callback.answer()


# ==========================================
# СТАТИСТИКА
# ==========================================

@router.message(Command("stats"))
@router.callback_query(F.data == "admin_stats")
async def show_statistics(event: Message | CallbackQuery):
    user_id = event.from_user.id
    is_op = await is_operator_or_admin(user_id, config.ADMIN_IDS)
    if not is_op:
        if isinstance(event, Message):
            await event.answer("⛔ Нет доступа.")
        else:
            await event.answer("⛔ Нет доступа!", show_alert=True)
        return

    stats = await get_stats()
    text = (
        f"📊 **Статистика службы поддержки {config.SERVER_NAME}**\n\n"
        f"• 👥 **Всего игроков в боте:** `{stats['total_users']}`\n"
        f"• 👨‍💼 **Активных операторов:** `{stats['total_operators']}`\n"
        f"────────────────────\n"
        f"• 🎫 **Всего обращений:** `{stats['total_tickets']}`\n"
        f"• 🟢 **Открытых (ждут ответа):** `{stats['open_tickets']}`\n"
        f"• 🟡 **В работе у операторов:** `{stats['in_progress_tickets']}`\n"
        f"• 🔴 **Закрытых тикетов:** `{stats['closed_tickets']}`\n"
        f"• 📅 **Создано за сегодня:** `{stats['tickets_today']}`"
    )
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=get_admin_panel_keyboard(), parse_mode="Markdown")


# ==========================================
# ПРОСМОТР ТИКЕТОВ ПО КАТЕГОРИЯМ
# ==========================================

@router.callback_query(F.data.in_(["admin_tickets_open", "admin_tickets_progress", "admin_tickets_all"]))
async def cb_view_tickets_list(callback: CallbackQuery):
    status_map = {
        "admin_tickets_open": "open",
        "admin_tickets_progress": "in_progress",
        "admin_tickets_all": None
    }
    status = status_map[callback.data]
    status_title = "Открытые" if status == "open" else ("В работе" if status == "in_progress" else "Все")

    tickets = await get_tickets(status=status, limit=PAGE_LIMIT, offset=0)
    if not tickets:
        await callback.message.edit_text(
            f"ℹ️ Тикетов в категории «{status_title}» не найдено.",
            reply_markup=get_admin_panel_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    text = f"📋 **Список тикетов («{status_title}»):**\nНажмите на тикет для деталей и ответа:"
    markup = get_tickets_pagination_keyboard(tickets, status=status or "all", page=0, limit=PAGE_LIMIT)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_page_"))
async def cb_paginate_tickets(callback: CallbackQuery):
    parts = callback.data.split("_")
    raw_status = parts[2]
    page = int(parts[3])
    status = None if raw_status == "all" else raw_status

    offset = page * PAGE_LIMIT
    tickets = await get_tickets(status=status, limit=PAGE_LIMIT, offset=offset)

    if not tickets and page > 0:
        await callback.answer("Больше тикетов нет.")
        return

    status_title = "Открытые" if status == "open" else ("В работе" if status == "in_progress" else "Все")
    text = f"📋 **Список тикетов («{status_title}», стр. {page + 1}):**"
    markup = get_tickets_pagination_keyboard(tickets, status=raw_status, page=page, limit=PAGE_LIMIT)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("admin_view_ticket_"))
async def cb_admin_view_single_ticket(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[3])
    ticket = await get_ticket(ticket_id)
    if not ticket:
        await callback.answer("Тикет не найден.", show_alert=True)
        return

    status_str = "🟢 Открыт" if ticket["status"] == "open" else ("🟡 В работе" if ticket["status"] == "in_progress" else "🔴 Закрыт")
    op_assigned = f"`{ticket['operator_id']}`" if ticket.get("operator_id") else "Не назначен"
    closed_info = f"\n🔒 **Закрыт:** {ticket['closed_at']}" if ticket.get("closed_at") else ""

    details_text = (
        f"🎫 **Информация о тикете #{ticket['id']}**\n\n"
        f"📊 **Статус:** {status_str}\n"
        f"📌 **Тема:** {ticket['topic']}\n"
        f"🎮 **Ник игрока:** `{ticket['player_nick']}`\n"
        f"🆔 **ID игрока:** `{ticket['user_id']}`\n"
        f"👨‍💼 **Оператор:** {op_assigned}\n"
        f"📅 **Создан:** {ticket['created_at']}"
        f"{closed_info}"
    )

    markup = get_operator_ticket_controls(ticket_id, status=ticket["status"])
    await callback.message.edit_text(details_text, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()


# ==========================================
# УПРАВЛЕНИЕ ОПЕРАТОРАМИ
# ==========================================

@router.callback_query(F.data == "admin_operators")
async def cb_manage_operators(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in config.ADMIN_IDS:
        await callback.answer("⛔ Управлять составом операторов могут только Главные Администраторы!", show_alert=True)
        return

    operators = await get_operators()
    text = "👥 **Список текущих операторов и администраторов:**\n\n"
    if not operators:
        text += "Операторы в базе данных пока отсутствуют.\n"
    else:
        for idx, op in enumerate(operators, start=1):
            role_icon = "👑 Главный Админ" if op["user_id"] in config.ADMIN_IDS else ("⭐️ Админ" if op["role"] == "admin" else "👨‍💼 Оператор")
            uname = f"@{op['username']}" if op.get("username") else "без username"
            text += f"{idx}. **{op['full_name']}** ({uname})\n   • ID: `{op['user_id']}` | Роль: {role_icon}\n"

    await callback.message.edit_text(text, reply_markup=get_operators_menu_keyboard(operators), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "admin_add_operator")
async def cb_add_operator_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("⛔ Только Главный Администратор может добавлять операторов!", show_alert=True)
        return

    await state.set_state(AdminStates.adding_operator)
    text = (
        "➕ **Добавление оператора**\n\n"
        "Отправьте числовой **Telegram ID** пользователя, которого хотите назначить оператором.\n"
        "*(Пользователь может узнать свой ID через @userinfobot)*"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_admin_action_inline(), parse_mode="Markdown")
    await callback.answer()


@router.message(AdminStates.adding_operator)
async def process_add_operator(message: Message, state: FSMContext):
    target_id_str = message.text.strip()
    if not target_id_str.isdigit():
        await message.answer("⚠️ Telegram ID должен состоять только из цифр. Попробуйте еще раз или нажмите отмену:")
        return

    target_id = int(target_id_str)
    await state.clear()

    # Проверяем пользователя в БД или регистрируем
    user = await get_user(target_id)
    if not user:
        await register_or_update_user(target_id, None, "Оператор", role="operator")
    else:
        await set_user_role(target_id, role="operator")

    await message.answer(
        f"✅ Пользователь с ID `{target_id}` успешно назначен оператором поддержки!",
        reply_markup=get_admin_panel_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "admin_remove_operator")
async def cb_remove_operator_start(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in config.ADMIN_IDS:
        await callback.answer("⛔ Только Главный Администратор может снимать операторов!", show_alert=True)
        return

    await state.set_state(AdminStates.removing_operator)
    text = (
        "➖ **Снятие прав оператора**\n\n"
        "Отправьте числовой **Telegram ID** оператора, которого хотите разжаловать до обычного игрока:"
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_admin_action_inline(), parse_mode="Markdown")
    await callback.answer()


@router.message(AdminStates.removing_operator)
async def process_remove_operator(message: Message, state: FSMContext):
    target_id_str = message.text.strip()
    if not target_id_str.isdigit():
        await message.answer("⚠️ ID должен быть числом. Попробуйте еще раз:")
        return

    target_id = int(target_id_str)
    if target_id in config.ADMIN_IDS:
        await message.answer("⛔ Нельзя снять права с Главного Администратора из config!")
        return

    await state.clear()
    success = await set_user_role(target_id, role="user")
    if success:
        await message.answer(
            f"✅ Пользователь `{target_id}` разжалован до обычного пользователя.",
            reply_markup=get_admin_panel_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"⚠️ Оператор с ID `{target_id}` не найден в базе данных.",
            reply_markup=get_admin_panel_keyboard(),
            parse_mode="Markdown"
        )
