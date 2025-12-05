import streamlit as st
import bcrypt
from utils.db import get_user_by_email

# Desplegable visible → archivo destino
AREA_PAGE = {
    "Admin": "pages/3_Admission.py",
    "SOAT": "pages/2_Seguros_SOAT.py",
    "Seguros": "pages/2_Seguros_SOAT.py",
    "Farmacia": "pages/4_Farmacia.py",
    "Laboratorio": "pages/5_Laboratorio.py",
    "Radiodiagnostico": "pages/6_Radiodiagnostico.py",
    "Triaje": "pages/1_Triage.py",
}

# Email real en Neon según área
EMAIL_MAP = {
    "Admin": "admin@hospital.com",
    "SOAT": "soat@hospital.com",
    "Seguros": "seguros@hospital.com",
    "Farmacia": "farmacia@hospital.com",
    "Laboratorio": "laboratorio@hospital.com",
    "Radiodiagnostico": "radiodiag@hospital.com",
    "Triaje": "triage@hospital.com",
}

st.title("SOATAPP - Inicio de Sesión")

with st.form("login"):
    area = st.selectbox("Seleccione su área de trabajo", list(AREA_PAGE.keys()))
    password = st.text_input("Contraseña", type="password")
    enviar = st.form_submit_button("Iniciar Sesión")

if enviar:
    email = EMAIL_MAP[area]
    user = get_user_by_email(email)
    if user and bcrypt.checkpw(password.encode(), user[1].encode()):
        st.session_state.user = {"email": user[0], "rol": user[2]}
        st.session_state.page = AREA_PAGE[area]
        st.rerun()
    else:
        st.error("Credenciales incorrectas")

if st.session_state.get("page"):
    st.switch_page(st.session_state.page)