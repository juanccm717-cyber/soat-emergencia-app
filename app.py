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

# --- Crear entrada en lista de espera ---
def crear_lista_espera(dni_paciente):
    checklist_inicial = {
        "accidente_confirmado": True,
        "placa_verificada": False,
        "soat_adjuntado": False,
        "dni_confirmado": True
    }
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO lista_espera (dni_paciente, checklist)
            VALUES (%s, %s)
            ON CONFLICT (dni_paciente) DO UPDATE SET
                estado = 'pendiente',
                checklist = EXCLUDED.checklist,
                updated_at = NOW()
        """, (dni_paciente.strip(), json.dumps(checklist_inicial)))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error al crear lista de espera: {str(e)}")
        return False

# --- Obtener checklist actual ---
def obtener_checklist(dni_paciente):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT checklist FROM lista_espera WHERE dni_paciente = %s", (dni_paciente.strip(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return json.loads(row[0]) if row else None
    except Exception as e:
        st.error(f"❌ Error al obtener checklist: {str(e)}")
        return None

# --- Actualizar checklist ---
def actualizar_checklist(dni_paciente, checklist):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE lista_espera
            SET checklist = %s, updated_at = NOW()
            WHERE dni_paciente = %s
        """, (json.dumps(checklist), dni_paciente.strip()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error al actualizar checklist: {str(e)}")
        return False

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

# --- Vincular paciente con SOAT (solo Admisión) ---
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
        st.error(f"❌ Error al vincular paciente con SOAT: {str(e)}")
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
        if data:
            st.session_state.ingresante = {"dni": data[0], "nombre": data[1], "cargo": data[2]}
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
    opcion = st.radio("Seleccione una función:", ["Registrar Paciente (Triaje)", "Checklist de Validación", "Subir PDF SOAT", "Hoja de Ruta"])
    
    # --- Triaje: Registrar paciente y lista de espera ---
    if opcion == "Registrar Paciente (Triaje)":
        if st.session_state.user["rol"] != "triage":
            st.error("❌ Solo Triaje puede registrar pacientes.")
        else:
            st.header("👤 Registro de Paciente en Triaje")
            dni = st.text_input("DNI del paciente", max_chars=12).strip()
            if dni:
                data = buscar_paciente(dni)
                if data: 
                    st.success(f"✅ Paciente ya registrado: **{data[1]}**")
                    if st.button("Añadir a lista de espera"):
                        if crear_lista_espera(dni):
                            st.success("✅ Paciente añadido a la lista de espera.")
                else:
                    nombre = st.text_input("Nombres y apellidos completos")
                    if st.button("Registrar y añadir a lista de espera"):
                        if nombre:
                            if registrar_paciente_triage(dni, nombre) and crear_lista_espera(dni):
                                st.success(f"✅ Paciente registrado y añadido a lista de espera.")
                        else:
                            st.error("❌ Ingrese nombres y apellidos.")

    # --- Checklist de validación ---
    elif opcion == "Checklist de Validación":
        st.header("✅ Checklist de Validación Rápida")
        dni = st.text_input("DNI del paciente (registrado en Triaje)", max_chars=12).strip()
        if dni:
            paciente = buscar_paciente(dni)
            if paciente:
                checklist = obtener_checklist(dni)
                if checklist is None:
                    st.warning("⚠️ El paciente aún no está en lista de espera. Regístrelo primero en Triaje.")
                else:
                    st.write(f"**Paciente:** {paciente[1]}")
                    st.subheader("Estado actual del checklist")
                    new_checklist = checklist.copy()
                    new_checklist["placa_verificada"] = st.checkbox("Placa verificada", value=checklist["placa_verificada"])
                    new_checklist["soat_adjuntado"] = st.checkbox("SOAT adjuntado", value=checklist["soat_adjuntado"])
                    
                    if st.button("Guardar Checklist"):
                        if actualizar_checklist(dni, new_checklist):
                            st.success("✅ Checklist actualizado.")
            else:
                st.error("❌ Paciente no registrado.")

    # --- Subir PDF SOAT (Admisión y Seguros) ---
    elif opcion == "Subir PDF SOAT":
        if st.session_state.user["rol"] not in ["admission", "seguros"]:
            st.error("❌ Solo Admisión y Seguros pueden subir el certificado SOAT.")
        else:
            st.header("📄 Subir Certificado SOAT (PDF)")
            uploaded_file = st.file_uploader("Adjunte el PDF descargado", type=["pdf"])
            if uploaded_file:
                datos = extraer_datos_soat(uploaded_file)
                if all([datos["placa"], datos["fecha_vigencia"], datos["compania"], datos["numero_poliza"]]):
                    st.success("✅ Datos extraídos:")
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
                    st.error("❌ No se extrajeron todos los datos. Asegúrese de que el PDF sea válido.")

    # --- Hoja de Ruta ---
    elif opcion == "Hoja de Ruta":
        st.header("📋 Hoja de Ruta")
        dni = st.text_input("DNI del paciente", max_chars=12).strip()
        if dni:
            paciente = buscar_paciente(dni)
            if paciente:
                checklist = obtener_checklist(dni)
                if checklist and checklist["soat_adjuntado"]:
                    st.success("✅ Hoja de ruta autorizada")
                    st.markdown("""
                    **Procedimientos autorizados:**
                    - Evaluación médica inicial
                    - Rayos X de tórax y extremidades
                    - Laboratorio: hemograma, glucosa, coagulación
                    - Medicación de emergencia (analgesia, antitetánica)
                    - Observación por 6 horas
                    """)
                else:
                    st.warning("⚠️ Hoja de ruta pendiente: complete el checklist y adjunte SOAT.")
            else:
                st.error("❌ Paciente no registrado.")