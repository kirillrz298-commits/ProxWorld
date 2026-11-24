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
        "🔑 **Проблемы со входом на сервер ProxGrief**\n\n"
        "Часто проблемы со входом вызваны ошибкой пароля, рассинхроном сессии или сетевыми сбоями.\n\n"
        "Выберите вашу проблему из списка ниже, чтобы прочесть инструкцию:"
    )
    await message.answer(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "issue_password")
async def cb_issue_password(callback: CallbackQuery):
    text = (
        "🔐 **Забыли пароль от аккаунта?**\n\n"
        "1. **Если вы ранее привязывали аккаунт:**\n"
        "   Воспользуйтесь официальным ботом привязки VK/Telegram для мгновенного сброса пароля.\n\n"
        "2. **Если вы помните старый пароль:**\n"
        "   Зайдите на сервер и введите команду: `/changepassword <старый_пароль> <новый_пароль>`\n\n"
        "3. **Если привязки не было:**\n"
        "   Создайте обращение к операторам, прикрепив скриншоты чеков доната или доказательства владения аккаунтом."
    )
    await callback.message.edit_text(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "issue_session")
async def cb_issue_session(callback: CallbackQuery):
    text = (
        "🚫 **Ошибка «Неверная сессия» или сбой клиента:**\n\n"
        "• **Ошибка 'Invalid Session':**\n"
        "  Полностью закройте Minecraft и перезапустите лаунчер (TLauncher, Prism, Lunar и т.д.).\n\n"
        "• **Ошибка 'Вы уже играете на сервере':**\n"
        "  Сервер удерживает сессию после дисконнекта. Подождите ровно 1 минуту и войдите снова.\n\n"
        "• **Ошибка 'Недопустимый ник':**\n"
        "  Ник должен быть от 3 до 16 символов латиницей без пробелов и спецсимволов."
    )
    await callback.message.edit_text(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "issue_ping")
async def cb_issue_ping(callback: CallbackQuery):
    text = (
        f"📡 **Сервер не пингуется или пишет «Can't resolve hostname»:**\n\n"
        f"1. Проверьте правильность введенного адреса: `{config.SERVER_IP}` (порт `{config.SERVER_PORT}`).\n"
        f"2. Попробуйте отключить сторонние VPN или прокси-сервисы.\n"
        f"3. Проверьте статус вашей интернет-сети или перезагрузите роутер.\n"
        f"4. Убедитесь, что версия вашего клиента поддерживается ({config.SERVER_VERSIONS}). Рекомендуемая версия: **1.16.5 / 1.20.2**."
    )
    await callback.message.edit_text(text, reply_markup=get_login_issues_inline(), parse_mode="Markdown")
    await callback.answer()


# ==========================================
# 💎 2. ДОНАТ И ПОКУПКИ
# ==========================================

@router.message(F.text == "💎 Донат и покупки")
async def menu_donate_issues(message: Message):
    text = (
        "💎 **Раздел «Донат и покупки»**\n\n"
        f"Официальный онлайн-магазин сервера: {config.SERVER_DONATE_URL}\n\n"
        "Все покупки на сервере обрабатываются в автоматическом режиме через защищенные платежные шлюзы.\n\n"
        "Выберите ваш вопрос:"
    )
    await message.answer(text, reply_markup=get_donate_issues_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "donate_delayed")
async def cb_donate_delayed(callback: CallbackQuery):
    text = (
        "⏳ **Донат не пришел вовремя:**\n\n"
        "1. **Время зачисления:**\n"
        "   В среднем оплата проходит за **1-5 минут**, но из-за нагрузки платежной системы может занимать до 20 минут.\n\n"
        "2. **Проверка на сервере:**\n"
        "   • Перезайдите на сервер.\n"
        "   • Введите команду `/cart` или `/menu`.\n\n"
        "3. **Если прошло более 20 минут:**\n"
        "   Создайте тикет оператору! Обязательно укажите ваш ник, точное время оплаты и прикрепите электронный чек."
    )
    await callback.message.edit_text(text, reply_markup=get_donate_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "donate_transfer")
async def cb_donate_transfer(callback: CallbackQuery):
    text = (
        "🔄 **Перенос донат-привилегий на другой ник:**\n\n"
        "• Перенос привилегий возможен только по решению Главной Администрации.\n"
        "• Для переноса необходимо предоставить чек покупки с почты/банка и доступ к обоим аккаунтам.\n\n"
        "Нажмите кнопку **«Связаться с оператором»**, чтобы отправить заявку на перенос."
    )
    await callback.message.edit_text(text, reply_markup=get_donate_issues_inline(), parse_mode="Markdown")
    await callback.answer()


