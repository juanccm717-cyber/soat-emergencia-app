import streamlit as st
import bcrypt
from utils.db import get_user_by_email  # ← tu función real

# Mapeo área → archivo
AREA_PAGE = {
    "Admisión": "pages/3_Admission.py",
    "Seguros (Sub-Oficina)": "pages/2_Seguros_SOAT.py",
    "Farmacia": "pages/4_Farmacia.py",
    "Laboratorio": "pages/5_Laboratorio.py",
    "Radiodiagnostico": "pages/6_Radiodiagnostico.py",
    "Triaje de Emergencia": "pages/1_Triage.py",
}

st.title("SOATAPP - Inicio de Sesión")

with st.form("login"):
    area = st.selectbox("Seleccione su área de trabajo", list(AREA_PAGE.keys()))
    password = st.text_input("Contraseña", type="password")
    enviar = st.form_submit_button("Iniciar Sesión")

if enviar:
    # 1. Obtener usuario de Neon (ejemplo con email hardcodeado por área)
    email = area.lower().replace(" ", "").replace("(", "").replace(")", "") + "@hospital.com"
    user = get_user_by_email(email)  # ← debe devolver (email, hash, rol) o None
    if user and bcrypt.checkpw(password.encode(), user[1].encode()):
        st.session_state.user = {"email": user[0], "rol": user[2]}
        st.session_state.page = AREA_PAGE[area]  # destino
        st.rerun()  # ← OBLIGATORIO
    else:
        st.error("Credenciales incorrectas")

# 2. Redirigir tras el rerun
if st.session_state.get("page"):
    st.switch_page(st.session_state.page)