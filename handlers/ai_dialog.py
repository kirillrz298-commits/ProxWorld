from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction

from states import AIDialog
from ai_helper import ai_assistant
from keyboards import get_ai_dialog_inline, get_main_reply_keyboard
from database import is_operator_or_admin
from config import config

router = Router(name="ai_dialog_router")

AI_GREETING = (
    "╭━━━━━━━━━━━━━━━━━━━━╮\n"
    "│   🤖 **НЕЙРОСЕТЬ PROXWORLD**  │\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
    "Привет! Я официальный ИИ-ассистент сервера **ProxWorld** 24/7.\n\n"
    "💡 **Я могу помочь вам с:**\n"
    "▸ Проблемами со входом, лаунчером и версиями (1.16.5 - 1.21+)\n"
    "▸ Вопросами по донату и связи с @DesTrooyda\n"
    "▸ Командами сервера, приватами, кланами и выживанием\n"
    "▸ Правилами сервера и порядком апелляции блокировок\n\n"
    "💬 *Напишите ваш вопрос прямо сюда в чат:*"
)

@router.message(F.text == "🤖 Задать вопрос ИИ")
@router.callback_query(F.data == "start_ai_dialog")
async def start_ai_chat(event: Message | CallbackQuery, state: FSMContext):
    await state.set_state(AIDialog.chatting)
    await state.update_data(history=[])
    
    if isinstance(event, CallbackQuery):
        await event.message.answer(AI_GREETING, reply_markup=get_ai_dialog_inline(), parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(AI_GREETING, reply_markup=get_ai_dialog_inline(), parse_mode="Markdown")


@router.message(AIDialog.chatting)
async def process_ai_question(message: Message, state: FSMContext):
    user_text = message.text
    if not user_text:
        await message.answer("Пожалуйста, напишите ваш вопрос текстом.")
        return

    # Отправляем индикатор набора текста
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Получаем историю диалога из стейта
    data = await state.get_data()
    history = data.get("history", [])

    # Запрашиваем ответ у ИИ
    response_text = await ai_assistant.get_response(user_text, history)

    # Обновляем историю диалога
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": response_text})
    await state.update_data(history=history)

    await message.answer(
        response_text,
        reply_markup=get_ai_dialog_inline(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "exit_ai_dialog")
async def exit_ai_chat(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    is_op = await is_operator_or_admin(callback.from_user.id, config.ADMIN_IDS)
    await callback.message.edit_text("Вы вышли из режима диалога с ИИ-помощником.", parse_mode="Markdown")
    await callback.message.answer(
        "Выберите действие в главном меню:",
        reply_markup=get_main_reply_keyboard(is_operator=is_op)
    )
    await callback.answer()

