from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

def get_db():
    conn = sqlite3.connect('crypto.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/latest')
def latest():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get the most recent price for each coin
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
    
    # Get last 24 price entries for a specific coin
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
