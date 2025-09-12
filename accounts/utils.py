import requests
from django.conf import settings

def send_sms(phone_number, code):
    if not hasattr(settings, "KAVENEGAR_API_KEY") or not hasattr(settings, "KAVENEGAR_SENDER_NUMBER"):
        raise ValueError("Kavenegar API key or sender number not set")
    url = f"https://api.kavenegar.com/v1/{settings.KAVENEGAR_API_KEY}/sms/send.json"
    data = {"receptor": phone_number, "message": f"Your code: {code}", "sender": settings.KAVENEGAR_SENDER_NUMBER}
    try:
        response = requests.post(url, data=data)
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
