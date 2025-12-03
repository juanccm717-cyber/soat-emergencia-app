import streamlit as st
import os
import psycopg2
import bcrypt
from datetime import datetime
from PyPDF2 import PdfReader
import re

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

# --- Autenticación ---
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

# --- Registrar ingresante ---
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

# --- Buscar ingresante ---
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

# --- Guardar SOAT desde PDF (Admisión y Seguros) ---
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

# --- Registrar paciente con nota de ingreso (solo Admisión) ---
def registrar_paciente_con_nota(dni_paciente, nombres, placa_soat, nota_ingreso):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pacientes_soat (dni_paciente, nombres_apellidos, placa_soat, nota_ingreso)
            VALUES (%s, %s, %s, %s)
        """, (dni_paciente.strip(), nombres.strip(), placa_soat.strip(), nota_ingreso.strip()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error al registrar paciente: {str(e)}")
        return False

# --- Roles ---
roles_nombres = {
    "admission": "Admisión",
    "seguros": "Seguros (Sub-Oficina)",
    "farmacia": "Farmacia",
    "laboratorio": "Laboratorio",
    "radiodiagnostico": "Radiodiagnóstico",
    "triage": "Triaje de Emergencia"
}

st.set_page_config(page_title="SOAT Emergencia", layout="centered")

# --- ETAPA 1: LOGIN ---
if st.session_state.user is None:
    st.title("🔐 Inicio de Sesión - SOAT Emergencia")
    rol_seleccionado = st.selectbox("Selecciona tu área", list(roles_nombres.keys()), format_func=lambda x: roles_nombres[x])
    email_real = f"{rol_seleccionado}@hospital.com"
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        user = autenticar_usuario(email_real, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas")

# --- ETAPA 2: INGRESANTE ---
elif st.session_state.ingresante is None:
    st.title(f"👤 Bienvenido, {roles_nombres[st.session_state.user['rol']]}.")
    dni = st.text_input("DNI del ingresante", max_chars=15).strip()
    if dni:
        data = buscar_ingresante(dni)
        if st.session_state.user["rol"] not in ["admission", "seguros"]:
            st.rerun()
        else:
            nombre = st.text_input("Nombres y apellidos")
            cargo = st.text_input("Cargo")
            if st.button("Registrar"):
                if nombre and cargo and registrar_ingresante(dni, nombre, cargo):
                    st.session_state.ingresante = {"dni": dni, "nombre": nombre, "cargo": cargo}
                    st.rerun()

# --- ETAPA 3: MENÚ PRINCIPAL ---
else:
    st.sidebar.title(f"🧍 {st.session_state.ingresante['nombre']}")
    st.sidebar.write(f"**Área:** {roles_nombres[st.session_state.user['rol']]}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.ingresante = None
        st.rerun()
    
    st.title("🏥 SOAT Emergencia")
    opcion = st.radio("Seleccione una función:", ["Confirmar Accidente", "Validar SOAT", "Subir PDF SOAT", "Registrar Paciente", "Hoja de Ruta"])
    
    # --- Triaje: Confirmar accidente ---
    if opcion == "Confirmar Accidente":
        if st.session_state.user["rol"] != "triage":
            st.error("❌ Solo Triaje de Emergencia puede confirmar accidentes.")
        else:
            st.header("⚠️ Confirmación de Accidente de Tránsito")
            st.write("El paciente ingresa por accidente de tránsito.")
            st.info("Una vez confirmado, Admisión o Seguros podrán proceder con la validación del SOAT.")

    # --- Validación SOAT: enlaces oficiales ---
    elif opcion == "Validar SOAT":
        st.header("🔍 Validar SOAT")
        st.write("### Consulte en los sitios oficiales:")
        st.markdown("""
        - [Interseguro - Consulta SOAT](https://www.interseguro.pe/soat/consulta-soat)
        - [Pacífico - Consulta SOAT](https://soat.pacifico.com.pe/experiencia/consulta-soat)
        - [Apeseg - Consulta SOAT](https://www.apeseg.org.pe/consultas-soat/)
        """)
        st.info("Después de validar, Admisión o Seguros pueden subir el PDF del certificado.")

    # --- Subir PDF SOAT (Admisión y Seguros) ---
    elif opcion == "Subir PDF SOAT":
        if st.session_state.user["rol"] not in ["admission", "seguros"]:
            st.error("❌ Solo Admisión y Seguros pueden subir el certificado SOAT.")
        else:
            st.header("📄 Subir Certificado SOAT (PDF)")
            uploaded_file = st.file_uploader("Adjunte el PDF descargado de la web oficial", type=["pdf"])
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
                    st.error("❌ No se extrajeron todos los datos. Asegúrese de que el PDF sea un certificado SOAT válido.")

    # --- Registrar Paciente con Nota de Ingreso (solo Admisión) ---
    elif opcion == "Registrar Paciente":
        if st.session_state.user["rol"] != "admission":
            st.error("❌ Solo Admisión puede registrar pacientes con nota de ingreso.")
        else:
            st.header("📝 Registrar Paciente y Nota de Ingreso")
            placa = st.text_input("Placa SOAT (registrada previamente)").strip().upper()
            if placa:
                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT placa FROM soat_activos WHERE placa = %s AND estado = true", (placa,))
                    existe = cur.fetchone()
                    cur.close()
                    conn.close()
                    if existe:
                        dni_paciente = st.text_input("DNI del paciente accidentado", max_chars=12).strip()
                        nombres = st.text_input("Nombres y apellidos del paciente").strip()
                        nota_ingreso = st.text_input("Número de nota de ingreso").strip()
                        if st.button("Registrar Paciente"):
                            if dni_paciente and nombres and nota_ingreso:
                                if registrar_paciente_con_nota(dni_paciente, nombres, placa, nota_ingreso):
                                    st.success("✅ Paciente registrado con nota de ingreso.")
                            else:
                                st.error("❌ Complete todos los campos.")
                    else:
                        st.error("❌ Placa SOAT no registrada o vencida.")
                except Exception as e:
                    st.error(f"❌ Error al verificar placa: {str(e)}")

    # --- Hoja de Ruta ---
    elif opcion == "Hoja de Ruta":
        st.header("📋 Hoja de Ruta")
        st.info("En desarrollo: lista de procedimientos autorizados para el paciente registrado.")