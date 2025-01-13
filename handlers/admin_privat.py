from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_on_game_false, orm_get_user, user_quantity
from filters.filters import Admin

from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard
bot = Bot(token='7592794682:AAHzauHBKTKcWE4X9v8sSENJYp8uRNfshd4')
########################### регистрация роутера и навешивание фильтра ##################################
admin_router = Router()
admin_router.message.filter(Admin())

ADMIN_KB = get_keyboard(
    'Рассылка',
    'Очистить запись',
    'Пользователи',
    sizes=(2,),
    placeholder='Выбири действие'
)


@admin_router.message(Command('admin'))
async def admin_panel(mes: Message):
    await mes.answer('Ну здарова, если хочешь стать простым смертным - нажми /start', reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Очистить запись')
async def admin_panel(mes: Message, session: AsyncSession):
    await orm_on_game_false(session)
    await mes.answer('Запись очищена')

class Spam(StatesGroup):
    spam_text = State()
    spam_photo = State()
    choice = State()

    texts = {
        'Spam:spam_text': 'Введите текст рассылки заново',
        'Spam:spam_photo': 'Отправьте другое фото',
    }

@admin_router.message(F.text == 'Рассылка', StateFilter(None))
async def spamming(mes: types.Message, state: FSMContext):
    await mes.answer('Введите текст рассылки', reply_markup=get_keyboard(
        'Назад',
        "Отмена",
        placeholder='Введите текст рассылки',
        sizes=(2, 1)
    ))
    await state.set_state(Spam.spam_text)

@admin_router.message(StateFilter(Spam), Command("отмена"))
@admin_router.message(StateFilter(Spam), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    else:
        await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)

# Вернутся на шаг назад (на прошлое состояние)

@admin_router.message(StateFilter(Spam), F.text == "Назад")
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == Spam.spam_text:
        await state.clear()
        await message.answer("Действия отменены", reply_markup=ADMIN_KB)
        return

    previous = None
    for step in Spam.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n {Spam.texts[previous.state]}"
            )
            return
        previous = step

########################### Шаг 1 получение текста рассылки ##################################
@admin_router.message(Spam.spam_text, F.text)
async def spam_t(mes: types.Message, state: FSMContext):
    lis = len(mes.text)
    if lis >= 200:
        await mes.answer('Вы ввели слишком длинный текст')
        return
    await state.update_data(spam_text=mes.text)
    await mes.answer('Отправьте фото для рассылки')
    await state.set_state(Spam.spam_photo)

########################### Шаг 2 получение фото рассылки ##################################
@admin_router.message(Spam.spam_photo, F.photo)
async def spam_t(mes: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(spam_photo=mes.photo[-1].file_id)
    data = await state.get_data()
    await mes.answer_photo(data['spam_photo'], caption=data['spam_text'])
    await mes.answer('Рассылка будет выглядеть так:\n'
                     'Начать рассылку?', reply_markup=get_keyboard(
        'Да',
        'Нет',
        placeholder='Делаем?',
        sizes=(2, 1)
    ))
    await state.set_state(Spam.choice)

@admin_router.message(Spam.spam_photo)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото")


@admin_router.message(F.text == 'Да', Spam.choice)
async def yes(mes: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    for user in await orm_get_user(session):
        try:
            await bot.send_photo(chat_id=user, photo=data['spam_photo'], caption=data['spam_text'])
        except TelegramForbiddenError:
            pass
    await state.clear()
    await mes.answer("Рассылка окончена", reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Нет', Spam.choice)
async def yes(mes: types.Message, state: FSMContext, session: AsyncSession):
    await mes.answer('Рассылка удалена', reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(F.text == "Пользователи")
async def get_users_for_admin(mes: types.Message, session: AsyncSession):
    a = await user_quantity(session)
    await mes.answer(f'Количество пользователей: {a}')