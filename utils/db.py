import psycopg2
import os
from psycopg2.extras import RealDictCursor

def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')

def get_user_by_email(email: str):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT email, password_hash, rol FROM usuarios WHERE email = %s",
                    (email,)
                )
                row = cur.fetchone()
                if row:
                    return (row["email"], row["password_hash"], row["rol"])
    except Exception as e:
        print("DB error:", e)
    return None