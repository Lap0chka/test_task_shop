import asyncio
import logging
from pathlib import Path
from typing import Dict

import aiohttp
import environ
import requests
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from urls import urls

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(BASE_DIR / ".env")

TOKEN = env("TG_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)


class OrderStates(StatesGroup):
    """State group representing the order process flow for a customer."""

    make_order: State = State()
    """State for making an order and selecting items."""

    shipping_address: State = State()
    """State for providing shipping address information."""


class TelegramBot:
    """Telegram bot with product management and order processing functionality."""

    def __init__(self) -> None:
        """Initializes the bot, dispatcher, router, and main/admin menus."""
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.router = Router()
        self.catalog_data: Dict[str, Dict] = {}
        self.menu = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Catalog")],
                [KeyboardButton(text="Make Order")],
            ],
            resize_keyboard=True,
        )
        self.cart = []
        self.setup_routes()

    def setup_routes(self) -> None:
        """Sets up command and message routes for the bot's functionalities."""
        self.router.message(Command(commands=["start"]))(self.start_command)
        self.router.message(lambda message: message.text == "Catalog")(self.get_request)
        self.router.message(lambda message: message.text == "Make Order")(
            self.make_order
        )
        self.router.message.register(self.process_order_input, OrderStates.make_order)
        self.router.message.register(
            self.process_shipping_input, OrderStates.shipping_address
        )

    async def start_command(self, message: types.Message) -> None:
        """Handles the /start command by displaying a welcome message and catalog."""
        await message.answer(
            "Hello! I am your shop bot. Choose a command: Our goods Here",
            reply_markup=self.menu,
        )
        await self.get_request(message)

    async def back_to_main_menu(self, message: types.Message) -> None:
        """Returns the user to the main menu."""
        await message.answer("Returning to the main menu.", reply_markup=self.menu)

    async def get_request(
            self, message: types.Message, url: str = urls["products"]
    ) -> None:
        """Requests the product catalog from the API and displays it to the user."""
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
                            self.catalog_data[item["title"]] = item

                        except Exception as e:
                            await message.answer(
                                f"Ошибка при обработке {index}-го элемента: {e}"
                            )

                else:
                    await message.answer(
                        "Failed to fetch the product catalog. Please try again later."
                    )

    async def make_order(self, message: types.Message, state: FSMContext) -> None:
        """
        Initiates the order creation process, prompting the user for product name and quantity.
        """
        if not self.catalog_data:
            await self.get_request(message)

        await message.answer(
            "Please enter the product name and quantity (e.g., Product 1 - 2 pcs)"
        )
        await state.set_state(OrderStates.make_order)

    async def process_order_input(
            self, message: types.Message, state: FSMContext
    ) -> None:
        """
        Processes user input for creating an order, calculating the total price.
        """
        try:
            if not message.text:
                await message.answer(
                    "Something went wrong return to the main menu.",
                    reply_markup=self.menu,
                )
                return
            product_name, quantity = message.text.split(" - ")

            if product_name in self.catalog_data:
                product_data = self.catalog_data[product_name]
                total_price = float(product_data["price"]) * int(quantity)
                price = float(product_data["price"])
                self.cart = [
                    {
                        "product_name": product_name,
                        "price": price,
                        "quantity": int(quantity),
                    }
                ]
                await message.answer(
                    f"You ordered {quantity} pcs of {product_name}.\n"
                    f"Total price: {total_price} USD.\n"
                )

                await self.get_shipping_address(message, state)
            else:
                await message.answer(
                    f"The product '{product_name}' is not available in our catalog. "
                    f"Please try again."
                )
        except ValueError:
            await message.answer(
                "Invalid input format. Please use the format: "
                "Product name - quantity (e.g., Product 1 - 2 pcs)."
            )

    async def get_shipping_address(
            self, message: types.Message, state: FSMContext
    ) -> None:
        """
        Prompts the user to enter their shipping address in a specific format.
        """
        await message.answer(
            "Please enter the shipping address:\n"
            "You should write like example:\n"
            "John Smith, my_email@gmail.com, Gullweg, 18, Berlin, Germany"
        )
        await state.set_state(OrderStates.shipping_address)

    async def process_shipping_input(
            self, message: types.Message, state: FSMContext
    ) -> None:
        """
        Processes the user's shipping address input and sends an order to the API for processing.
        """

        try:
            if not message.text:
                await message.answer(
                    "Something went wrong return to the main menu.",
                    reply_markup=self.menu,
                )
                return
            address_parts = message.text.split(", ")
            if len(address_parts) < 6:
                await message.answer(
                    "Please provide the address in the correct format."
                )
                return
            full_name, email, street_address, apartment_address, city, country = (
                address_parts
            )

            data = {
                "shipping_address": {
                    "full_name": full_name,
                    "email": email,
                    "street_address": street_address,
                    "apartment_address": apartment_address,
                    "city": city,
                    "country": country,
                },
                "cart_items": self.cart,
            }
            response = await asyncio.to_thread(
                requests.post, urls["checkout"], json=data
            )

            if response.status_code == 201:
                response_data = response.json()
                checkout_url = response_data.get("checkout_url")
                checkout_url_api = response_data.get("api_test_url")
                await message.answer(
                    f"Your order has been processed successfully! "
                    f"Complete your payment with stripe: {checkout_url}\n"
                    f"-----------------------------------\n"
                    f"Complete your payment with test api: {checkout_url_api}"
                )
            else:
                await message.answer(
                    "There was an error processing your order. Please try again later."
                )
        except Exception:
            await message.answer("An error occurred while processing your order.")
        await state.clear()

    async def run(self) -> None:
        """
        Starts the bot and its handlers, initiating polling for new messages.
        """
        self.dp.include_router(self.router)
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    telegram_bot = TelegramBot()
    asyncio.run(telegram_bot.run())
