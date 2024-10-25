import os

import aiohttp
import django
import asyncio
import logging

import requests
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_URL = 'http://127.0.0.1:4421/v1/api/'
GET_PRODUCT = f'{API_URL}products/'
CHECKOUT = f'{API_URL}chekout/'
TOKEN = '7878094227:AAFrz_Pjo1ogi8lLoJUc_Gm0533cz8WbWcQ'

logging.basicConfig(level=logging.INFO)


class OrderStates(StatesGroup):
    make_order = State()
    shipping_address = State()


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.router = Router()
        self.catalog_data = {}
        self.menu = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text='Catalog')],
                [KeyboardButton(text='Make Order')]
            ],
            resize_keyboard=True
        )
        self.setup_routes()

    def setup_routes(self):
        """Настраивает маршруты для команд."""
        self.router.message(Command(commands=['start']))(self.start_command)
        self.router.message(lambda message: message.text == 'Catalog')(self.show_catalog)
        self.router.message(lambda message: message.text == 'Make Order')(self.make_order)
        self.router.message.register(self.process_order_input, OrderStates.make_order)
        self.router.message.register(self.process_shipping_input, OrderStates.shipping_address)

    async def start_command(self, message: types.Message):
        """Обрабатывает команду /start."""
        await message.answer("Hello! I am your shop bot. Choose a command:", reply_markup=self.menu)

    async def show_catalog(self, message: types.Message):
        """Показывает каталог товаров, запрашивая их через API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(GET_PRODUCT) as response:
                if response.status == 200:
                    data = await response.json()
                    catalog = "\n".join([f"{item['title']} - {item['price']} USD" for item in data])
                    await message.answer(f"Our product catalog:\n{catalog}")

                    self.catalog_data = {item['title']: item for item in data}
                else:
                    await message.answer("Failed to fetch the product catalog. Please try again later.")

    async def make_order(self, message: types.Message, state: FSMContext):
        """Обрабатывает запрос на создание заказа и ждет ввода пользователя."""
        if not self.catalog_data:
            await message.answer("Please view the catalog first by typing 'Catalog'.")
            return

        await message.answer("Please enter the product name and quantity (e.g., Product 1 - 2 pcs)")
        await state.set_state(OrderStates.make_order)

    async def process_order_input(self, message: types.Message, state: FSMContext):
        """Обрабатывает ввод пользователя для создания заказа."""
        try:
            product_name, quantity = message.text.split(' - ')
            quantity = int(quantity.split(' ')[0])
            if product_name in self.catalog_data:
                product = self.catalog_data[product_name]
                total_price = product['price'] * quantity
                self.cart =  [{
                        'product_name': product_name,
                        'price': float(product['price']),
                        'quantity': int(quantity)
                    },
                ]
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

    async def get_shipping_address(self, message: types.Message, state: FSMContext):
        await message.answer("Please enter the shipping address:\n"
                             "You shloud write like example\n"
                             "John Smith, my_email@gmail.com, Gullweg, 18, Berlin, Germany")
        await state.set_state(OrderStates.shipping_address)

    async def process_shipping_input(self, message: types.Message, state: FSMContext):
        """Обрабатывает ввод адреса доставки."""
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
            print(data)
            # Отправляем POST-запрос в API
            response = await asyncio.to_thread(requests.post, CHECKOUT, json=data)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")

            # Проверяем статус ответа перед попыткой преобразовать его в JSON
            if response.status_code == 201:
                response_data = response.json()
                checkout_url = response_data.get('checkout_url')
                await message.answer(
                    f"Your order has been processed successfully! Complete your payment here: {checkout_url}")
            else:
                await message.answer(
                    "There was an error processing your order. Please try again later.")
                # Отладка: выводим текст ответа в случае ошибки
                print(f"Error response content: {response.text}")
        except requests.exceptions.JSONDecodeError as e:
            await message.answer("An error occurred while processing your order.")
            print(f"JSON decode error: {e}")
            print(f"Response text that caused the error: {response.text}")
        except Exception as e:
            await message.answer("An error occurred while processing your order.")
            print(f"Unexpected error: {e}")

            # Очищаем состояние после завершения
        await state.clear()

    async def run(self):
        """Запускает бота и его обработчики."""
        self.dp.include_router(self.router)
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dp.start_polling(self.bot)


# Запуск бота
if __name__ == "__main__":
    telegram_bot = TelegramBot()
    asyncio.run(telegram_bot.run())
