import logging
from typing import Optional, List, Dict
from openai import AsyncOpenAI
from config import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""
Ты — официальный ИИ-помощник службы поддержки популярного Minecraft-сервера "{config.SERVER_NAME}" (Гриферский сервер выживания).
Твоя задача — вежливо, чётко, дружелюбно и профессионально помогать игрокам решать их проблемы.

Информация о сервере {config.SERVER_NAME}:
- IP для подключения: {config.SERVER_IP} (Порт по умолчанию: {config.SERVER_PORT})
- Поддерживаемые версии клиента: {config.SERVER_VERSIONS}
- Официальный сайт и покупка доната: {config.SERVER_SITE} ({config.SERVER_DONATE_URL})
- Правила сервера: {config.SERVER_RULES_URL}
- Сообщество ВКонтакте: {config.SERVER_VK_URL}
- Discord сервер: {config.SERVER_DISCORD_URL}

Специфика гриф-сервера:
1. Проблемы со входом:
   - "Забыл пароль" -> Восстановление через привязанный ВК/ТГ или через тикет оператору. Игрок может использовать /changepassword если помнит старый пароль.
   - "Неверная сессия / Перезапустите игру" -> Полностью перезапустить лаунчер Minecraft.
   - "Вы не зарегистрированы" -> Написать в чате: /register <пароль> <повтор_пароля>
   - "Вы уже на сервере" -> Подождать 1-2 минуты, сервер сбросит зависшую сессию.
   - "Не пингуется сервер" -> Проверить интернет, отключить VPN/Proxy или попробовать альтернативный IP.
2. Донат и покупки:
   - Покупки выдаются автоматически в течение 5-15 минут после оплаты на сайте {config.SERVER_DONATE_URL}.
   - Если прошло более 15 минут: игроку нужно подготовить чек/квитанцию, указать ник и сервер и нажать "👨‍💻 Связь с оператором".
   - Перенос доната возможен только через главного администратора при подтверждении чека.
3. Блокировки и наказания:
   - Блокировки консоли / античита (Auto-Ban): если игрок уверен в ошибке, необходимо подать апелляцию через оператора с доказательствами (скриншоты, логи).
   - Блокировки модераторами: указать ник модератора, причину и пункт правил.
   - Покупка разбана доступна на сайте {config.SERVER_DONATE_URL}.
