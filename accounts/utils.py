import requests
from django.conf import settings

def send_sms(phone_number, code):
    url = f"https://api.kavenegar.com/v1/{settings.KAVENEGAR_API_KEY}/sms/send.json"
    data = {
        "receptor": phone_number,
        "message": f"Drip Clothing\nYour Verification Code is : {code}",

        "sender": settings.KAVENEGAR_SENDER_NUMBER
    }
    response = requests.post(url, data=data)
    return response.json()
