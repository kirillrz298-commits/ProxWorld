from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from config import config
from keyboards import (
    get_login_issues_inline,
    get_donate_issues_inline,
    get_punishment_issues_inline,
    get_faq_inline
)

router = Router(name="categories_router")

# ==========================================
# 🔑 1. ПРОБЛЕМЫ СО ВХОДОМ
# ==========================================

@router.message(F.text == "🔑 Проблемы со входом")
async def menu_login_issues(message: Message):
    text = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "│  🔑 **ПРОБЛЕМЫ СО ВХОДОМ**  │\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "Часто сложности при подключении к **ProxWorld** вызваны ошибкой пароля, сбоем сессии или настройками сети.\n\n"
        "👇 *Выберите вашу проблему ниже, чтобы получить инструкцию по решению:*"
    )
    await message.answer(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "issue_password")
async def cb_issue_password(callback: CallbackQuery):
    text = (
        "╭─ 🔐 **Забыли пароль от аккаунта?** ──────\n"
        "│ Сервер: ProxWorld\n"
        "╰──────────────────────────────────\n\n"
        "▸ **1. Если вы помните старый пароль:**\n"
        "   Зайдите на сервер и смените пароль: `/changepassword <старый> <новый>`\n\n"
        "▸ **2. Если аккаунт был привязан:**\n"
        "   Воспользуйтесь официальным сервисом привязки для моментального восстановления.\n\n"
        "▸ **3. Если доступ утерян полностью:**\n"
        "   Создайте обращение к операторам! Прикрепите доказательства владения аккаунтом (чеки покупок, скриншоты игры)."
    )
    await callback.message.edit_text(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "issue_session")
async def cb_issue_session(callback: CallbackQuery):
    text = (
        "╭─ 🚫 **Ошибка сессии или лаунчера** ──────\n"
        "│ Решение типичных ошибок клиента\n"
        "╰──────────────────────────────────\n\n"
        "✦ **«Invalid Session» / «Недействительная сессия»:**\n"
        "  Полностью закройте игру и перезапустите лаунчер (TLauncher, Prism, Lunar и т.д.).\n\n"
        "✦ **«Вы уже играете на сервере»:**\n"
        "  Сессия подвисла после отключения. Подождите 1 минуту — сервер автоматически сбросит её.\n\n"
        "✦ **«Недопустимые символы в нике»:**\n"
        "  Никнейм должен состоять из 3-16 символов английского алфавита и цифр."
    )
    await callback.message.edit_text(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "issue_ping")
async def cb_issue_ping(callback: CallbackQuery):
    text = (
        "╭─ 📡 **Сервер не пингуется или не виден** ─\n"
        "│ Сетевая диагностика подключения\n"
        "╰──────────────────────────────────\n\n"
        f"▸ 1. Проверьте правильность адреса: `{config.SERVER_IP}` *(в разработке)*\n"
        f"▸ 2. Поддерживаемые версии клиента: **{config.SERVER_VERSIONS}**\n"
        f"▸ 3. Отключите сторонние VPN или прокси, которые могут блокировать соединение.\n"
        f"▸ 4. Перезагрузите роутер или подождите пару минут (сервер может быть на тех. обслуживании)."
    )
    await callback.message.edit_text(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")
    await callback.answer()


# ==========================================
# 💎 2. ДОНАТ И ПОКУПКИ
# ==========================================

@router.message(F.text == "💎 Донат и покупки")
async def menu_donate_issues(message: Message):
    text = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "│   💎 **ДОНАТ И ПОКУПКИ**    │\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "По всем вопросам покупки доната, привилегий, кейсов и наборов на сервере **ProxWorld**:\n\n"
        f"✦ **Связь по донату:** {config.SERVER_SITE}\n"
        "✦ **Время зачисления:** обычно моментально (в редких случаях до 15-20 минут)\n\n"
        "👇 *Выберите ваш вопрос или создайте обращение:*"
    )
    await message.answer(text, reply_markup=get_donate_issues_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "donate_delayed")
async def cb_donate_delayed(callback: CallbackQuery):
    text = (
        "╭─ ⏳ **Задержка выдачи доната** ──────────\n"
        "│ Что делать, если донат не пришёл?\n"
        "╰──────────────────────────────────\n\n"
        "▸ **1. Проверка в игре:**\n"
        "   Перезайдите на сервер и введите команду `/cart` или `/menu`.\n\n"
        "▸ **2. Ожидание обработки:**\n"
        "   Иногда платежная система обрабатывает платеж до 15 минут.\n\n"
        "▸ **3. Связь с поддержкой:**\n"
        f"   Если прошло больше времени — напишите {config.SERVER_SITE} или создайте тикет оператору с чеком оплаты!"
    )
    await callback.message.edit_text(text, reply_markup=get_donate_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "donate_transfer")
async def cb_donate_transfer(callback: CallbackQuery):
    text = (
        "╭─ 🔄 **Перенос доната на другой ник** ─────\n"
        "│ Условия переноса привилегий\n"
        "╰──────────────────────────────────\n\n"
        "✦ Перенос возможен только по согласованию с Главной Администрацией.\n"
        "✦ Обязательно потребуется предоставить чек/выписку об оплате и подтвердить владение обоими никами.\n\n"
        f"👉 Для переноса свяжитесь с {config.SERVER_SITE} или нажмите **«Связаться с оператором»**."
    )
    await callback.message.edit_text(text, reply_markup=get_donate_issues_inline(), parse_mode="Markdown")
    await callback.answer()


