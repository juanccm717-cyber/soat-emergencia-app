import streamlit as st
import bcrypt
from utils.db import get_user_by_email

# Mapeo área → archivo
AREA_PAGE = {
    "Admin": "pages/3_Admission.py",
    "SOAT": "pages/2_Seguros_SOAT.py",
    "Seguros": "pages/2_Seguros_SOAT.py",
    "Farmacia": "pages/4_Farmacia.py",
    "Laboratorio": "pages/5_Laboratorio.py",
    "Radiodiagnostico": "pages/6_Radiodiagnostico.py",
    "Triaje": "pages/1_Triage.py",
}

# Emails reales en Neon
EMAIL_MAP = {
    "Admin": "admin@hospital.com",
    "SOAT": "soat@hospital.com",
    "Seguros": "seguros@hospital.com",
    "Farmacia": "farmacia@hospital.com",
    "Laboratorio": "laboratorio@hospital.com",
    "Radiodiagnostico": "radiodiag@hospital.com",
    "Triaje": "triage@hospital.com",
}

st.title("SOATAPP – Inicio de Sesión (DEBUG)")

with st.form("login"):
    area = st.selectbox("Seleccione su área de trabajo", list(AREA_PAGE.keys()))
    password = st.text_input("Contraseña", type="password")
    enviar = st.form_submit_button("Iniciar Sesión")

if enviar:
    email = EMAIL_MAP[area]
    st.write("🔍 Email que se busca:", email)
    user = get_user_by_email(email)
    if user:
        st.write("✅ Usuario encontrado en BD:", user)
        hash_bd = user[1].encode()
        st.write("🔑 Hash en BD:", hash_bd)
        st.write("🔑 Password enviada:", password.encode())
        if bcrypt.checkpw(password.encode(), hash_bd):
            st.success("✅ Hash coincide → ingresando")
            st.session_state.user = {"email": user[0], "rol": user[2]}
            st.session_state.page = AREA_PAGE[area]
            st.rerun()
        else:
            st.error("❌ Hash NO coincide")
    else:
        st.error("❌ Usuario NO encontrado en BD")

if st.session_state.get("page"):
    st.switch_page(st.session_state.page)