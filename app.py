from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests
import schedule
import time
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ─── Database ────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect('crypto.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT NOT NULL,
            coin_name TEXT NOT NULL,
            price_usd REAL NOT NULL,
            market_cap REAL,
            volume_24h REAL,
            price_change_24h REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('crypto.db')
    conn.row_factory = sqlite3.Row
    return conn

# ─── Collector ───────────────────────────────────────────────────────────────

def fetch_and_store():
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1
        }
        response = requests.get(url, params=params, timeout=10)
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
    except Exception as e:
        print(f"Collection error: {e}")

def run_scheduler():
    schedule.every(1).hours.do(fetch_and_store)
    while True:
        schedule.run_pending()
        time.sleep(60)

# ─── API Routes ──────────────────────────────────────────────────────────────

@app.route('/api/latest')
def latest():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT coin_id, coin_name, price_usd, market_cap, volume_24h, price_change_24h, timestamp
        FROM prices
        WHERE timestamp = (
            SELECT MAX(timestamp) FROM prices p2 WHERE p2.coin_id = prices.coin_id
        )
        ORDER BY market_cap DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/history/<coin_id>')
def history(coin_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT price_usd, timestamp
        FROM prices
        WHERE coin_id = ?
        ORDER BY timestamp DESC
        LIMIT 24
    ''', (coin_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# ─── Start ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    fetch_and_store()  # Collect immediately on startup

    # Run scheduler in background thread so Flask can still serve requests
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
