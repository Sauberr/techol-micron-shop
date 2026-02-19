import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"👋 Hello, <b>{message.from_user.first_name}</b>!\n\n"
        f"🛒 Welcome to <b>Micron Hardware Store</b> bot.\n\n"
        f"This bot sends order notifications to the store administrator."
    )

