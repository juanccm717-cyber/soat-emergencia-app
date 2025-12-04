import streamlit as st
import os
import psycopg2
import bcrypt
from datetime import datetime
from PyPDF2 import PdfReader
import re
import json

# --- Inicialización de sesión ---
if "user" not in st.session_state:
    st.session_state.user = None
if "ingresante" not in st.session_state:
    st.session_state.ingresante = None

# --- Conexión segura a Neon ---
def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT"),
            sslmode="require"
        )
    except Exception as e:
        st.error(f"❌ Error al conectar con la base de datos: {str(e)}")
        st.stop()

# --- Autenticación desde base de datos ---
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
        st.error(f"❌ Error en autenticación: {str(e)}")
        return None

# --- Registrar ingresante (quien usa la app) ---
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
    except Exception as e:
        st.error(f"❌ Error al registrar ingresante: {str(e)}")
        return False

# --- Buscar ingresante por DNI ---
def buscar_ingresante(dni):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT dni, nombres_apellidos, cargo FROM ingresantes WHERE dni = %s", (dni.strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Exception as e:
        st.error(f"❌ Error al buscar ingresante: {str(e)}")
        return None

# --- Registrar paciente en Triaje ---
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
    except Exception as e:
        st.error(f"❌ Error al registrar paciente: {str(e)}")
        return False

# --- Buscar paciente por DNI ---
def buscar_paciente(dni):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT dni, nombres_apellidos FROM pacientes WHERE dni = %s", (dni.strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Exception as e:
        st.error(f"❌ Error al buscar paciente: {str(e)}")
        return None

