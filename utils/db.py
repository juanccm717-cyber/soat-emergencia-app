# utils/db.py
import os
import psycopg2
import bcrypt
import json
from datetime import datetime
from PyPDF2 import PdfReader
import re

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT"),
        sslmode="require"
    )

def autenticar_usuario(email, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email, password_hash, rol FROM usuarios WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row and bcrypt.checkpw(password.encode('utf-8'), row[1].encode('utf-8')):
            return {"email": row[0], "rol": row[2]}
        return None
    except Exception as e:
        return None

def buscar_ingresante(dni):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT dni, nombres_apellidos, cargo FROM ingresantes WHERE dni = %s", (dni.strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except:
        return None

def registrar_ingresante(dni, nombre, cargo):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ingresantes (dni, nombres_apellidos, cargo)
            VALUES (%s, %s, %s)
            ON CONFLICT (dni) DO NOTHING
        """, (dni.strip(), nombre.strip(), cargo.strip()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        return False

def buscar_paciente(dni):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT dni, nombres_apellidos FROM pacientes WHERE dni = %s", (dni.strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except:
        return None

def registrar_paciente_triage(dni, nombre):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pacientes (dni, nombres_apellidos)
            VALUES (%s, %s)
            ON CONFLICT (dni) DO NOTHING
        """, (dni.strip(), nombre.strip()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        return False

def extraer_datos_soat(pdf_file):
    reader = PdfReader(pdf_file)
    texto = "".join(page.extract_text() or "" for page in reader.pages)
    placa_match = re.search(r'Placa\s*[:\s]*([A-Z0-9]{6,7})', texto, re.IGNORECASE)
    placa = placa_match.group(1) if placa_match else None
    fecha_match = re.search(r'Hasta\s*(\d{2}/\d{2}/\d{4})', texto)
    fecha_vigencia = datetime.strptime(fecha_match.group(1), "%d/%m/%Y").date() if fecha_match else None
    compania = "Interseguro" if "INTERSEGURO" in texto.upper() else "Pacífico" if "PACIFICO" in texto.upper() else None
    poliza_match = re.search(r'N°\s*Póliza- Certificado\s*(\d+)', texto)
    numero_poliza = poliza_match.group(1) if poliza_match else None
    dni_asegurado = re.search(r'DNI del Asegurado\s*[:\s]*(\d+)', texto, re.IGNORECASE)
    dni_asegurado = dni_asegurado.group(1) if dni_asegurado else "70000001"
    return {
        "placa": placa,
        "dni_asegurado": dni_asegurado,
        "fecha_vigencia": fecha_vigencia,
        "compania": compania,
        "numero_poliza": numero_poliza
    }

def guardar_soat_desde_pdf(placa, dni_asegurado, fecha_vigencia, compania, numero_poliza):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO soat_activos (placa, dni_asegurado, fecha_vigencia, compania, numero_poliza)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (placa) DO UPDATE SET
                dni_asegurado = EXCLUDED.dni_asegurado,
                fecha_vigencia = EXCLUDED.fecha_vigencia,
                compania = EXCLUDED.compania,
                numero_poliza = EXCLUDED.numero_poliza,
                estado = true
        """, (placa, dni_asegurado, fecha_vigencia, compania, numero_poliza))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        return False

def vincular_paciente_soat(dni_paciente, placa_soat, nota_ingreso):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pacientes_soat (dni_paciente, placa_soat, nota_ingreso)
            VALUES (%s, %s, %s)
        """, (dni_paciente.strip(), placa_soat.strip(), nota_ingreso.strip()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except:
        return False

def verificar_soat(placa):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT placa FROM soat_activos WHERE placa = %s AND estado = true", (placa,))
        return cur.fetchone() is not None
    except:
        return False