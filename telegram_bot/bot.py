from typing import Dict

import aiohttp
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.utils.text import slugify
from urls import urls

TOKEN = '7878094227:AAFrz_Pjo1ogi8lLoJUc_Gm0533cz8WbWcQ'

logging.basicConfig(level=logging.INFO)

from aiogram.fsm.state import State, StatesGroup

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
                [KeyboardButton(text='Catalog')],
                [KeyboardButton(text='Make Order')],
                [KeyboardButton(text='Admin')]
            ],
            resize_keyboard=True
        )
        self.admin_menu = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Change')],
                [KeyboardButton(text='Delete')],
                [KeyboardButton(text='Add')],
                [KeyboardButton(text='Back')]
            ],
            resize_keyboard=True
        )
        self.setup_routes()

    def setup_routes(self) -> None:
        """Sets up command and message routes for the bot's functionalities."""
        self.router.message(Command(commands=['start']))(self.start_command)
        self.router.message(lambda message: message.text == 'Catalog')(self.get_request)
        self.router.message(lambda message: message.text == 'Make Order')(self.make_order)
        self.router.message.register(self.process_order_input, OrderStates.make_order)
        self.router.message.register(self.process_shipping_input, OrderStates.shipping_address)

        # Admin panel
        self.router.message(lambda message: message.text == 'Admin')(self.admin_interface)
        self.router.message(lambda message: message.text == 'Change')(self.edit_product)
        self.router.message(lambda message: message.text == 'Delete')(self.delete_product)
        self.router.message(lambda message: message.text == 'Add')(self.add_product)
        self.router.message(lambda message: message.text == 'Back')(self.back_to_main_menu)
        self.router.message.register(self.find_goods, AdminPanel.get_goods)
        self.router.message.register(self.send_patch, AdminPanel.patch)
        self.router.message.register(self.send_delete, AdminPanel.delete)
        self.router.message.register(self.send_post, AdminPanel.post)

    async def start_command(self, message: types.Message) -> None:
        """Handles the /start command by displaying a welcome message and catalog.
        """
        await message.answer("Hello! I am your shop bot. Choose a command: Our goods Here", reply_markup=self.menu)
        await self.get_request(message)

    async def admin_interface(self, message: types.Message) -> None:
        """Displays the admin menu with options for managing products.
        """
        await message.answer("You came to the admin panel. Choose what you want to do.", reply_markup=self.admin_menu)

    async def edit_product(self, message: types.Message, state: FSMContext) -> None:
        """Prompts the admin to enter the product name for editing.
        """
        if not self.catalog_data:
            await self.get_request(message)
        await message.answer("Enter the name of the product you want to edit:")
        await state.set_state(AdminPanel.get_goods)

    async def find_goods(self, message: types.Message, state: FSMContext) -> None:
        """Finds a product by name and prepares for patching.
        """
        name = message.text
        if name not in self.catalog_data:
            await message.answer("This product is not available.")
            return
        product_id = self.catalog_data[name]['id']
        self.url = f"{urls['products']}{product_id}/"
        await self.get_request(message, self.url)
        await state.clear()
        await message.answer('Specify the field to update (e.g., title="Nike Air Max").')
        await state.set_state(AdminPanel.patch)

    async def send_patch(self, message: types.Message, state: FSMContext) -> None:
        """Sends a patch request to update product information.
        """
        name, value = message.text.split('=')
        data = {name.strip(): value.strip()}
        response = requests.patch(self.url, json=data)
        if response.status_code == 200:
            await message.answer("Product updated successfully.")
            await state.clear()
        else:
            await message.answer("An error occurred while updating the product.")

    async def delete_product(self, message: types.Message, state: FSMContext) -> None:
        """Prompts the admin to enter the product name for deletion.
        """
        if not self.catalog_data:
            await self.get_request(message)
        await message.answer("Enter the name of the product you want to delete:")
        await state.set_state(AdminPanel.delete)

    async def send_delete(self, message: types.Message, state: FSMContext) -> None:
        """Sends a delete request for the specified product.
        """
        name = message.text
        product_id = self.catalog_data[name]['id']
        self.url = f"{urls['products']}{product_id}/"
        response = requests.delete(self.url)
        if response.status_code == 204:
            await message.answer("Product deleted successfully.")
            await state.clear()
        else:
            await message.answer("An error occurred while deleting the product.")

    async def add_product(self, message: types.Message, state: FSMContext) -> None:
        """Prompts the admin to enter details for a new product.
        """
        await message.answer("Enter product details (e.g., title=Chanel price=999).")
        await state.set_state(AdminPanel.post)

    async def send_post(self, message: types.Message, state: FSMContext) -> None:
        """Sends a post request to add a new product to the catalog.
        """
        name, price = message.text.split(' ')
        title = name.split('=')[-1]
        price = float(price.split('=')[-1])
        data = {
            "title": title,
            "slug": slugify(title),
            "price": price,
            "category": 2
        }
        response = requests.post(urls['products'], json=data)
        if response.status_code == 201:
            await message.answer("New product added successfully.")
            await state.clear()
        else:
            await message.answer("An error occurred while adding the product.")

    async def back_to_main_menu(self, message: types.Message) -> None:
        """Returns the user to the main menu.
        """
        await message.answer("Returning to the main menu.", reply_markup=self.menu)

    async def get_request(self, message: types.Message, url: str = urls['products']) -> None:
        """Fetches and displays the product catalog."""

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        catalog = "\n".join(
                            [f"{index}. {item['title']} - {item['price']} USD" for index, item in enumerate(data, 1)]
                        )
                        await message.answer(f"Our product catalog:\n{catalog}")
                        self.catalog_data = {item['title']: item for item in data}
                    else:
                        await message.answer(f"Product:\n{data}")
                else:
                    await message.answer("Failed to fetch the product catalog. Please try again later.")

    async def back_to_main_menu(self, message: types.Message) -> None:
        """Sends a message to the user returning them to the main menu."""
        await message.answer("Вы вернулись в главное меню.", reply_markup=self.menu)

    async def get_request(self, message: types.Message, url: str = urls['products']) -> None:
        """ Requests the product catalog from the API and displays it to the user. """

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        catalog = "\n".join([f"{index}. {item['title']} - {item['price']} USD"
                                             for index, item in enumerate(data, 1)])
                        await message.answer(f"Our product catalog:\n{catalog}")
                        self.catalog_data = {item['title']: item for item in data}
                    else:
                        await message.answer(f"Product:\n{data}")
                else:
                    await message.answer("Failed to fetch the product catalog. Please try again later.")

    async def make_order(self, message: types.Message, state: FSMContext) -> None:
        """
        Initiates the order creation process, prompting the user for product name and quantity.
        """
        if not self.catalog_data:
            await message.answer("Please view the catalog first by typing 'Catalog'.")
            return

        await message.answer("Please enter the product name and quantity (e.g., Product 1 - 2 pcs)")
        await state.set_state(OrderStates.make_order)

    async def process_order_input(self, message: types.Message, state: FSMContext) -> None:
        """
        Processes user input for creating an order, calculating the total price.
        """
        try:
            product_name, quantity = message.text.split(' - ')
            quantity = int(quantity.split(' ')[0])
            if product_name in self.catalog_data:
                product = self.catalog_data[product_name]
                total_price = product['price'] * quantity
                self.cart = [{
                    'product_name': product_name,
                    'price': float(product['price']),
                    'quantity': int(quantity)
                }]
                await message.answer(
                    f"You ordered {quantity} pcs of {product_name}.\n"
                    f"Total price: {total_price} USD.\n"
                )

                await self.get_shipping_address(message, state)
            else:
                await message.answer(f"The product '{product_name}' is not available in our catalog. Please try again.")
        except ValueError:
            await message.answer(
                "Invalid input format. Please use the format: Product name - quantity (e.g., Product 1 - 2 pcs).")

    async def get_shipping_address(self, message: types.Message, state: FSMContext) -> None:
        """
        Prompts the user to enter their shipping address in a specific format.
        """
        await message.answer("Please enter the shipping address:\n"
                             "You should write like example:\n"
                             "John Smith, my_email@gmail.com, Gullweg, 18, Berlin, Germany")
        await state.set_state(OrderStates.shipping_address)

    async def process_shipping_input(self, message: types.Message, state: FSMContext) -> None:
        """
        Processes the user's shipping address input and sends an order to the API for processing.
        """
        try:
            address_parts = message.text.split(', ')
            full_name, email, street_address, apartment_address, city, country = address_parts

            data = {
                "shipping_address": {
                    "full_name": full_name,
                    "email": email,
                    "street_address": street_address,
                    "apartment_address": apartment_address,
                    "city": city,
                    "country": country,
                },
                "cart_items": self.cart
            }
            response = await asyncio.to_thread(requests.post, urls['checkout'], json=data)
            if response.status_code == 201:
                response_data = response.json()
                checkout_url = response_data.get('checkout_url')
                await message.answer(
                    f"Your order has been processed successfully! Complete your payment here: {checkout_url}")
            else:
                await message.answer("There was an error processing your order. Please try again later.")
        except requests.exceptions.JSONDecodeError as e:
            await message.answer("An error occurred while processing your order.")
        except Exception as e:
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
