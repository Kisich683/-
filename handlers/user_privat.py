from aiogram import F, types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns

from database.orm_query import orm_add_user, on_db, orm_go_game, orm_users_in_game, orm_cancel


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
async def start_cmd(message: Message, session: AsyncSession, state: FSMContext):
    usl = await on_db(session, message.from_user.id)
    print(usl)
    if usl:
        await message.answer('Дважды в реку не войдешь... Вот тебе менюшка', reply_markup=USER_KB)
    else:
        await message.answer('Ну привет, мафиозник. Введи свой никнейм, но помни, поменять его ты уже не сможешь...')
        await state.set_state(Naming.nick_name)


@user_private_router.message(StateFilter(Naming), Naming.nick_name)
async def registration(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(nick_name=message.text)
    data = await state.get_data()
    await orm_add_user(session, user_id=message.from_user.id,
                       chat_id=message.chat.id,
                       nick_name=data['nick_name'])
    await message.answer('Ты теперь в банде 😎', reply_markup=USER_KB)
    await state.clear()


######################## Запись на игру

class GoGame(StatesGroup):
    come_time = State()
    leave_time = State()

@user_private_router.message(F.text == 'Записаться', StateFilter(None))
async def go_to_play(mes: Message, state: FSMContext):
    await state.set_state(GoGame.come_time)
    await mes.answer('Когда придешь?', reply_markup=get_callback_btns(btns={
        '16:00': 'come_16:00',
        '16:30': 'come_16 30',
        '17:00': 'come_17:00',
        '17:30': 'come_17:30',
        '18:00': 'come_18:00',
        '18:30': 'come_18:30',
        '19:00': 'come_19:00',
        '19:30': 'come_19:30',
        '20:00': 'come_20:00',
        'С начала': 'come_начала'
    },
    sizes=(3, 3, 3, 1)))

@user_private_router.callback_query(GoGame.come_time, F.data.startswith("come_"))
async def change_come_callback(callback: types.CallbackQuery, state: FSMContext):
    come_time = callback.data.split("_")[-1]

    await state.update_data(come_time=come_time)

    await callback.answer()
    await callback.message.edit_text(
        "Во сколько уйдешь?", reply_markup=get_callback_btns(btns={
            '18:00': 'leave_18:00',
            '18:30': 'leave_18 30',
            '19:00': 'leave_19:00',
            '19:30': 'leave_19:30',
            '20:00': 'leave_20:00',
            '20:30': 'leave_20:30',
            'До конца': 'leave_конца'
            },
        sizes=(3, 3, 1)))

    await state.set_state(GoGame.leave_time)


@user_private_router.callback_query(GoGame.leave_time, F.data.startswith("leave_"))
async def change_leave_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    leave_time = callback.data.split("_")[-1]

    await state.update_data(leave_time=leave_time)
    data = await state.get_data()
    await orm_go_game(session=session, data=data, user_id=callback.from_user.id)

    await callback.answer()
    await callback.message.edit_text("Ты записан на игру")
    await state.clear()



@user_private_router.message(F.text == 'Кто записался')
async def users_in_game(mes: Message, session: AsyncSession):
    users = await orm_users_in_game(session=session)
    await mes.answer(f'{users}')


@user_private_router.message(F.text == 'Отменить запись')
async def cancel(mes: Message, session: AsyncSession):
    await orm_cancel(session=session, user_id=mes.from_user.id)
    await mes.answer(f'{mes}')

