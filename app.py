import streamlit as st
import os
import psycopg2
import bcrypt
from datetime import datetime

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

# --- Validar SOAT por placa ---
def validar_soat(placa):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT placa, dni_paciente, fecha_vigencia, compania, numero_poliza
            FROM soat_activos
            WHERE placa = %s AND estado = true AND fecha_vigencia >= CURRENT_DATE
        """, (placa.strip().upper(),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Exception as e:
        st.error(f"❌ Error al validar SOAT: {str(e)}")
        return None

# --- Guardar SOAT manualmente (para Seguros y Admisión) ---
def registrar_soat_manual(placa, dni_paciente, fecha_vigencia, compania, numero_poliza):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO soat_activos (placa, dni_paciente, fecha_vigencia, compania, numero_poliza)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (placa) DO UPDATE SET
                dni_paciente = EXCLUDED.dni_paciente,
                fecha_vigencia = EXCLUDED.fecha_vigencia,
                compania = EXCLUDED.compania,
                numero_poliza = EXCLUDED.numero_poliza,
                estado = true
        """, (placa.strip().upper(), dni_paciente.strip(), fecha_vigencia, compania.strip(), numero_poliza.strip()))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error al registrar SOAT: {str(e)}")
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

# --- ETAPA 1: LOGIN POR ÁREA ---
if st.session_state.user is None:
    st.title("🔐 Inicio de Sesión - SOAT Emergencia")
    
    rol_seleccionado = st.selectbox(
        "Selecciona tu área de trabajo",
        options=list(roles_nombres.keys()),
        format_func=lambda x: roles_nombres[x]
    )
    
    email_real = f"{rol_seleccionado}@hospital.com"
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        if not password:
            st.warning("⚠️ Por favor, ingresa una contraseña.")
        else:
            user = autenticar_usuario(email_real, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

# --- ETAPA 2: IDENTIFICACIÓN DEL INGRESANTE ---
elif st.session_state.ingresante is None:
    st.title(f"👤 Bienvenido, {roles_nombres[st.session_state.user['rol']]}.")
    st.subheader("Por favor, identifícate como personal autorizado")
    
    dni = st.text_input("DNI del ingresante", max_chars=15).strip()
    
    if dni:
        datos = buscar_ingresante(dni)
        if datos:
            st.session_state.ingresante = {
                "dni": datos[0],
                "nombre": datos[1],
                "cargo": datos[2]
            }
            st.success(f"✅ Bienvenido, **{datos[1]}** ({datos[2]})")
            st.rerun()
        else:
            st.warning("⚠️ Ingresante no registrado. Complete sus datos a continuación.")
            nombre = st.text_input("Nombres y apellidos completos")
            cargo = st.text_input("Cargo o rol en el hospital")
            if st.button("Registrar como ingresante"):
                if nombre.strip() and cargo.strip():
                    if registrar_ingresante(dni, nombre, cargo):
                        st.session_state.ingresante = {
                            "dni": dni,
                            "nombre": nombre,
                            "cargo": cargo
                        }
                        st.success("✅ Registro exitoso. Bienvenido.")
                        st.rerun()
                else:
                    st.error("❌ Por favor, complete todos los campos.")

# --- ETAPA 3: MENÚ PRINCIPAL ---
else:
    st.sidebar.title(f"🧍 {st.session_state.ingresante['nombre']}")
    st.sidebar.write(f"**Cargo:** {st.session_state.ingresante['cargo']}")
    st.sidebar.write(f"**Área:** {roles_nombres[st.session_state.user['rol']]}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.ingresante = None
        st.rerun()
    
    st.title("🏥 SOAT Emergencia - Menú Principal")
    opcion = st.radio("Selecciona una función:", ["Validar SOAT", "Registrar SOAT (Seguros/Admisión)", "Hoja de Ruta"])
    
    # --- Validar SOAT ---
    if opcion == "Validar SOAT":
        st.header("🔍 Validación de SOAT")
        placa = st.text_input("Ingrese la placa del vehículo", max_chars=10).strip().upper()
        if st.button("Consultar SOAT"):
            if not placa:
                st.warning("⚠️ Por favor, ingrese una placa.")
            else:
                resultado = validar_soat(placa)
                if resultado:
                    dni_paciente, fecha_vigencia, compania, numero_poliza = resultado
                    st.success(f"✅ SOAT activo")
                    st.write(f"**DNI del asegurado:** {dni_paciente}")
                    st.write(f"**Compañía:** {compania}")
                    st.write(f"**Póliza:** {numero_poliza}")
                    st.write(f"**Vigente hasta:** {fecha_vigencia}")
                else:
                    st.error("❌ SOAT no activo, vencido o no registrado.")
    
    # --- Registrar SOAT (solo para Seguros y Admisión) ---
    elif opcion == "Registrar SOAT (Seguros/Admisión)":
        if st.session_state.user["rol"] not in ["seguros", "admission"]:
            st.error("❌ Solo las áreas de Seguros y Admisión pueden registrar SOAT.")
        else:
            st.header("📄 Registrar SOAT Manualmente")
            placa = st.text_input("Placa", max_chars=10).strip().upper()
            dni_paciente = st.text_input("DNI del asegurado", max_chars=12).strip()
            compania = st.selectbox("Compañía de seguros", ["Interseguro", "Pacífico", "Otra"])
            if compania == "Otra":
                compania = st.text_input("Nombre de la compañía")
            numero_poliza = st.text_input("Número de póliza", max_chars=20).strip()
            fecha_vigencia = st.date_input("Fecha de vigencia (hasta)", value=datetime.today().date())
            
            if st.button("Registrar SOAT"):
                if placa and dni_paciente and compania and numero_poliza:
                    if registrar_soat_manual(placa, dni_paciente, fecha_vigencia, compania, numero_poliza):
                        st.success(f"✅ SOAT registrado para placa {placa}")
                else:
                    st.error("❌ Complete todos los campos.")
    
    # --- Hoja de Ruta ---
    elif opcion == "Hoja de Ruta":
        st.header("📋 Hoja de Ruta")
        st.info("Funcionalidad en desarrollo.")