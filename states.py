from aiogram.fsm.state import State, StatesGroup

class TicketCreation(StatesGroup):
    choosing_topic = State()
    entering_nick = State()
    entering_description = State()

class TicketChat(StatesGroup):
    active_chat = State()  # Состояние, когда игрок общается внутри тикета

class OperatorReply(StatesGroup):
    entering_text = State()

class AIDialog(StatesGroup):
    chatting = State()

class AdminStates(StatesGroup):
    adding_operator = State()
    removing_operator = State()
    broadcast_message = State()

