import requests
import sqlite3
from datetime import datetime
import schedule
import time

def fetch_and_store():
    # Fetch top 10 coins from CoinGecko (no API key needed)
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1
    }

    response = requests.get(url, params=params)
    coins = response.json()

    conn = sqlite3.connect('crypto.db')
    cursor = conn.cursor()

    for coin in coins:
        cursor.execute('''
            INSERT INTO prices (coin_id, coin_name, price_usd, market_cap, volume_24h, price_change_24h)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            coin['id'],
            coin['name'],
            coin['current_price'],
            coin['market_cap'],
            coin['total_volume'],
            coin['price_change_percentage_24h']
        ))

    conn.commit()
    conn.close()
    print(f"Data collected at {datetime.now()}")

if __name__ == "__main__":
    fetch_and_store()  # Run immediately on start
    schedule.every(1).hours.do(fetch_and_store)
    print("Scheduler running — collecting data every hour...")
    while True:
        schedule.run_pending()
        time.sleep(60)