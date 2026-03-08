import yfinance as yf
import pandas as pd
import requests

# --- הגדרות אישיות ---
TOKEN = "8747380852:AAGVaECHypCmUI8Qg4n237i35P-TBMKrLr4" 
CHAT_ID = "5882902045"

# --- רשימת נכסים מורחבת ---
# מניות (Stocks)
STOCKS = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "GOOGL", "META"]
# קריפטו (Crypto) - פועל 24/7
CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"]
# מתכות (Metals)
METALS = ["GC=F", "SI=F"] # GC=זהב, SI=כסף
# אנרגיה (Energy)
ENERGY = ["CL=F", "NG=F"] # CL=נפט גולמי, NG=גז טבעי

SYMBOLS = STOCKS + CRYPTO + METALS + ENERGY

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
    print(f"🔎 סורק {len(SYMBOLS)} נכסים בשווקים השונים...")
    data = yf.download(SYMBOLS, period="1y", interval="1d", group_by='ticker', progress=False)
    
    for symbol in SYMBOLS:
        try:
            df = data[symbol].copy().dropna()
            if len(df) < 50: continue
            
            # חישוב אינדיקטורים
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['RSI'] = calculate_rsi(df['Close'])
            
            price = round(df['Close'].iloc[-1], 2)
            rsi = round(df['RSI'].iloc[-1], 2)
            
            # התאמת אייקון לפי סוג הנכס
            icon = "📊"
            if symbol in CRYPTO: icon = "🪙"
            elif symbol in METALS: icon = "✨"
            elif symbol in ENERGY: icon = "🛢️"
            elif symbol in STOCKS: icon = "📈"

            # בדיקת סיגנל RSI
            if rsi < 32:
                send_telegram_msg(f"{icon} *הזדמנות קנייה (RSI):* {symbol}\nמחיר: {price}$\nמצב: מכירת יתר ({rsi})")
            elif rsi > 75:
                send_telegram_msg(f"{icon} *התראת מכירה (RSI):* {symbol}\nמחיר: {price}$\nמצב: קניית יתר ({rsi})")

            # בדיקת סיגנל צלב זהב
            if df['MA20'].iloc[-2] < df['MA50'].iloc[-2] and df['MA20'].iloc[-1] > df['MA50'].iloc[-1]:
                send_telegram_msg(f"🚀 *פריצת מגמה:* {symbol}\nמחיר: {price}$\nאירוע: צלב זהב (MA20 חצה MA50)")

        except Exception as e:
            print(f"שגיאה ב-{symbol}: {e}")

if __name__ == "__main__":
    run_bot()
