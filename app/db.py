import sqlite3
from datetime import date

DB_NAME = "database.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

# ---------- API KEY ----------
def get_api_key(key: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT key, status, daily_quota FROM api_keys WHERE key = ?",
        (key,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "key": row[0],
        "status": row[1],
        "daily_quota": row[2]
    }

# ---------- USAGE ----------
def get_usage(key: str, today: date):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT count FROM api_usage WHERE api_key = ? AND date = ?",
        (key, today.isoformat())
    )
    row = cur.fetchone()
    conn.close()

    return row[0] if row else 0

def increment_usage(key: str, today: date):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO api_usage (api_key, date, count)
        VALUES (?, ?, 1)
        ON CONFLICT(api_key, date)
        DO UPDATE SET count = count + 1
        """,
        (key, today.isoformat())
    )

    conn.commit()
    conn.close()