# --- Extraer datos de PDF de SOAT ---
def extraer_datos_soat(pdf_file):
    reader = PdfReader(pdf_file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    
    placa_match = re.search(r'Placa\s*[:\s]*([A-Z0-9]{6,7})', texto, re.IGNORECASE)
    placa = placa_match.group(1) if placa_match else None

    fecha_match = re.search(r'Hasta\s*(\d{2}/\d{2}/\d{4})', texto)
    fecha_vigencia = None
    if fecha_match:
        try:
            fecha_vigencia = datetime.strptime(fecha_match.group(1), "%d/%m/%Y").date()
        except:
            pass

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

# --- Guardar SOAT desde PDF ---
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
    except Exception as e:
        st.error(f"❌ Error al guardar SOAT: {str(e)}")
        return False

# --- Vincular paciente con SOAT y nota de ingreso ---
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
    except Exception as e:
        st.error(f"❌ Error al vincular paciente: {str(e)}")
        return False

# --- Nombres amigables de roles ---
roles_nombres = {
    "admission": "Admisión",
    "seguros": "Seguros (Sub-Oficina)",
    "farmacia": "Farmacia",
    "laboratorio": "Laboratorio",
    "radiodiagnostico": "Radiodiagnóstico",
    "triage": "Triaje de Emergencia"
}

# --- Configuración de la página ---
st.set_page_config(page_title="SOAT Emergencia", layout="centered")

# --- ETAPA 1: LOGIN INICIAL ---
if st.session_state.user is None:
    st.title("🔐 Inicio de Sesión - SOAT Emergencia")
    email = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        user = autenticar_usuario(email, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# --- ETAPA 2: IDENTIFICACIÓN DEL INGRESANTE (quien usa la app) ---
elif st.session_state.ingresante is None:
    st.title("👤 Identificación del Personal Autorizado")
    dni = st.text_input("DNI", max_chars=15).strip()
    if dni:
        data = buscar_ingresante(dni)
        if data:
            st.session_state.ingresante = {"dni": data[0], "nombre": data[1], "cargo": data[2]}
            st.rerun()
        else:
            nombre = st.text_input("Nombres y apellidos completos")
            cargo = st.text_input("Cargo o rol en el hospital")
            if st.button("Registrar como ingresante"):
                if nombre.strip() and cargo.strip():
                    if registrar_ingresante(dni, nombre, cargo):
                        st.session_state.ingresante = {"dni": dni, "nombre": nombre, "cargo": cargo}
                        st.success("✅ Registro exitoso")
                        st.rerun()
                else:
                    st.error("❌ Complete todos los campos.")

# --- ETAPA 3: MENÚ PRINCIPAL POR ROL ---
else:
    st.sidebar.title(f"🧍 {st.session_state.ingresante['nombre']}")
    st.sidebar.write(f"**Área:** {roles_nombres[st.session_state.user['rol']]}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.ingresante = None
        st.rerun()

    st.title("🏥 SOAT Emergencia - Menú Principal")

    # --- Triaje: solo registra paciente ---
    if st.session_state.user["rol"] == "triage":
        st.header("📌 Registro de Paciente (Triaje)")
        dni = st.text_input("DNI del paciente", max_chars=12).strip()
        if dni:
            data = buscar_paciente(dni)
            if data:
                st.success(f"✅ Paciente ya registrado: **{data[1]}**")
            else:
                nombre = st.text_input("Nombres y apellidos completos")
                if st.button("Registrar Paciente"):
                    if nombre.strip():
                        if registrar_paciente_triage(dni, nombre):
                            st.success(f"✅ Paciente registrado: **{nombre}**")
                    else:
                        st.error("❌ Ingrese nombres y apellidos.")

    # --- Seguros: solo sube PDF SOAT ---
    elif st.session_state.user["rol"] == "seguros":
        st.header("📄 Subir Certificado SOAT")
        uploaded_file = st.file_uploader("Adjunte el PDF del certificado", type=["pdf"])
        if uploaded_file:
            datos = extraer_datos_soat(uploaded_file)
            if all([datos["placa"], datos["fecha_vigencia"], datos["compania"], datos["numero_poliza"]]):
                st.success("✅ Datos extraídos del PDF:")
                st.write(f"**Placa:** {datos['placa']}")
                st.write(f"**Titular (DNI):** {datos['dni_asegurado']}")
                st.write(f"**Compañía:** {datos['compania']}")
                st.write(f"**Póliza:** {datos['numero_poliza']}")
                st.write(f"**Vigente hasta:** {datos['fecha_vigencia']}")
                if st.button("Registrar SOAT"):
                    if guardar_soat_desde_pdf(
                        datos["placa"],
                        datos["dni_asegurado"],
                        datos["fecha_vigencia"],
                        datos["compania"],
                        datos["numero_poliza"]
                    ):
                        st.success(f"✅ SOAT registrado para placa {datos['placa']}")
            else:
                st.error("❌ No se extrajeron todos los datos. Use un PDF válido de SOAT.")

    # --- Admisión: solo vincula SOAT con nota de ingreso ---
    elif st.session_state.user["rol"] == "admission":
        st.header("🔗 Vincular SOAT con Nota de Ingreso")
        dni = st.text_input("DNI del paciente (registrado en Triaje)", max_chars=12).strip()
        if dni:
            paciente = buscar_paciente(dni)
            if paciente:
                st.write(f"**Paciente:** {paciente[1]}")
                placa = st.text_input("Placa SOAT (registrada)").strip().upper()
                if placa:
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("SELECT placa FROM soat_activos WHERE placa = %s AND estado = true", (placa,))
                        existe = cur.fetchone()
                        cur.close()
                        conn.close()
                        if existe:
                            nota_ingreso = st.text_input("Número de nota de ingreso").strip()
                            if st.button("Vincular"):
                                if nota_ingreso:
                                    if vincular_paciente_soat(dni, placa, nota_ingreso):
                                        st.success("✅ Vinculación exitosa")
                                else:
                                    st.error("❌ Ingrese el número de nota de ingreso.")
                        else:
                            st.error("❌ Placa SOAT no registrada o vencida.")
                    except Exception as e:
                        st.error(f"❌ Error al verificar placa: {str(e)}")
            else:
                st.error("❌ Paciente no registrado en Triaje.")

    # --- Otros roles (información genérica) ---
    else:
        st.info("🟢 Bienvenido. Tu área no tiene módulos específicos en esta versión.")