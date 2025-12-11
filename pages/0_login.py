import streamlit as st
import bcrypt
from utils.db import get_user_by_email

# ---------- 7 ÁREAS VÁLIDAS (igual a tabla usuarios) ----------
AREA_PAGE = {
    "ADMINISTRADOR": "pages/7_Dashboard.py",   # acceso total
    "TRIAJE": "pages/1_Triaje.py",
    "SEGUROS-SOAT": "pages/2_Seguros_SOAT.py",
    "ADMISION": "pages/3_Admission.py",
    "FARMACIA": "pages/4_Farmacia.py",
    "LABORATORIO": "pages/5_Laboratorio.py",
    "RADIO DIAGNOSTICO": "pages/6_Radiodiagnostico.py",
}

# Emails reales en Neon (1 × 1 con tabla usuarios)
EMAIL_MAP = {
    "ADMINISTRADOR": "admin@hospital.com",
    "TRIAJE": "triage@hospital.com",
    "SEGUROS-SOAT": "seguros@hospital.com",
    "ADMISION": "admission@hospital.com",
    "FARMACIA": "farmacia@hospital.com",
    "LABORATORIO": "laboratorio@hospital.com",
    "RADIO DIAGNOSTICO": "radiodiag@hospital.com",
}

st.title("SOATAPP – Inicio de Sesión")
st.markdown("Ingrese su área y contraseña para continuar.")

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
        st.error("❌ Credenciales incorrectas")

if "page" in st.session_state:
    st.switch_page(st.session_state.page)