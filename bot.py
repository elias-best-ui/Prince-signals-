import yfinance as yf
import pandas as pd
import requests
import time

# --- הגדרות אישיות ---
TOKEN = "8747380852:AAGVaECHypCmUI8Qg4n237i35P-TBMKrLr4"
CHAT_ID = "5882902045"

def send_questionnaire():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    text = (
        "👋 *ברוך הבא ל-Prince Signals!*\n\n"
        "כדי שנתחיל, איזה סוג סוחר אתה?\n"
        "1️⃣ **Day Trader** (מהיר, סיכוי גבוה)\n"
        "2️⃣ **Swing Trader** (מגמות של כמה ימים)\n"
        "3️⃣ **Long Term** (השקעות לטווח ארוך)"
    )
    keyboard = {
        "inline_keyboard": [
            [{"text": "1️⃣ Day Trader", "callback_data": "type_day"}],
            [{"text": "2️⃣ Swing Trader", "callback_data": "type_swing"}],
            [{"text": "3️⃣ Long Term", "callback_data": "type_long"}]
        ]
    }
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "reply_markup": keyboard}
    requests.post(url, json=payload)

def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url).json()
    return response.get("result", [])

def run_setup():
    print("🤖 שולח שאלון ומחכה לתשובה בטלגרם...")
    send_questionnaire()
    
    # לולאה שמחכה לתשובה למשך 2 דקות
    start_time = time.time()
    while time.time() - start_time < 120:
        updates = get_updates()
        for update in updates:
            if "callback_query" in update:
                data = update["callback_query"]["data"]
                user_choice = data.split("_")[1]
                
                # אישור קבלת התשובה
                confirm_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                requests.post(confirm_url, json={
                    "chat_id": CHAT_ID, 
                    "text": f"✅ הבחירה התקבלה! הוגדרת כ: *{user_choice}*.\nמהיום תקבל סיגנלים שמתאימים רק לך.",
                    "parse_mode": "Markdown"
                })
                print(f"✅ המשתמש בחר: {user_choice}")
                return user_choice
        time.sleep(3)
    
    print("⏰ הזמן עבר, לא התקבלה תשובה.")
    return None

if __name__ == "__main__":
    choice = run_setup()
    # כאן בהמשך נוסיף את הלוגיקה שתלויה ב-choice
