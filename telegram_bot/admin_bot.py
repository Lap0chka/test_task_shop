import asyncio

from aiogram.client.session import aiohttp
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from typing import Dict
from aiogram import Bot, Dispatcher, Router, types
import environ
import logging
from pathlib import Path
from aiogram.fsm.storage.memory import MemoryStorage
from django.utils.text import slugify
import requests
from urls import urls
from aiogram.fsm.context import FSMContext

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(BASE_DIR / ".env")

TOKEN = env("TG_ADMIN_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


class AdminPanel(StatesGroup):
    """State group representing different actions in the admin panel."""

    get: State = State()
    """State for retrieving goods data."""

    patch: State = State()
    """State for updating (patching) goods information."""

    delete: State = State()
    """State for deleting goods information."""

    post: State = State()
    """State for adding (posting) new goods to the catalog."""


class TelegramAdminBot:
    def __init__(self) -> None:
        self.bot = Bot(token=TOKEN)
        self.url = ""
        self.dp = Dispatcher(storage=MemoryStorage())
        self.router = Router()
        self.admin_menu = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Change")],
                [KeyboardButton(text="Delete")],
                [KeyboardButton(text="Add")],
                [KeyboardButton(text="List goods")],
            ],
            resize_keyboard=True,
        )
        self.setup_routes()
        self.dp.include_router(self.router)
        self.catalog: Dict[str, Dict[str, str]] = {}

    def setup_routes(self) -> None:
        # Admin panel
        self.router.message(Command(commands=["start"]))(self.start_command)
        self.router.message(lambda message: message.text == "List goods")(
            self.list_goods
        )
        self.router.message(lambda message: message.text == "Change")(self.edit_product)
        self.router.message(lambda message: message.text == "Delete")(
            self.delete_product
        )
        self.router.message(lambda message: message.text == "Add")(self.add_product)

        self.router.message.register(self.find_goods, AdminPanel.get)
        self.router.message.register(self.send_patch, AdminPanel.patch)
        self.router.message.register(self.send_delete, AdminPanel.delete)
        self.router.message.register(self.send_post, AdminPanel.post)

    async def start_command(self, message: types.Message) -> None:
        """Handles the /start command by displaying a welcome message and catalog."""
        await message.answer(
            "Hello! I am your shop bot. Choose a command: Our goods Here",
            reply_markup=self.admin_menu,
        )

    async def run(self) -> None:
        """Start bot"""
        await self.dp.start_polling(self.bot)

    async def list_goods(
            self, message: types.Message, url: str = urls["products"]
    ) -> None:
        """Requests the catalog from the API and displays it to the user."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    ngrok_url = urls["ngrok_url"]
                    for index, item in enumerate(data, 1):
                        try:
                            await message.answer(
                                f"{index}. {item['title']} - {item['price']} USD"
                            )
                            image_url = item["image"].replace(
                                "http://127.0.0.1:4421", ngrok_url
                            )
                            await message.answer_photo(photo=image_url)
                            self.catalog[item["title"]] = item

                        except Exception as e:
                            await message.answer(
                                f"Ошибка при обработке {index}-го элемента: {e}"
                            )

                else:
                    await message.answer(
                        "Failed to fetch the product catalog. Please try again later."
                    )

    async def edit_product(self, message: types.Message, state: FSMContext) -> None:
        """Prompts the admin to enter the product name for editing."""
        if not self.catalog:
            await self.list_goods(message)

        await message.answer("Enter the name of the product you want to edit:")
        await state.set_state(AdminPanel.get)

    async def find_goods(self, message: types.Message, state: FSMContext) -> None:
        """Finds a product by name and prepares for patching."""
        name = message.text
        if not self.catalog:
            await self.list_goods(message)
            return
        product_id = self.catalog[name]["id"]
        self.url = f"{urls['products']}{product_id}/"
        await self.list_goods(message, self.url)
        await state.clear()
        await message.answer(
            'Specify the field to update (e.g., title="Nike Air Max").'
        )
        await state.set_state(AdminPanel.patch)

    async def send_patch(self, message: types.Message, state: FSMContext) -> None:
        """Sends a patch request to update product information."""
        if not message.text:
            await message.answer(
                "Something went wrong return to the main menu.",
                reply_markup=self.admin_menu,
            )
            return
        name, value = message.text.split("=")
        data = {name.strip(): value.strip()}
        response = requests.patch(self.url, json=data)
        if response.status_code == 200:
            await message.answer("Product updated successfully.")
            await state.clear()
        else:
            await message.answer("An error occurred while updating the product.")

    async def delete_product(self, message: types.Message, state: FSMContext) -> None:
        """Prompts the admin to enter the product name for deletion."""
        if not self.catalog:
            await self.list_goods(message)
        await message.answer("Enter the name of the product you want to delete:")
        await state.set_state(AdminPanel.delete)

    async def send_delete(self, message: types.Message, state: FSMContext) -> None:
        """Sends a delete request for the specified product."""
        if not message.text:
            await message.answer(
                "Something went wrong return to the main menu.",
                reply_markup=self.admin_menu,
            )
            return
        name = message.text
        product_id = self.catalog[name]["id"]
        self.url = f"{urls['products']}{product_id}/"
        response = requests.delete(self.url)
        if response.status_code == 204:
            await message.answer("Product deleted successfully.")
            await state.clear()
        else:
            await message.answer("An error occurred while deleting the product.")

    async def add_product(self, message: types.Message, state: FSMContext) -> None:
        """Prompts the admin to enter details for a new product."""
        await message.answer("Enter product details (e.g., title=Chanel price=999).")
        await state.set_state(AdminPanel.post)

    async def send_post(self, message: types.Message, state: FSMContext) -> None:
        """Sends a post request to add a new product to the catalog."""
        if not message.text:
            await message.answer(
                "Something went wrong return to the main menu.",
                reply_markup=self.admin_menu,
            )
            return
        name, price = message.text.split(" ")
        title = name.split("=")[-1]
        price = float(price.split("=")[-1])
        data = {"title": title, "slug": slugify(title), "price": price, "category": 2}
        response = requests.post(urls["products"], json=data)
        if response.status_code == 201:
            await message.answer("New product added successfully.")
            await state.clear()
        else:
            await message.answer("An error occurred while adding the product.")


if __name__ == "__main__":
    telegram_bot = TelegramAdminBot()
    asyncio.run(telegram_bot.run())