# ==========================================
# 🔨 3. БЛОКИРОВКИ И НАКАЗАНИЯ
# ==========================================

@router.message(F.text == "🔨 Блокировки и наказания")
async def menu_punishment_issues(message: Message):
    text = (
        "🔨 **Блокировки и наказания**\n\n"
        "Мы строго следим за честной игрой и соблюдением правил на сервере ProxGrief.\n\n"
        "Если ваш аккаунт был заблокирован античитом или персоналом, выберите подходящий пункт:"
    )
    await message.answer(text, reply_markup=get_punishment_issues_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "ban_anticheat")
async def cb_ban_anticheat(callback: CallbackQuery):
    text = (
        "🛡️ **Блокировка античитом (Консолью):**\n\n"
        "Античит сервера блокирует за подозрительные пакеты, читы (Killaura, Fly, Speedmine, Baritone и др.).\n\n"
        "• Если бан произошел из-за сильного лага/пинга, подайте заявку через оператора с описанием момента блокировки.\n"
        "• Разбан можно приобрести моментально в нашем магазине без ожидания."
    )
    await callback.message.edit_text(text, reply_markup=get_punishment_issues_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "ban_moderator")
async def cb_ban_moderator(callback: CallbackQuery):
    text = (
        "👮 **Блокировка модератором:**\n\n"
        "Модераторы всегда имеют доказательства (видеозапись или скриншот нарушения).\n\n"
        "**Как обжаловать:**\n"
        "1. Создайте тикет оператору.\n"
        "2. Укажите: Ваш ник, ник модератора, причину бана и почему вы считаете наказание ошибочным.\n"
        "3. Ожидайте ответа старшей модерации."
    )
    await callback.message.edit_text(text, reply_markup=get_punishment_issues_inline(), parse_mode="Markdown")
    await callback.answer()


# ==========================================
# ❓ 4. ЧАСТЫЕ ВОПРОСЫ (FAQ)
# ==========================================

@router.message(F.text == "❓ Частые вопросы")
async def menu_faq_issues(message: Message):
    text = (
        "❓ **База знаний и частые вопросы (FAQ)**\n\n"
        "Здесь собраны ответы на самые популярные вопросы новичков и опытных гриферов сервера ProxGrief:"
    )
    await message.answer(text, reply_markup=get_faq_inline(), parse_mode="Markdown")


@router.callback_query(F.data == "faq_start")
async def cb_faq_start(callback: CallbackQuery):
    text = (
        f"🎮 **Как начать играть на {config.SERVER_NAME}:**\n\n"
        f"1. Запустите лаунчер Minecraft (версия {config.SERVER_VERSIONS}).\n"
        f"2. Добавьте в сетевой игре сервер: `{config.SERVER_IP}`\n"
        f"3. Войдите на сервер и зарегистрируйтесь командой: `/register <пароль> <повтор>`\n"
        f"4. При следующих входах используйте: `/login <пароль>`\n"
        f"5. Напишите `/rtp` для случайной телепортации в мир и начните строить базу!"
    )
    await callback.message.edit_text(text, reply_markup=get_faq_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "faq_rules")
async def cb_faq_rules(callback: CallbackQuery):
    text = (
        "⚔️ **Правила грифа и приватов:**\n\n"
        "• ProxGrief — анархо-гриферский сервер, здесь разрешены взрывы баз, ловушки и рейды!\n"
        "• Запрещено использование стороннего ПО (читов), дюпов, краш-машин и оскорбления администрации.\n"
        "• Не доверяйте пароли и доступ в регион непроверенным игрокам.\n\n"
        f"Полный свод правил: {config.SERVER_RULES_URL}"
    )
    await callback.message.edit_text(text, reply_markup=get_faq_inline(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "faq_commands")
async def cb_faq_commands(callback: CallbackQuery):
    text = (
        "⌨️ **Основные команды сервера:**\n\n"
        "• `/menu` — главное меню сервера\n"
        "• `/rtp` — случайная телепортация в дикий мир\n"
        "• `/spawn` — возвращение на спавн\n"
        "• `/sethome [название]` — установить точку дома\n"
        "• `/home [название]` — телепорт домой\n"
        "• `/tpa [ник]` — отправить запрос на телепортацию\n"
        "• `/ah` или `/auc` — аукцион сервера\n"
        "• `/pay [ник] [сумма]` — перевести игровую валюту\n"
        "• `/clan` — управление кланом"
    )
    await callback.message.edit_text(text, reply_markup=get_faq_inline(), parse_mode="Markdown")
    await callback.answer()

