import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
    ADMIN_IDS: List[int] = None
    SUPPORT_CHAT_ID: int = int(os.getenv("SUPPORT_CHAT_ID", "0"))
    
    # AI Assistant
    AI_API_KEY: str = os.getenv("AI_API_KEY", "").strip()
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").strip()
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini").strip()
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "True").lower() in ("true", "1", "yes")
    
    # Server Details
    SERVER_NAME: str = os.getenv("SERVER_NAME", "ProxGrief")
    SERVER_IP: str = os.getenv("SERVER_IP", "mc.proxgrief.ru")
    SERVER_PORT: str = os.getenv("SERVER_PORT", "25565")
    SERVER_VERSIONS: str = os.getenv("SERVER_VERSIONS", "1.16.5 - 1.20.4")
    SERVER_SITE: str = os.getenv("SERVER_SITE", "https://proxgrief.ru")
    SERVER_DONATE_URL: str = os.getenv("SERVER_DONATE_URL", "https://proxgrief.ru/donate")
    SERVER_RULES_URL: str = os.getenv("SERVER_RULES_URL", "https://proxgrief.ru/rules")
    SERVER_VK_URL: str = os.getenv("SERVER_VK_URL", "https://vk.com/proxgrief")
    SERVER_DISCORD_URL: str = os.getenv("SERVER_DISCORD_URL", "https://discord.gg/proxgrief")

    def __post_init__(self):
        raw_admins = os.getenv("ADMIN_IDS", "")
        admins = []
        for admin_id in raw_admins.split(","):
            admin_id = admin_id.strip()
            if admin_id.isdigit():
                admins.append(int(admin_id))
        self.ADMIN_IDS = admins

config = Config()

