import streamlit as st
import os

# --- Configuración inicial ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- Intentar conectar a la base de datos ---
try:
    import psycopg2
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT"),
        sslmode="require"
    )
    st.success("✅ Conexión a la base de datos exitosa!")
except Exception as e:
    st.error(f"❌ Error de conexión: {str(e)}")
    st.stop()  # Detiene la ejecución si hay error

# --- Lógica de login ---
if st.session_state.user is None:
    st.title("🔐 Iniciar Sesión")
    with st.form("login_form"):
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")
    
    if submit:
        # Simulación de login (en producción, consulta la tabla 'usuarios')
        if email == "admin@hospital.com" and password == "test125879":
            st.session_state.user = {"email": email, "rol": "admin"}
            st.rerun()
        elif email == "soat@hospital.com" and password == "test1234":
            st.session_state.user = {"email": email, "rol": "soat"}
            st.rerun()
        else:
            st.error("Correo o contraseña incorrectos")
else:
    # Menú principal
    st.sidebar.title(f"Bienvenido, {st.session_state.user['email']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.user = None
        st.rerun()
    
    st.title("🏥 SOAT Emergencia")
    st.write("Menú principal cargado.")