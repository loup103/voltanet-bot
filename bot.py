import os
import time
import threading
import requests
import pandas as pd
import ta
from flask import Flask

# --- CONFIGURATION DU PETIT SERVEUR WEB (Pour Render) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "VoltaDev VIP Bot is running live!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- VOS IDENTIFIANTS TELEGRAM ---
TELEGRAM_TOKEN = "8981234758:AAG1vmVinN6fzqyNq_h7eV4Zh0HD0wHJTe0"
CHANNEL_ID = "-1004362539635"  # ID de votre canal VoltaDev Signals VIP

CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
INTERVAL = "1h"

def send_channel_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erreur de connexion : {e}")

def analyze_cryptos():
    print("🔎 [VIP] Analyse du marché Crypto...")
    for symbol in CRYPTO_SYMBOLS:
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit=100"
            response = requests.get(url)
            data = response.json()
            
            df = pd.DataFrame(data, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            last_price = df['close'].iloc[-1]
            last_rsi = df['rsi'].iloc[-1]
            
            print(f"  └─ {symbol} | Prix: {last_price:.2f}$ | RSI (1h): {last_rsi:.1f}")
            
            if last_rsi <= 30:
                msg = (
                    f"🟢 **SIGNAL VIP CRYPTO (Survente)**\n\n"
                    f"📌 **Paire :** `{symbol}`\n"
                    f"💵 **Prix actuel :** `{last_price:.2f} $`\n"
                    f"📊 **RSI (1h) :** `{last_rsi:.1f}` (Seuil <= 30)\n\n"
                    f"🎯 *Zone d'opportunité détectée par VoltaDev VIP Signals.*"
                )
                send_channel_alert(msg)
            elif last_rsi >= 70:
                msg = (
                    f"🔴 **SIGNAL VIP CRYPTO (Surchauffe)**\n\n"
                    f"📌 **Paire :** `{symbol}`\n"
                    f"💵 **Prix actuel :** `{last_price:.2f} $`\n"
                    f"📊 **RSI (1h) :** `{last_rsi:.1f}` (Seuil >= 70)\n\n"
                    f"🎯 *Zone de prise de bénéfices détectée par VoltaDev VIP Signals.*"
                )
                send_channel_alert(msg)
        except Exception as e:
            print(f"Erreur sur {symbol}: {e}")

def analyze_forex():
    print("🔎 [VIP] Analyse du marché Forex...")
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        res = requests.get(url).json()
        rates = res.get("rates", {})
        forex_pairs = {"EUR/USD": rates.get("EUR"), "GBP/USD": rates.get("GBP"), "USD/JPY": rates.get("JPY")}
        for pair, rate in forex_pairs.items():
            if rate:
                print(f"  └─ {pair} | Taux direct : {rate:.4f}")
    except Exception as e:
        print(f"Erreur d'analyse Forex: {e}")

def run_bot():
    print("🚀 Démarrage du système de surveillance VoltaDev VIP...")
    send_channel_alert("⚡ **Le Bot VoltaDev VIP (Crypto & Forex) est désormais actif et opérationnel !**\n\nLes alertes de détection en temps réel seront publiées directement dans ce canal.")
    while True:
        analyze_cryptos()
        analyze_forex()
        print("⏳ Pause de 5 minutes avant la prochaine analyse globale...\n")
        time.sleep(300)

if __name__ == "__main__":
    # Lancement du bot dans un fil d'exécutif séparé
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Lancement du serveur web pour Render
    run_web()
