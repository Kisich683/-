from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.types import Message
from sqlalchemy.orm import joinedload, selectinload

from database.models import User


async def orm_add_user(session: AsyncSession, user_id, chat_id, nick_name):
    tg_id = User(
        user_id=user_id,
        chat_id=chat_id,
        nick_name=nick_name,
        in_game=False
    )
    session.add(tg_id)
    await session.commit()
    return


async def on_db(session: AsyncSession, user_id):
    query = await session.scalar(select(User.user_id))
    try:
        if user_id in query:
            return True
    except TypeError:
        return False


