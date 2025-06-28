import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
BASE_URL = 'https://api.paystack.co'

headers = {
    'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
    'content-Type': 'application/json',
}

def initialize_payment(email, amount, reference):
    url = f'{BASE_URL}/transaction/initialize'
    data = {
        'email': email,
        'amount': int(amount * 100),
        'reference': reference,
        'callback_url': 'http://localhost:3000/payment-success'
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def verify_payment(reference):
    url = f'{BASE_URL}/transaction/verify/{reference}'
    response = requests.get(url, headers=headers)
    return response.json()