from aiogram import F, types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession

from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns

from database.orm_query import orm_add_user, on_db


user_private_router = Router()


USER_KB = get_keyboard(
            "Записаться",
            "Отменить запись",
            "Кто записался",
            placeholder="Что вас интересует?",
            sizes=(2, 2))


class Naming(StatesGroup):
    nick_name = State()


########################### Обработка команды старт ##################################
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession, state: FSMContext):
    usl = await on_db(session, message.from_user.id)
    if usl:
        await message.answer('Дважды в реку не войдешь... Вот тебе менюшка', reply_markup=USER_KB)
    else:
        await message.answer('Ну привет, мафиозник. Введи свой никнейм, но помни, поменять его ты уже не сможешь...')
        await state.set_state(Naming.nick_name)


@user_private_router.message(StateFilter(Naming), Naming.nick_name)
async def registration(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(nick_name=message.text)
    data = await state.get_data()
    await orm_add_user(session, user_id=message.from_user.id,
                       chat_id=message.chat.id,
                       nick_name=data['nick_name'])
    await message.answer('Ты теперь в банде 😎', reply_markup=USER_KB)
    await state.clear()
