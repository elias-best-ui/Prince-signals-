import yfinance as yf
import pandas as pd
import requests

# --- הגדרות אישיות ---
TOKEN = "8747380852:AAGVaECHypCmUl8Qg4n237i35P-TBMKrLr4" 
CHAT_ID = "שים_כאן_את_המספר_שקיבלת" # למשל: "5882902045"

# רשימת המניות לסריקה
SYMBOLS = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "BTC-USD"]

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except:
        print("שגיאה בשליחה לטלגרם")

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_bot():
    print("🔎 סורק מניות...")
    # משיכת נתונים
    data = yf.download(SYMBOLS, period="1y", interval="1d", group_by='ticker', progress=False)
    
    for symbol in SYMBOLS:
        try:
            df = data[symbol].copy().dropna()
            
            # חישוב אינדיקטורים
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = calculate_rsi(df['Close'])
            
            price = round(df['Close'].iloc[-1], 2)
            rsi = round(df['RSI'].iloc[-1], 2)

            # בדיקת סיגנל RSI (יומי)
            if rsi < 35:
                send_telegram_msg(f"🔥 *סיגנל יומי: הזדמנות קנייה*\nנכס: `{symbol}`\nמחיר: {price}$\nמצב: מכירת יתר (RSI: {rsi})")
            
            # בדיקת סיגנל צלב זהב (שבועי)
            if df['MA20'].iloc[-2] < df['MA50'].iloc[-2] and df['MA20'].iloc[-1] > df['MA50'].iloc[-1]:
                send_telegram_msg(f"🚀 *סיגנל שבועי: פריצה*\nנכס: `{symbol}`\nמחיר: {price}$\nאירוע: צלב זהב (20 חוצה 50)")

        except Exception as e:
            print(f"שגיאה ב-{symbol}: {e}")

if __name__ == "__main__":
    run_bot()
