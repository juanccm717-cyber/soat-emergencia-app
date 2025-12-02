import streamlit as st
import os

# --- Configuración inicial ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- Mostrar mensaje de prueba ---
st.write("✅ App cargada correctamente")

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
    
    # Aquí puedes añadir el login real
    st.info("Ahora puedes implementar el formulario de login.")
    
except Exception as e:
    st.error(f"❌ Error de conexión: {str(e)}")
    st.code(str(e), language="python")