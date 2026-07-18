import pandas as pd
import psycopg2
import os
from psycopg2.extras import execute_values

DB_CONFIG = {
    'host': 'localhost',
    'database': 'trading',
    'user': 'flexx',
    'password': 'mulla'
}

CSV_PATH = os.path.expanduser('~/storage/shared/Download/1ohlc_15m.csv')

def load_csv_to_db():
    df = pd.read_csv(CSV_PATH, parse_dates=['timestamp'])
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ohlcv_15m (
            timestamp TIMESTAMP PRIMARY KEY,
            open NUMERIC,
            high NUMERIC,
            low NUMERIC,
            close NUMERIC,
            volume NUMERIC
        )
    """)
    
    data = [tuple(row) for row in df.values]
    execute_values(cur,
        "INSERT INTO ohlcv_15m (timestamp, open, high, low, close, volume) VALUES %s ON CONFLICT DO NOTHING",
        data
    )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(df)} rows into PostgreSQL")

if __name__ == '__main__':
    load_csv_to_db()
