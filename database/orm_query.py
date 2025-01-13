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
    query = select(User.user_id)
    res = await session.execute(query)
    try:
        if user_id in res.scalars().all():
            return True
    except TypeError:
        return False


async def orm_go_game(session: AsyncSession, data: dict, user_id):
    query = update(User).where(User.user_id == user_id).values(
        come_time=data['come_time'],
        leave_time=data["leave_time"],
        in_game=True
    )
    await session.execute(query)
    await session.commit()


async def orm_users_in_game(session: AsyncSession):
    query = select(User).where(User.in_game == True)
    res = await session.execute(query)
    a = []
    count = 1
    for i in res.scalars().all():
        a += f'{count}. {i.nick_name} c {i.come_time} до {i.leave_time}\n'
        count += 1
    return ''.join(a)


async def orm_cancel(session: AsyncSession, user_id):
    query = update(User).where(User.user_id == user_id).values(
        in_game=False
    )
    await session.execute(query)
    await session.commit()


async def orm_on_game_false(session: AsyncSession):
    query = update(User).values(in_game=False)
    await session.execute(query)
    await session.commit()

async def orm_get_user(session: AsyncSession):
    query = select(User.chat_id)
    result = await session.execute(query)
    return result.scalars().all()


async def user_quantity(session: AsyncSession):
    query = select(User.user_id)
    result = await session.execute(query)
    return len(result.scalars().all())

