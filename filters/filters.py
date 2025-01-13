from aiogram.filters import Filter
from aiogram import Bot, types


class Admin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message) -> bool:
        admins = [333502700, 6572924310]
        return message.from_user.id in admins


