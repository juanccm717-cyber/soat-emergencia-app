import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    """Construye DATABASE_URL desde Secrets y conecta a Neon con SSL."""
    user   = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host   = os.getenv("DB_HOST")
    port   = os.getenv("DB_PORT", 5432)
    dbname = os.getenv("DB_NAME")
    if not all([user, password, host, dbname]):
        raise RuntimeError("❌ Faltan variables de entorno para conectar a Neon.")
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
    return psycopg2.connect(dsn)

def get_user_by_email(email: str):
    """Busca usuario por email exacto. Devuelve (email, password_hash, rol) o None."""
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