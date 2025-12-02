import streamlit as st
import os
import psycopg2
import bcrypt

# --- Inicialización de sesión ---
if "user" not in st.session_state:
    st.session_state.user = None
if "ingresante" not in st.session_state:
    st.session_state.ingresante = None

# --- Conexión segura a Neon.tech ---
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

# --- Autenticación segura desde la base de datos ---
def autenticar_usuario(email, password_plana):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email, password_hash, rol FROM usuarios WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            stored_hash = row[1]
            if bcrypt.checkpw(password_plana.encode('utf-8'), stored_hash.encode('utf-8')):
                return {"email": row[0], "rol": row[2]}
        return None
    except Exception as e:
        st.error(f"❌ Error en autenticación: {str(e)}")
        return None

# --- Registrar ingresante en la base de datos (una sola vez por DNI) ---
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

# --- Mapeo de roles a nombres amigables ---
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

# --- ETAPA 2: IDENTIFICACIÓN DEL INGRESANTE (QUIEN REGISTRA) ---
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

# --- ETAPA 3: MENÚ PRINCIPAL (YA AUTENTICADO) ---
else:
    # Barra lateral con info del ingresante
    st.sidebar.title(f"🧍 {st.session_state.ingresante['nombre']}")
    st.sidebar.write(f"**Cargo:** {st.session_state.ingresante['cargo']}")
    st.sidebar.write(f"**Área:** {roles_nombres[st.session_state.user['rol']]}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.session_state.ingresante = None
        st.rerun()
    
    # Contenido principal
    st.title("🏥 SOAT Emergencia - Menú Principal")
    st.write("✅ Acceso validado con seguridad.")
    st.write("### Funcionalidades próximas:")
    st.markdown("""
    - 🔍 Validación de SOAT por placa vehicular
    - 📋 Registro de pacientes con cobertura SOAT
    - 🗺️ Generación automática de hoja de ruta
    - 📊 Consulta de historial de atención
    """)