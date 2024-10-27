from pathlib import Path

import stripe
import requests
import time
import hmac
import hashlib
from typing import Optional, Dict
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(BASE_DIR / '.env')

stripe.api_key = env('STRIPE_SECRET_KEY')


binance_api_key = 'your_binance_api_key'
binance_secret_key = 'your_binance_secret_key'
binance_base_url = 'https://api.binance.com'


def create_stripe_payment(amount: int, currency: str = 'usd') -> Optional[Dict]:
    """
    Creates a payment intent on Stripe to charge a specified amount.

    Args:
        amount (int): The amount to charge in the smallest currency unit (e.g., cents for USD).
        currency (str): The currency code (default is 'usd').

    Returns:
        Optional[Dict]: The payment intent details if successful, otherwise None.
    """
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method_types=['card']
        )
        return payment_intent
    except Exception as e:
        print(f"Error creating payment on Stripe: {e}")
        return None


def check_stripe_payment(payment_intent_id: str) -> bool:
    """
    Checks if a Stripe payment has succeeded.

    Args:
        payment_intent_id (str): The ID of the payment intent to check.

    Returns:
        bool: True if the payment was successful, False otherwise.
    """
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return payment_intent['status'] == 'succeeded'
    except Exception as e:
        print(f"Error checking payment status: {e}")
        return False


def create_binance_signature(query_string: str) -> str:
    """
    Creates a signature for Binance API requests using HMAC SHA256.

    Args:
        query_string (str): The query string to sign.

    Returns:
        str: The generated HMAC SHA256 signature.
    """
    return hmac.new(
        binance_secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def buy_crypto_binance(symbol: str = 'USDTBUSD', amount: float = 100.0) -> Optional[Dict]:
    """
    Buys USDT on Binance with a market order.

    Args:
        symbol (str): The trading pair symbol (e.g., 'USDTBUSD' for buying USDT with BUSD).
        amount (float): The amount of the base currency to spend (e.g., BUSD or USD).

    Returns:
        Optional[Dict]: The details of the purchase order if successful, otherwise None.
    """
    timestamp = int(time.time() * 1000)
    params = f"symbol={symbol}&side=BUY&type=MARKET&quoteOrderQty={amount}&timestamp={timestamp}"
    signature = create_binance_signature(params)

    headers = {
        'X-MBX-APIKEY': binance_api_key
    }

    try:
        response = requests.post(
            f"{binance_base_url}/api/v3/order",
            headers=headers,
            params=params + f"&signature={signature}"
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error purchasing USDT on Binance: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error calling Binance API: {e}")
        return None


# Example usage
# Step 1: Create a payment on Stripe
amount_to_send = 10000  # Amount in cents (10000 = $100)
stripe_payment = create_stripe_payment(amount_to_send)

if stripe_payment:
    print(f"Stripe Payment ID: {stripe_payment['id']}")

    # Step 2: Check if payment succeeded
    if check_stripe_payment(stripe_payment['id']):
        print("Payment was successful on Stripe!")

        # Step 3: Buy cryptocurrency on Binance
        crypto_purchase = buy_crypto_binance(symbol='BTCUSDT', amount=0.001)

        if crypto_purchase:
            print(f"Crypto purchase on Binance successful: {crypto_purchase}")
    else:
        print("Payment on Stripe did not complete successfully.")
else:
    print("Error creating payment on Stripe")
