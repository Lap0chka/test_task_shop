# E-Commerce Telegram Bot with Admin Panel and Crypto Payment Integration

This project is an internet store with both a web interface and a Telegram bot for customer interaction. It includes an admin panel integrated within the Telegram bot, allowing you to easily manage products, pricing, and discounts. Additionally, it supports cryptocurrency payments, where customers can pay with a card (via Apple Pay, Google Pay, or card number) and have payments converted to USDT using an integrated exchange.

## Features

- **E-commerce Telegram Bot**: Customers can browse, add products to the cart, and make purchases directly within Telegram.
- **Admin Panel in Telegram**: A convenient admin panel within the Telegram bot lets you manage products, prices, discounts, and inventory.
- **Crypto Payment System**: Customers can pay using cards, Apple Pay, or Google Pay, with automatic conversion to USDT via an exchange integration.
- **Web Interface**: A basic web frontend for additional customer interactions.

## Technology Stack

- **Django**: Backend framework for handling business logic, product management, and order processing.
- **Django REST Framework (DRF)**: For building REST API endpoints that facilitate bot and web communication.
- **Aiogram**: Telegram bot framework for Python that provides fast, flexible, and easy-to-use bot interaction.
- **SQLite: Database for storing products, orders, and user data.

## Code Quality and Formatting Tools

The project uses several tools for code quality and consistency:
- **Black**: For consistent code formatting.
- **isort**: To sort and organize imports.
- **Flake8**: To check code style and catch errors.
- **mypy**: To perform static type checking.

## Project Setup

### Prerequisites

- Python 3.12
- Virtualenv

### Installation

Installation Steps

1. Clone the Repository: Open your terminal and run the following commands to clone the repository and navigate to the project folder:
git clone https://github.com/Lap0chka/test_task_shop
cd test_task_shop
2. Open Project in PyCharm:
Open PyCharm and navigate to the project folder test_task_shop to open it.
PyCharm will help manage dependencies and provide tools for running the project.
3. Set Up Virtual Environment: In PyCharm, set up a Python virtual environment by going to File > Settings > Project: test_task_shop > Python Interpreter, and select Add Interpreter > Add Local Interpreter > New Environment.
4. Install Dependencies: Install the required dependencies from the requirements.txt file by running:
pip install -r requirements.txt
5. Create and Configure .env File: Create a .env file in the root of the project to store sensitive information like API keys and tokens. Add the following variables, replacing placeholder values with your actual keys and secrets.
DEBUG=True  # Enable debugging mode; set to False in production
SECRET_KEY=your_django_secret_key  # Secret key for Django application security

# Stripe configuration for crypto payment processing
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key  # Public key for Stripe API
STRIPE_SECRET_KEY=your_stripe_secret_key  # Secret key for Stripe API
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret  # Webhook secret for Stripe to handle events
STRIPE_TEST_API=True  # Set to True for testing with Stripe’s sandbox

# BitPay configuration (another crypto provider)
BITPAY_SECRET=your_bitpay_secret_key  # Secret key for BitPay API

# Telegram bot configuration
TG_BOT_TOKEN=your_telegram_bot_token  # Token for the main customer bot
TG_ADMIN_BOT_TOKEN=your_admin_telegram_bot_token  # Token for the admin management bot

# SimpleSwap configuration for USDT conversion
SIMPLE_SWAP=your_simpleswap_api_key  # API key for SimpleSwap service

# Cryptocurrency wallet address for payments
BTC_ADDRESS=your_bitcoin_wallet_address  # Bitcoin address for receiving payments
DEBUG: Enables debug mode, which provides detailed error messages. Set it to False in production for security.
SECRET_KEY: Django’s secret key used for hashing and session management. This must be unique and kept secure.
Stripe Keys:
STRIPE_PUBLISHABLE_KEY: Public key used by Stripe for client-side transactions.
STRIPE_SECRET_KEY: Secret key for authenticating requests to Stripe's API.
STRIPE_WEBHOOK_SECRET: Secret key for validating webhooks from Stripe to handle payment notifications securely.
STRIPE_TEST_API: Set to True to enable test mode for Stripe, useful for development.
BITPAY_SECRET: BitPay secret key for handling cryptocurrency transactions via BitPay, if used as an alternative to Stripe.
TG_BOT_TOKEN: Token for the main Telegram bot that customers will use to interact with the store.
TG_ADMIN_BOT_TOKEN: Token for the admin bot, which provides a management interface within Telegram.
SIMPLE_SWAP: API key for SimpleSwap, used to facilitate cryptocurrency exchange (e.g., converting fiat payments to USDT).
BTC_ADDRESS: Bitcoin address where cryptocurrency payments will be received.
6. §Run the Project: In PyCharm, open the terminal and run the following command to start the Django development server:
python manage.py runserver
The server will start, and you can view the web interface by navigating to http://127.0.0.1:8000/ in your browser.
7. Run the Telegram Bot: To start the Telegram bot, create a separate Python script or a background task in PyCharm. Run the script that initializes and listens for bot commands. Make sure the TG_BOT_TOKEN and TG_ADMIN_BOT_TOKEN are correctly configured in .env.
Additional Notes
The .env file securely stores sensitive information so it doesn’t get hard-coded into the source code.
Using PyCharm provides built-in tools to manage virtual environments, debug, and run tests, which can make development faster and more manageable.
You can customize the settings further, such as configuring a production database or setting up logging, as the project scales.
