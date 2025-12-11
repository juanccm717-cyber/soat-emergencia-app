import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_conn():
    """Devuelve conexión SSL a Neon usando 5 secrets de Streamlit."""
    user     = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host     = os.getenv("DB_HOST")
    port     = int(os.getenv("DB_PORT", 5432))
    dbname   = os.getenv("DB_NAME")
    if not all([user, password, host, dbname]):
        raise RuntimeError("❌ Faltan variables de entorno.")
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
    return psycopg2.connect(dsn)

# ---------- USUARIOS ----------
def get_user_by_email(email: str):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT email, password_hash, rol FROM usuarios WHERE email = %s", (email,))
                return cur.fetchone()
    except Exception as e:
        print("get_user_by_email:", e)
    return None

# ---------- PACIENTES ----------
def buscar_paciente(dni: str):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM pacientes WHERE dni = %s", (dni,))
                return cur.fetchone()
    except Exception as e:
        print("buscar_paciente:", e)
    return None

def registrar_paciente(dni: str, nombres: str, apellidos: str):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pacientes (dni, nombres, apellidos) VALUES (%s, %s, %s)",
                    (dni, nombres, apellidos)
                )
                conn.commit()
                return True
    except Exception as e:
        print("registrar_paciente:", e)
    return False

# ---------- SOAT ----------
def verificar_soat(placa: str):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM soat_activos WHERE placa = %s AND vencimiento >= CURRENT_DATE",
                    (placa,)
                )
                return cur.fetchone()
    except Exception as e:
        print("verificar_soat:", e)
    return None

def vincular_paciente_soat(dni: str, placa: str):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pacientes_soat (dni, placa, fecha_registro) VALUES (%s, %s, CURRENT_DATE)",
                    (dni, placa)
                )
                conn.commit()
                return True
    except Exception as e:
        print("vincular_paciente_soat:", e)
    return False