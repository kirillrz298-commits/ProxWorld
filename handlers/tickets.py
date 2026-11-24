import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import config
from database import (
    create_ticket,
    get_active_ticket_by_user,
    get_ticket,
    close_ticket,
    assign_ticket_operator,
    add_ticket_message,
    get_ticket_messages,
    is_operator_or_admin,
    get_operators
)
from states import TicketCreation, TicketChat, OperatorReply
from keyboards import (
    get_ticket_topics_keyboard,
    get_cancel_reply_keyboard,
    get_player_ticket_controls,
    get_operator_ticket_controls,
    get_operator_reply_cancel_inline,
    get_main_reply_keyboard
)

logger = logging.getLogger(__name__)
router = Router(name="tickets_router")

TOPIC_MAP = {
    "topic_login": "🔑 Проблемы со входом",
    "create_ticket_login": "🔑 Проблемы со входом",
    "topic_donate": "💎 Донат и покупки",
    "create_ticket_donate": "💎 Донат и покупки",
    "topic_punishment": "🔨 Блокировки и наказания",
    "create_ticket_ban": "🔨 Блокировки и наказания",
    "topic_bugs": "🐛 Баги и тех. проблемы",
    "topic_other": "❓ Другой вопрос"
}


async def notify_operators_about_new_ticket(bot, ticket_id: int, user, nick: str, topic: str, text: str):
    """Рассылка уведомления операторам о новом тикете."""
    username_str = f"@{user.username}" if user.username else "нет username"
    notification_text = (
        f"╭─ 🔔 **НОВОЕ ОБРАЩЕНИЕ #{ticket_id}** ──────\n"
        f"│ 👤 **Игрок:** `{nick}`\n"
        f"│ 🆔 **Telegram ID:** `{user.id}` ({username_str})\n"
        f"│ 📌 **Тема:** {topic}\n"
        f"╰──────────────────────────────────\n\n"
        f"📝 **Суть проблемы:**\n{text}"
    )
    
    markup = get_operator_ticket_controls(ticket_id)
    
    # 1. Если настроен чат поддержки
    if config.SUPPORT_CHAT_ID != 0:
        try:
            await bot.send_message(config.SUPPORT_CHAT_ID, notification_text, reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Не удалось отправить тикет в SUPPORT_CHAT_ID: {e}")

    # 2. Уведомление администраторам и зарегистрированным операторам в ЛС
    operators = await get_operators()
    operator_ids = {op["user_id"] for op in operators}.union(set(config.ADMIN_IDS))
    
    for op_id in operator_ids:
        if op_id != user.id:
            try:
                await bot.send_message(op_id, notification_text, reply_markup=markup, parse_mode="Markdown")
            except Exception as e:
                logger.debug(f"Не удалось доставить уведомление оператору {op_id}: {e}")


# ==========================================
# СОЗДАНИЕ ТИКЕТА
# ==========================================

@router.message(F.text == "👨‍💻 Связь с оператором")
@router.message(Command("ticket"))
@router.callback_query(F.data.in_(["start_ticket_creation", "create_ticket_login", "create_ticket_donate", "create_ticket_ban"]))
async def init_ticket_creation(event: Message | CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    active_ticket = await get_active_ticket_by_user(user_id)
    
    # Если у игрока уже есть открытое обращение
    if active_ticket:
        text = (
            f"ℹ️ **У вас уже открыто обращение #{active_ticket['id']}!**\n\n"
            f"📌 **Тема:** {active_ticket['topic']}\n"
            f"📊 **Статус:** {active_ticket['status']}\n\n"
            f"Вы можете просто писать сообщения сюда — они сразу передаются оператору.\n"
            f"Если проблема решена, закройте тикет кнопкой ниже:"
        )
        markup = get_player_ticket_controls(active_ticket["id"])
        if isinstance(event, CallbackQuery):
            await event.message.answer(text, reply_markup=markup, parse_mode="Markdown")
            await event.answer()
        else:
            await event.answer(text, reply_markup=markup, parse_mode="Markdown")
        await state.set_state(TicketChat.active_chat)
        return

    # Если была нажата кнопка с конкретной категорией
    if isinstance(event, CallbackQuery) and event.data in TOPIC_MAP:
        selected_topic = TOPIC_MAP[event.data]
        await state.update_data(topic=selected_topic)
        await state.set_state(TicketCreation.entering_nick)
        await event.message.answer(
            f"📝 **Выбрана тема:** {selected_topic}\n\n"
            f"🎮 **Шаг 1 из 2:** Введите ваш точный игровой ник на сервере {config.SERVER_NAME}:",
            reply_markup=get_cancel_reply_keyboard(),
            parse_mode="Markdown"
        )
        await event.answer()
        return

    # Обычный выбор темы
    await state.set_state(TicketCreation.choosing_topic)
    msg_text = "📋 **Создание обращения в техподдержку**\n\nПожалуйста, выберите тему вашего вопроса:"
    markup = get_ticket_topics_keyboard()
    
    if isinstance(event, CallbackQuery):
        await event.message.answer(msg_text, reply_markup=markup, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(msg_text, reply_markup=markup, parse_mode="Markdown")


@router.callback_query(TicketCreation.choosing_topic, F.data.startswith("topic_"))
async def process_topic_choice(callback: CallbackQuery, state: FSMContext):
    topic = TOPIC_MAP.get(callback.data, "Общий вопрос")
    await state.update_data(topic=topic)
    await state.set_state(TicketCreation.entering_nick)
    
    await callback.message.answer(
        f"📝 **Выбрана тема:** {topic}\n\n"
        f"🎮 **Шаг 1 из 2:** Введите ваш игровой никнейм на сервере {config.SERVER_NAME}:",
        reply_markup=get_cancel_reply_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_ticket_creation")
@router.message(TicketCreation.entering_nick, F.text == "❌ Отмена")
@router.message(TicketCreation.entering_description, F.text == "❌ Отмена")
async def cancel_creation(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    is_op = await is_operator_or_admin(event.from_user.id, config.ADMIN_IDS)
    cancel_text = "❌ Создание обращения отменено."
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(cancel_text)
        await event.message.answer("Главное меню:", reply_markup=get_main_reply_keyboard(is_op))
        await event.answer()
    else:
        await event.answer(cancel_text, reply_markup=get_main_reply_keyboard(is_op))


@router.message(TicketCreation.entering_nick)
async def process_nick(message: Message, state: FSMContext):
    nick = message.text.strip()
    if len(nick) < 2 or len(nick) > 32:
        await message.answer("⚠️ Никнейм должен быть от 2 до 32 символов. Попробуйте еще раз:")
        return

    await state.update_data(player_nick=nick)
    await state.set_state(TicketCreation.entering_description)
    
    await message.answer(
        f"✅ Никнейм: `{nick}`\n\n"
        f"✍️ **Шаг 2 из 2:** Подробно опишите вашу проблему.\n"
        f"Укажите детали (дата/время, сервер, что произошло, чеки/ссылки на скриншоты):",
        reply_markup=get_cancel_reply_keyboard(),
        parse_mode="Markdown"
    )


@router.message(TicketCreation.entering_description)
async def process_description(message: Message, state: FSMContext):
    description = message.text
    if not description or len(description.strip()) < 5:
        await message.answer("⚠️ Пожалуйста, опишите проблему подробнее (минимум 5 символов):")
        return

    data = await state.get_data()
    topic = data.get("topic", "Общий вопрос")
    player_nick = data.get("player_nick", "Не указан")
    
    # Создаем тикет в БД
    ticket_id = await create_ticket(
        user_id=message.from_user.id,
        player_nick=player_nick,
        topic=topic,
        initial_text=description
    )
    
    await state.clear()
    await state.set_state(TicketChat.active_chat)
    
    # Уведомляем игрока
    is_op = await is_operator_or_admin(message.from_user.id, config.ADMIN_IDS)
    success_text = (
        f"╭─ 🎉 **Обращение #{ticket_id} создано!** ─────\n"
        f"│ 📌 **Тема:** {topic}\n"
        f"│ 🎮 **Никнейм:** `{player_nick}`\n"
        f"╰──────────────────────────────────\n\n"
        f"⏳ Мы уведомили дежурных операторов — вам ответят в ближайшее время!\n\n"
        f"💬 *Все ваши сообщения в этом чате автоматически передаются в обращение.*"
    )
    
    await message.answer(success_text, reply_markup=get_main_reply_keyboard(is_op), parse_mode="Markdown")
    await message.answer(
        "Вы можете отправить дополнительную информацию или закрыть тикет при решении:",
        reply_markup=get_player_ticket_controls(ticket_id)
    )
    
    # Оповещаем операторов
    await notify_operators_about_new_ticket(
        bot=message.bot,
        ticket_id=ticket_id,
        user=message.from_user,
        nick=player_nick,
        topic=topic,
        text=description
    )


# ==========================================
# ПРОСМОТР ТЕКУЩЕГО ТИКЕТА ИГРОКОМ
# ==========================================

@router.message(F.text == "🎫 Мой тикет")
async def show_my_ticket(message: Message):
    active_ticket = await get_active_ticket_by_user(message.from_user.id)
    if not active_ticket:
        await message.answer(
            "У вас нет активных обращений в поддержку.\n\n"
            "Если у вас возник вопрос или проблема, нажмите **«👨‍💻 Связь с оператором»**!",
            parse_mode="Markdown"
        )
        return

    status_str = "🟢 Открыто (ожидает ответа)" if active_ticket["status"] == "open" else "🟡 В работе у оператора"
    text = (
        f"🎫 **Ваше текущее обращение #{active_ticket['id']}**\n\n"
        f"📌 **Тема:** {active_ticket['topic']}\n"
        f"🎮 **Ник:** `{active_ticket['player_nick']}`\n"
        f"📊 **Статус:** {status_str}\n"
        f"📅 **Дата создания:** {active_ticket['created_at']}\n\n"
        f"Просто напишите сообщение в чат, чтобы дополнить обращение."
    )
    await message.answer(text, reply_markup=get_player_ticket_controls(active_ticket["id"]), parse_mode="Markdown")


# ==========================================
# ПЕРЕСЫЛКА СООБЩЕНИЙ ИГРОКА ОПЕРАТОРУ
# ==========================================

@router.message(TicketChat.active_chat)
async def forward_player_message_in_state(message: Message):
    await handle_player_message(message)


@router.message(F.text, ~F.text.startswith("/"))
async def check_open_ticket_message(message: Message, state: FSMContext):
    """Ловит сообщения игрока, у которого есть открытый тикет, даже если сбросился стейт."""
    current_state = await state.get_state()
    if current_state:
        return
        
    active_ticket = await get_active_ticket_by_user(message.from_user.id)
    if active_ticket:
        await handle_player_message(message)


async def handle_player_message(message: Message):
    """Логика сохранения и пересылки сообщения игрока операторам."""
    active_ticket = await get_active_ticket_by_user(message.from_user.id)
    if not active_ticket:
        return

    ticket_id = active_ticket["id"]
    text = message.text

    # Сохраняем в БД
    await add_ticket_message(
        ticket_id=ticket_id,
        sender_id=message.from_user.id,
        sender_type="user",
        sender_name=active_ticket.get("player_nick") or message.from_user.full_name,
        text=text
    )

    alert_text = (
        f"📩 **Новое сообщение в тикете #{ticket_id}**\n"
        f"👤 От: `{active_ticket.get('player_nick')}` (ID: `{message.from_user.id}`)\n\n"
        f"💬 {text}"
    )
    markup = get_operator_ticket_controls(ticket_id)

    # Если назначен конкретный оператор, шлем ему лично
    if active_ticket.get("operator_id"):
        try:
            await message.bot.send_message(active_ticket["operator_id"], alert_text, reply_markup=markup, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Не удалось доставить сообщение оператору: {e}")
    else:
        # Иначе в чат саппорта или админам
        if config.SUPPORT_CHAT_ID != 0:
            try:
                await message.bot.send_message(config.SUPPORT_CHAT_ID, alert_text, reply_markup=markup, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Не удалось отправить в support chat: {e}")
                
    await message.answer("✅ Ваше сообщение доставлено операторам.")


# ==========================================
# ОПЕРАТОРСКИЕ ДЕЙСТВИЯ (КНОПКИ)
# ==========================================

@router.callback_query(F.data.startswith("op_take_"))
async def cb_operator_take(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[2])
    is_op = await is_operator_or_admin(callback.from_user.id, config.ADMIN_IDS)
    if not is_op:
        await callback.answer("⛔ У вас нет прав оператора!", show_alert=True)
        return

    ticket = await get_ticket(ticket_id)
    if not ticket:
        await callback.answer("Тикет не найден.", show_alert=True)
        return

    await assign_ticket_operator(ticket_id, callback.from_user.id)
    op_name = callback.from_user.full_name
    
    await callback.message.edit_text(
        f"{callback.message.text}\n\n👨‍💼 **Тикет взят в работу оператором:** {op_name}",
        reply_markup=get_operator_ticket_controls(ticket_id, status="in_progress"),
        parse_mode="Markdown"
    )
    
    # Уведомляем игрока
    try:
        await callback.bot.send_message(
            ticket["user_id"],
            f"👨‍💼 Оператор **{op_name}** взял ваше обращение #{ticket_id} в работу!",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Не удалось уведомить игрока о взятии тикета: {e}")

    await callback.answer("Вы успешно взяли тикет в работу!")


@router.callback_query(F.data.startswith("op_reply_"))
async def cb_operator_reply_start(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split("_")[2])
    is_op = await is_operator_or_admin(callback.from_user.id, config.ADMIN_IDS)
    if not is_op:
        await callback.answer("⛔ У вас нет прав оператора!", show_alert=True)
        return

    ticket = await get_ticket(ticket_id)
    if not ticket or ticket["status"] == "closed":
        await callback.answer("Этот тикет закрыт или не существует.", show_alert=True)
        return

    await state.set_state(OperatorReply.entering_text)
    await state.update_data(ticket_id=ticket_id)

    await callback.message.answer(
        f"✍️ **Введите ответ для игрока по тикету #{ticket_id}:**\n"
        f"(Ник: `{ticket.get('player_nick')}`, Тема: {ticket.get('topic')})",
        reply_markup=get_operator_reply_cancel_inline(ticket_id),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("op_cancel_reply_"))
async def cb_cancel_operator_reply(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Ответ отменен.")
    await callback.answer()


@router.message(OperatorReply.entering_text)
async def process_operator_reply_text(message: Message, state: FSMContext):
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    await state.clear()

    ticket = await get_ticket(ticket_id)
    if not ticket or ticket["status"] == "closed":
        await message.answer("⚠️ Обращение уже закрыто или не найдено.")
        return

    reply_text = message.text
    op_name = message.from_user.full_name or "Оператор поддержки"

    # Сохраняем ответ в БД
    await add_ticket_message(
        ticket_id=ticket_id,
        sender_id=message.from_user.id,
        sender_type="operator",
        sender_name=op_name,
        text=reply_text
    )

    # Отправляем игроку
    user_msg = (
        f"👨‍💻 **Ответ оператора по обращению #{ticket_id}:**\n\n"
        f"{reply_text}\n\n"
        f"────────────────────\n"
        f"💬 *Вы можете ответить на это сообщение, чтобы продолжить диалог, "
        f"или закрыть обращение, если вопрос решен.*"
    )
    try:
        await message.bot.send_message(
            ticket["user_id"],
            user_msg,
            reply_markup=get_player_ticket_controls(ticket_id),
            parse_mode="Markdown"
        )
        await message.answer(f"✅ Ваш ответ успешно отправлен игроку по тикету #{ticket_id}!")
    except Exception as e:
        logger.error(f"Не удалось отправить ответ игроку {ticket['user_id']}: {e}")
        await message.answer(f"⚠️ Не удалось доставить сообщение игроку (возможно, он заблокировал бота). Ошибка: {e}")


@router.callback_query(F.data.startswith("op_history_"))
async def cb_operator_view_history(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[2])
    messages = await get_ticket_messages(ticket_id)
    if not messages:
        await callback.answer("История переписки пуста.", show_alert=True)
        return

    history_text = f"📜 **История сообщений по тикету #{ticket_id}:**\n\n"
    for m in messages:
        sender_prefix = "👤 Игрок" if m["sender_type"] == "user" else "👨‍💼 Оператор"
        history_text += f"**[{m['created_at'][11:16]}] {sender_prefix} ({m['sender_name']}):**\n{m['text']}\n\n"

    # Если текст слишком длинный для одного сообщения в ТГ (лимит 4096 символов)
    if len(history_text) > 4000:
        history_text = history_text[-3900:]
        history_text = "*(показаны последние сообщения)*\n\n" + history_text

    await callback.message.answer(history_text, parse_mode="Markdown")
    await callback.answer()


# ==========================================
# ЗАКРЫТИЕ ТИКЕТОВ
# ==========================================

@router.callback_query(F.data.startswith("op_close_"))
async def cb_operator_close(callback: CallbackQuery):
    ticket_id = int(callback.data.split("_")[2])
    is_op = await is_operator_or_admin(callback.from_user.id, config.ADMIN_IDS)
    if not is_op:
        await callback.answer("⛔ Только оператор может закрыть тикет этой кнопкой!", show_alert=True)
        return

    await perform_close_ticket(ticket_id, closed_by="operator", operator_name=callback.from_user.full_name, bot=callback.bot)
    await callback.message.edit_text(f"{callback.message.text}\n\n🔒 **Тикет #{ticket_id} закрыт оператором.**", parse_mode="Markdown")
    await callback.answer("Тикет успешно закрыт!")


@router.callback_query(F.data.startswith("user_close_ticket_"))
async def cb_user_close(callback: CallbackQuery, state: FSMContext):
    ticket_id = int(callback.data.split("_")[3])
    await state.clear()
    await perform_close_ticket(ticket_id, closed_by="user", operator_name=None, bot=callback.bot)
    await callback.message.edit_text(
        f"🔒 **Ваше обращение #{ticket_id} закрыто.**\n\n"
        f"Спасибо за обращение в службу поддержки {config.SERVER_NAME}!\n"
        f"Если у вас появятся новые вопросы, мы всегда рады помочь.",
        parse_mode="Markdown"
    )
    await callback.answer("Обращение закрыто.")


@router.message(Command("close"))
async def cmd_close_ticket(message: Message, state: FSMContext):
    """Команда /close для закрытия тикета."""
    args = message.text.split()
    is_op = await is_operator_or_admin(message.from_user.id, config.ADMIN_IDS)
    
    if len(args) > 1 and args[1].isdigit():
        ticket_id = int(args[1])
        if not is_op:
            await message.answer("Закрывать чужие тикеты по номеру могут только операторы.")
            return
        await perform_close_ticket(ticket_id, closed_by="operator", operator_name=message.from_user.full_name, bot=message.bot)
        await message.answer(f"🔒 Тикет #{ticket_id} закрыт.")
        return

    # Если без аргументов — закрывает собственный тикет
    active_ticket = await get_active_ticket_by_user(message.from_user.id)
    if not active_ticket:
        await message.answer("У вас нет активного тикета для закрытия.")
        return

    await state.clear()
    await perform_close_ticket(active_ticket["id"], closed_by="user", operator_name=None, bot=message.bot)
    await message.answer(f"🔒 Ваше обращение #{active_ticket['id']} успешно закрыто.")


@router.message(Command("reply"))
async def cmd_reply_ticket(message: Message):
    """Команда /reply <id> <текст ответа> для операторов."""
    is_op = await is_operator_or_admin(message.from_user.id, config.ADMIN_IDS)
    if not is_op:
        await message.answer("⛔ Данная команда доступна только операторам техподдержки.")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.answer("ℹ️ **Использование:** `/reply <ID_тикета> <текст ответа>`\nПример: `/reply 12 Здравствуйте! Проверьте сейчас.`", parse_mode="Markdown")
        return

    ticket_id = int(parts[1])
    reply_text = parts[2]
    ticket = await get_ticket(ticket_id)

    if not ticket:
        await message.answer(f"⚠️ Тикет #{ticket_id} не найден.")
        return

    if ticket["status"] == "closed":
        await message.answer(f"⚠️ Тикет #{ticket_id} уже закрыт.")
        return

    op_name = message.from_user.full_name or "Оператор поддержки"
    await add_ticket_message(
        ticket_id=ticket_id,
        sender_id=message.from_user.id,
        sender_type="operator",
        sender_name=op_name,
        text=reply_text
    )

    user_msg = (
        f"👨‍💻 **Ответ оператора по обращению #{ticket_id}:**\n\n"
        f"{reply_text}\n\n"
        f"────────────────────\n"
        f"💬 *Вы можете написать ответ прямо сюда.*"
    )
    try:
        await message.bot.send_message(
            ticket["user_id"],
            user_msg,
            reply_markup=get_player_ticket_controls(ticket_id),
            parse_mode="Markdown"
        )
        await message.answer(f"✅ Ответ успешно доставлен игроку по тикету #{ticket_id}!")
    except Exception as e:
        await message.answer(f"⚠️ Ошибка отправки игроку: {e}")


async def perform_close_ticket(ticket_id: int, closed_by: str, operator_name: str | None, bot):
    """Общая функция закрытия обращения."""
    ticket = await get_ticket(ticket_id)
    if not ticket or ticket["status"] == "closed":
        return

    await close_ticket(ticket_id)

    # Если закрыл оператор, уведомляем игрока
    if closed_by == "operator":
        try:
            name_str = f"оператором **{operator_name}**" if operator_name else "оператором"
            await bot.send_message(
                ticket["user_id"],
                f"🔒 **Ваше обращение #{ticket_id} было закрыто {name_str}.**\n\n"
                f"Если ваш вопрос не был решен или появились новые вопросы, вы всегда можете открыть новое обращение в меню бота.\n"
                f"Спасибо, что играете на {config.SERVER_NAME}!",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить пользователя о закрытии тикета: {e}")