4. Геймплей и приваты:
   - Сервер гриферский: гриферство, рейды баз и взрывы динамитом разрешены в рамках правил.
   - Приваты регионов создаются деревянным топором (//wand) или через авто-приват блоками.

ВАЖНЫЕ ПРАВИЛА ДЛЯ ТЕБЯ:
1. Отвечай кратко, по делу и структурированно (используй списки и эмодзи).
2. Обращайся к игроку на "ты" или уважительное "вы", будь доброжелательным саппортом.
3. Если вопрос касается возврата денег, проверки транзакций, разбана по ошибке модератора, пропажи доната, взлома аккаунта — обязательно посоветуй обратиться к живому оператору кнопкой «👨‍💻 Связь с оператором».
4. Не придумывай несуществующие команды сервера. Если не знаешь точного ответа, честно скажи и предложи помощь живого специалиста поддержки.
"""

# Базовые быстрые ответы (fallback на случай отсутствия API ключа)
FALLBACK_ANSWERS = [
    {
        "keywords": ["пароль", "забыл пароль", "восстановить", "сброс пароля"],
        "answer": f"🔑 **Восстановление пароля:**\n\n1. Если аккаунт был привязан к ВК/ТГ, восстановите доступ через бота привязки.\n2. Если привязки не было, вам поможет живой оператор! Нажмите кнопку **«👨‍💻 Связь с оператором»** и укажите ваш ник."
    },
    {
        "keywords": ["не заходит", "ошибка входа", "не могу зайти", "сессия", "версия", "айпи", "ip"],
        "answer": f"🌐 **Проблемы с подключением к {config.SERVER_NAME}:**\n\n• **IP сервера:** `{config.SERVER_IP}`\n• **Версии:** {config.SERVER_VERSIONS}\n• Перезапустите ваш лаунчер Minecraft.\n• Попробуйте отключить или включить VPN.\n• Убедитесь, что ник не содержит запрещенных символов."
    },
    {
        "keywords": ["донат", "не пришел", "купил", "деньги списали", "покупка", "привилеги"],
        "answer": f"💎 **Вопросы по донату:**\n\n• Покупки обычно зачисляются в течение **5-15 минут**.\n• На сервере введите команду `/cart` или перезайдите на сервер.\n• Если донат не пришел через 20 минут, нажмите кнопку **«👨‍💻 Связь с оператором»** и пришлите чек/номер заказа."
    },
    {
        "keywords": ["бан", "забанили", "разбан", "кик", "мут", "апелляци", "наказан"],
        "answer": f"🔨 **Блокировки и наказания:**\n\n• Узнать причину можно при попытке входа на сервер.\n• Разбан можно приобрести на сайте: {config.SERVER_DONATE_URL}\n• Если считаете бан ошибочным, нажмите **«👨‍💻 Связь с оператором»** и подайте заявку на разбан."
    }
]


class AIAssistant:
    def __init__(self):
        self.api_key = config.AI_API_KEY
        self.base_url = config.AI_BASE_URL
        self.model = config.AI_MODEL
        self.enabled = config.AI_ENABLED
        self.client: Optional[AsyncOpenAI] = None

        if self.enabled and self.api_key and self.api_key != "YOUR_AI_API_KEY_HERE":
            try:
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
                logger.info(f"AI Assistant успешно настроен. Модель: {self.model}, Base URL: {self.base_url}")
            except Exception as e:
                logger.error(f"Ошибка при инициализации AI клиента: {e}")
                self.client = None
        else:
            logger.warning("AI_API_KEY не задан или выключен. Бот будет использовать встроенную базу знаний.")

    def is_configured(self) -> bool:
        """Проверка, готов ли клиент ИИ к работе с внешним API."""
        return bool(self.client and self.api_key and self.api_key != "YOUR_AI_API_KEY_HERE")

    def _fallback_search(self, user_text: str) -> Optional[str]:
        """Поиск по локальной базе знаний."""
        text_lower = user_text.lower()
        for item in FALLBACK_ANSWERS:
            if any(kw in text_lower for kw in item["keywords"]):
                return item["answer"]
        return None

    async def get_response(self, user_question: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Получить ответ от ИИ-помощника или из базы знаний."""
        # 1. Если ИИ настроен и включен
        if self.is_configured():
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                if history:
                    messages.extend(history[-6:])  # До 6 последних сообщений контекста
                messages.append({"role": "user", "content": user_question})

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=600,
                    temperature=0.7
                )
                answer = response.choices[0].message.content.strip()
                return answer
            except Exception as e:
                logger.error(f"Ошибка вызова AI API: {e}")
                # Если сбой в API, пробуем fallback
                fallback = self._fallback_search(user_question)
                if fallback:
                    return f"{fallback}\n\n*(Ответ из базы знаний, сервис ИИ временно недоступен)*"
                return (
                    "⚠️ Сервис ИИ сейчас временно недоступен.\n\n"
                    "Вы можете обратиться напрямую к нашей службе поддержки: "
                    "нажмите кнопку **«👨‍💻 Связь с оператором»** ниже!"
                )

        # 2. Если API ключ не настроен - используем умный fallback
        fallback = self._fallback_search(user_question)
        if fallback:
            return fallback

        return (
            f"🤖 **ИИ-помощник {config.SERVER_NAME}:**\n\n"
            f"Я не нашёл точного ответа на ваш вопрос в быстрой базе знаний.\n\n"
            f"Пожалуйста, обратитесь к живому оператору — наши специалисты всегда готовы помочь вам!\n\n"
            f"👇 Нажмите кнопку **«👨‍💻 Связь с оператором»** ниже, чтобы создать обращение."
        )


ai_assistant = AIAssistant()

