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

1. Clone the repository:
   ```bash
   git clone https://github.com/Lap0chka/test_task_shop
   cd test_task_shop
