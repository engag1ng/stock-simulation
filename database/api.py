import sqlite3
import json

def create_db():
    conn, cursor = initialize_db()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_data (
        timestamp TEXT,
        symbol TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        features TEXT,
        PRIMARY KEY (timestamp, symbol)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS backtest_results (
        start_timestamp TEXT NOT NULL,
        end_timestamp TEXT NOT NULL,
        symbol TEXT NOT NULL,
        interval TEXT,
        decisions TEXT,
        revenue REAL,
        start_capital REAL,
        strategy TEXT NOT NULL,
        PRIMARY KEY (start_timestamp, end_timestamp, symbol, strategy)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS forwardtest_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        start_price REAL,
        path TEXT,
        decisions TEXT,
        revenue REAL,
        start_capital REAL,
        strategy TEXT
    );
    """)

    close_conn(conn)


def initialize_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    return conn, cursor

def close_conn(conn):
    conn.commit()
    conn.close()

def fetch_market_data(conn, start_timestamp, end_timestamp, ticker):
    cursor = conn.cursor()

    query = """
    SELECT timestamp, open, high, low, close, volume, features
    FROM market_data
    WHERE symbol = ? AND timestamp BETWEEN ? AND ?
    ORDER BY timestamp ASC
    """
    res = cursor.execute(query, (ticker, start_timestamp, end_timestamp))
    rows = res.fetchall()

    result = [
        {
            "timestamp": row[0],
            "open": row[1],
            "high": row[2],
            "low": row[3],
            "close": row[4],
            "volume": row[5],
        }
        for row in rows
    ]

    return json.dumps(result, indent=2)

def insert_feature(conn, feature_func):
    """
    Applies a feature-generating function to each row of market_data.
    The function must return a dict of feature_name: value.
    """
    cursor = conn.cursor()

    # Get all required data from the table
    cursor.execute("SELECT timestamp, symbol, open, high, low, close, volume, features FROM market_data")
    rows = cursor.fetchall()

    for timestamp, symbol, open_, high, low, close, volume, features in rows:
        if features:
            existing = json.loads(features)
        else:
            existing = {}

        # Calculate new features using user-provided function
        new_features = feature_func({
            "timestamp": timestamp,
            "symbol": symbol,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume
        })

        # Merge and update
        merged = {**existing, **new_features}
        merged_json = json.dumps(merged)

        cursor.execute("""
            UPDATE market_data
            SET features = ?
            WHERE timestamp = ? AND symbol = ?
        """, (merged_json, timestamp, symbol))

    conn.commit()


def remove_feature(conn, feature_to_remove):
    cursor = conn.cursor()

    res = cursor.execute("SELECT timestamp, symbol, features FROM market_data")
    rows = res.fetchall()

    for timestamp, symbol, features in rows:
        if not features:
            continue

        feature_dict = json.loads(features)
        if feature_to_remove in feature_dict:
            del feature_dict[feature_to_remove]

            updated_json = json.dumps(feature_dict)
            cursor.execute("""
                UPDATE market_data
                SET features = ?
                WHERE timestamp = ? AND symbol = ?
            """, (updated_json, timestamp, symbol))

    conn.commit()