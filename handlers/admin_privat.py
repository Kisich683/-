from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from filters.filters import Admin

from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard

bot = Bot(token='7750297853:AAGmrKJjS5o-r_G0FaH0XtSNbpOVS6N-ocE')
########################### регистрация роутера и навешивание фильтра ##################################
admin_router = Router()
admin_router.message.filter(Admin())

#ADMIN_KB
@admin_router.message(Command('admin'))
async def admin_panel(mes: Message):
    await mes.answer('Ну здарова, если хочешь стать простым смертным - нажми /start')