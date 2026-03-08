import yfinance as yf
import pandas as pd
import requests

# --- הגדרות אישיות ---
TOKEN = "8747380852:AAGVaECHypCmUI8Qg4n237i35P-TBMKrLr4" 
CHAT_ID = "5882902045"

# --- רשימת נכסים ---
STOCKS = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN", "GOOGL", "META", "AMD"]
CRYPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
METALS = ["GC=F", "SI=F"]
ENERGY = ["CL=F", "NG=F"]

SYMBOLS = STOCKS + CRYPTO + METALS + ENERGY

def send_telegram_complex(message, symbol):
    # יצירת כפתורי קישור לגרפים
    tradingview_url = f"https://www.tradingview.com/symbols/{symbol.replace('-USD', '')}/"
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 צפה בגרף (TradingView)", "url": tradingview_url},
                {"text": "📈 Yahoo Finance", "url": f"https://finance.yahoo.com/quote/{symbol}"}
            ]
        ]
    }
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    requests.post(url, json=payload)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def run_bot():
    data = yf.download(SYMBOLS, period="1y", interval="1d", group_by='ticker', progress=False)
    
    for symbol in SYMBOLS:
        try:
            df = data[symbol].copy().dropna()
            if len(df) < 50: continue
            
            price = round(df['Close'].iloc[-1], 2)
            rsi = round(calculate_rsi(df['Close']).iloc[-1], 2)
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]

            # הגדרת יעד וסטופ לוס בסיסיים (3% רווח, 1.5% הפסד)
            target = round(price * 1.03, 2)
            stop_loss = round(price * 0.985, 2)

            msg = ""
            # זיהוי סיגנל לונג (קנייה)
            if rsi < 30:
                msg = (f"🟢 *הזדמנות קנייה (LONG)*\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"💎 נכס: `{symbol}`\n"
                       f"💰 מחיר נוכחי: `{price}$`\n"
                       f"📉 RSI: `{rsi}` (מכירת יתר)\n\n"
                       f"🎯 יעד משוער: `{target}$`\n"
                       f"🛡️ סטופ לוס: `{stop_loss}$`\n")

            # זיהוי סיגנל שורט (מכירה)
            elif rsi > 75:
                target_short = round(price * 0.97, 2)
                stop_short = round(price * 1.015, 2)
                msg = (f"🔴 *הזדמנות שורט (SHORT)*\n"
                       f"━━━━━━━━━━━━━━━\n"
                       f"💎 נכס: `{symbol}`\n"
                       f"💰 מחיר נוכחי: `{price}$`\n"
                       f"📈 RSI: `{rsi}` (קניית יתר)\n\n"
                       f"🎯 יעד משוער: `{target_short}$`\n"
                       f"🛡️ סטופ לוס: `{stop_short}$`\n")

            if msg:
                send_telegram_complex(msg, symbol)

        except Exception as e:
            continue

if __name__ == "__main__":
    run_bot()
