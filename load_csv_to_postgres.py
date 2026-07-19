import pandas as pd
import psycopg2
import os
from psycopg2.extras import execute_values

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'trading'),
    'user': os.environ.get('DB_USER', 'flexx'),
    'password': os.environ.get('DB_PASSWORD'),
}

CSV_PATH = os.path.expanduser('~/storage/shared/Download/1ohlc_15m.csv')


def load_csv_to_db():
    df = pd.read_csv(CSV_PATH)

    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)
    df = df.rename(columns={'Timestamp': 'timestamp'})

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ohlcv_15m (
            timestamp TIMESTAMPTZ PRIMARY KEY,
            open NUMERIC,
            high NUMERIC,
            low NUMERIC,
            close NUMERIC
        )
    """)

    data = [tuple(row) for row in df[['timestamp', 'open', 'high', 'low', 'close']].values]
    execute_values(cur,
        "INSERT INTO ohlcv_15m (timestamp, open, high, low, close) VALUES %s ON CONFLICT DO NOTHING",
        data
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {len(df)} rows into PostgreSQL")


if __name__ == '__main__':
    load_csv_to_db()
