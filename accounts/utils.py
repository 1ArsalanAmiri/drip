import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_sms(phone_number, code, test_mode=False):
    if test_mode or settings.DEBUG:
        logger.info(f"[TEST MODE] OTP for {phone_number}: {code}")
        return {"status": "ok", "code": code}
    api_key = getattr(settings, "KAVENEGAR_API_KEY", None)
    sender = getattr(settings, "KAVENEGAR_SENDER_NUMBER", None)
    if not api_key or not sender:
        logger.error("Kavenegar config missing")
        return {"status": "error", "message": "SMS not sent"}
    try:
        resp = requests.post(f"https://api.kavenegar.com/v1/{api_key}/sms/send.json",
                             data={"receptor": phone_number, "message": f"OTP: {code}", "sender": sender},
                             timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.exception("Kavenegar request failed")
        return {"status": "error", "message": str(e)}