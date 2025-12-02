import streamlit as st
import os

# --- Configuración inicial de sesión ---
if "user" not in st.session_state:
    st.session_state.user = None

# --- Simulación de login (sin base de datos aún) ---
def fake_login(email, password):
    if email == "admin@hospital.com" and password == "test125879":
        return {"email": email, "rol": "admin"}
    elif email == "soat@hospital.com" and password == "test1234":
        return {"email": email, "rol": "soat"}
    return None

# --- Interfaz ---
st.set_page_config(page_title="SOAT Emergencia", layout="centered")

if st.session_state.user is None:
    st.title("🔐 Iniciar Sesión")
    with st.form("login_form"):
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Iniciar sesión")
    
    if submit:
        user = fake_login(email, password)
        if user:
            st.session_state.user = user
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