# ==========================================
# 🔨 3. БЛОКИРОВКИ И НАКАЗАНИЯ
# ==========================================

@router.message(F.text == "🔨 Блокировки и наказания")
async def menu_punishment_issues(message: Message):
    text = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "│  🔨 **БЛОКИРОВКИ И НАКАЗАНИЯ** │\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "Мы следим за честной и комфортной игрой на сервере **ProxWorld**.\n\n"
        "Если ваш аккаунт заблокирован античитом или персоналом, ознакомьтесь с информацией ниже:"
    )
    await message.answer(text, reply_markup=get_punishment_issues_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "ban_anticheat")
async def cb_ban_anticheat(callback: CallbackQuery):
    text = (
        "╭─ 🛡️ **Блокировка античитом (Консоль)** ──\n"
        "│ Сервер: ProxWorld\n"
        "╰──────────────────────────────────\n\n"
        "Античит автоматически наказывает за подозрительные пакеты и чит-клиенты.\n\n"
        "✦ Если бан выдан по ошибке из-за резкого скачка пинга/лага — подайте апелляцию через тикет оператору.\n"
        f"✦ По вопросам разбана вы также можете обратиться к {config.SERVER_SITE}."
    )
    await callback.message.edit_text(text, reply_markup=get_punishment_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "ban_moderator")
async def cb_ban_moderator(callback: CallbackQuery):
    text = (
        "╭─ 👮 **Блокировка модератором** ─────────\n"
        "│ Порядок обжалования наказания\n"
        "╰──────────────────────────────────\n\n"
        "Каждый модератор хранит доказательства выданного наказания.\n\n"
        "▸ **Как подать апелляцию:**\n"
        "1. Нажмите **«Подать апелляцию (Тикет)»**\n"
        "2. Укажите: ваш ник, ник модератора, причину бана и почему считаете наказание ошибочным\n"
        "3. Ожидайте ответа старшей администрации."
    )
    await callback.message.edit_text(text, reply_markup=get_punishment_issues_inline(), parse_mode="Markdown")
    await callback.answer()


# ==========================================
# ❓ 4. ЧАСТЫЕ ВОПРОСЫ (FAQ)
# ==========================================

@router.message(F.text == "❓ Частые вопросы")
async def menu_faq_issues(message: Message):
    text = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "│   ❓ **БАЗА ЗНАНИЙ (FAQ)**   │\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "Здесь собраны ответы на самые частые вопросы игроков сервера **ProxWorld**:\n\n"
        "👇 *Выберите интересующий вас раздел:*"
    )
    await message.answer(text, reply_markup=get_faq_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "faq_start")
async def cb_faq_start(callback: CallbackQuery):
    text = (
        "╭─ 🎮 **Как начать играть на ProxWorld:** ──\n"
        "│ Пошаговая инструкция для новичков\n"
        "╰──────────────────────────────────\n\n"
        f"▸ 1. Запустите Minecraft (версия **{config.SERVER_VERSIONS}**)\n"
        f"▸ 2. Добавьте сервер в сетевую игру: `{config.SERVER_IP}` *(в разработке)*\n"
        "▸ 3. Подключитесь и зарегистрируйтесь: `/register <пароль> <повтор>`\n"
        "▸ 4. При повторном входе введите: `/login <пароль>`\n"
        "▸ 5. Используйте `/rtp` для случайного перемещения в мир и начинайте строить базу!"
    )
    await callback.message.edit_text(text, reply_markup=get_faq_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "faq_rules")
async def cb_faq_rules(callback: CallbackQuery):
    text = (
        "╭─ ⚔️ **Правила грифа и выживания:** ─────\n"
        "│ ProxWorld: честная и захватывающая игра\n"
        "╰──────────────────────────────────\n\n"
        "✦ Разрешены рейды баз, ловушки и взрывы динамитом.\n"
        "✦ **Запрещено:** использование стороннего софта (читов, X-Ray), дюпы, краш-машины и спам.\n"
        f"✦ По всем правилам и вопросам обращайтесь к {config.SERVER_SITE}."
    )
    await callback.message.edit_text(text, reply_markup=get_faq_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "faq_commands")
async def cb_faq_commands(callback: CallbackQuery):
    text = (
        "╭─ ⌨️ **Полезные команды сервера:** ──────\n"
        "│ Нажмите на команду для копирования\n"
        "╰──────────────────────────────────\n\n"
        "• `/menu` — главное меню сервера\n"
        "• `/rtp` — телепортация в дикий мир\n"
        "• `/spawn` — возвращение на спавн\n"
        "• `/sethome [имя]` — установить точку дома\n"
        "• `/home [имя]` — телепорт домой\n"
        "• `/tpa [ник]` — запрос на телепортацию к игроку\n"
        "• `/ah` — игровой аукцион предметов\n"
        "• `/pay [ник] [сумма]` — перевод игровой валюты\n"
        "• `/clan` — управление кланом"
    )
    await callback.message.edit_text(text, reply_markup=get_faq_inline(), parse_mode="Markdown")
    await callback.answer()
