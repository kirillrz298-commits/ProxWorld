import aiosqlite
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "bot_database.sqlite3"
logger = logging.getLogger(__name__)

async def init_db():
    """Инициализация базы данных SQLite с необходимыми таблицами."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                player_nick TEXT,
                topic TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                operator_id INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP DEFAULT NULL
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ticket_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                sender_type TEXT NOT NULL, -- 'user', 'operator', 'ai', 'system'
                sender_name TEXT,
                text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
            )
        """)
        
        await db.commit()
    logger.info("База данных успешно инициализирована.")


async def register_or_update_user(user_id: int, username: Optional[str], full_name: str, role: str = "user") -> None:
    """Регистрация или обновление пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, full_name, role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
        """, (user_id, username, full_name, role))
        await db.commit()


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить пользователя по Telegram ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def is_operator_or_admin(user_id: int, admin_ids: List[int]) -> bool:
    """Проверка, является ли пользователь оператором или админом."""
    if user_id in admin_ids:
        return True
    user = await get_user(user_id)
    if user and user.get("role") in ("operator", "admin"):
        return True
    return False


async def get_operators() -> List[Dict[str, Any]]:
    """Получить список всех операторов."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE role IN ('operator', 'admin') ORDER BY role DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def set_user_role(user_id: int, role: str) -> bool:
    """Изменить роль пользователя (operator, user, admin)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
        await db.commit()
        return cursor.rowcount > 0


async def create_ticket(user_id: int, player_nick: str, topic: str, initial_text: str) -> int:
    """Создать новый тикет и сохранить первое сообщение."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO tickets (user_id, player_nick, topic, status)
            VALUES (?, ?, ?, 'open')
        """, (user_id, player_nick, topic))
        ticket_id = cursor.lastrowid
        
        await db.execute("""
            INSERT INTO ticket_messages (ticket_id, sender_id, sender_type, sender_name, text)
            VALUES (?, ?, 'user', ?, ?)
        """, (ticket_id, user_id, player_nick or "Игрок", initial_text))
        
        await db.commit()
        return ticket_id


async def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    """Получить тикет по ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_active_ticket_by_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Получить текущий открытый тикет пользователя, если есть."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM tickets 
            WHERE user_id = ? AND status IN ('open', 'in_progress')
            ORDER BY id DESC LIMIT 1
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_tickets(status: Optional[str] = None, limit: int = 15, offset: int = 0) -> List[Dict[str, Any]]:
    """Получить список тикетов с фильтром по статусу и пагинацией."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if status:
            query = "SELECT * FROM tickets WHERE status = ? ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (status, limit, offset)
        else:
            query = "SELECT * FROM tickets ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (limit, offset)
            
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def assign_ticket_operator(ticket_id: int, operator_id: int) -> bool:
    """Назначить оператора на тикет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE tickets 
            SET operator_id = ?, status = 'in_progress'
            WHERE id = ?
        """, (operator_id, ticket_id))
        await db.commit()
        return True


async def close_ticket(ticket_id: int) -> bool:
    """Закрыть тикет."""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = await db.execute("""
            UPDATE tickets 
            SET status = 'closed', closed_at = ?
            WHERE id = ? AND status != 'closed'
        """, (now, ticket_id))
        await db.commit()
        return cursor.rowcount > 0


async def add_ticket_message(ticket_id: int, sender_id: int, sender_type: str, sender_name: str, text: str) -> int:
    """Добавить сообщение в переписку по тикету."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO ticket_messages (ticket_id, sender_id, sender_type, sender_name, text)
            VALUES (?, ?, ?, ?, ?)
        """, (ticket_id, sender_id, sender_type, sender_name, text))
        await db.commit()
        return cursor.lastrowid


async def get_ticket_messages(ticket_id: int) -> List[Dict[str, Any]]:
    """Получить все сообщения по тикету."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM ticket_messages 
            WHERE ticket_id = ? 
            ORDER BY id ASC
        """, (ticket_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_stats() -> Dict[str, int]:
    """Получить сводную статистику по тикетам и пользователям."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Всего тикетов
        async with db.execute("SELECT COUNT(*) FROM tickets") as c:
            total_tickets = (await c.fetchone())[0]
            
        # Открытых / в работе
        async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'") as c:
            open_tickets = (await c.fetchone())[0]
            
        async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'in_progress'") as c:
            in_progress_tickets = (await c.fetchone())[0]
            
        # Закрытых
        async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'") as c:
            closed_tickets = (await c.fetchone())[0]
            
        # Всего пользователей
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total_users = (await c.fetchone())[0]
            
        # Количество операторов
        async with db.execute("SELECT COUNT(*) FROM users WHERE role IN ('operator', 'admin')") as c:
            total_operators = (await c.fetchone())[0]
            
        # Тикетов за сегодня
        today_date = datetime.now().strftime("%Y-%m-%d")
        async with db.execute("SELECT COUNT(*) FROM tickets WHERE created_at LIKE ?", (f"{today_date}%",)) as c:
            tickets_today = (await c.fetchone())[0]

        return {
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress_tickets,
            "closed_tickets": closed_tickets,
            "total_users": total_users,
            "total_operators": total_operators,
            "tickets_today": tickets_today
        }

