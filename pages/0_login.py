import streamlit as st
from utils.db import autenticar_usuario

st.set_page_config(page_title="SOATAPP", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None
if "ingresante" not in st.session_state:
    st.session_state.ingresante = None

st.title("🔐 SOATAPP - Inicio de Sesión")
email = st.text_input("Correo electrónico")
password = st.text_input("Contraseña", type="password")
if st.button("Iniciar Sesión"):
    user = autenticar_usuario(email, password)
    if user:
        st.session_state.user = user
        st.switch_page("pages/1_Triage.py")
    else:
        st.error("❌ Usuario o contraseña incorrectos.")