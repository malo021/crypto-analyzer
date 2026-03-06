import sqlite3

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
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()