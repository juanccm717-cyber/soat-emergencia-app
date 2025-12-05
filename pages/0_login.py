import streamlit as st
import bcrypt
from utils.db import get_user_by_email

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
    # ---- depuración visible ----
    email = (
        area.lower()
        .replace(" ", "")
        .replace("(", "")
        .replace(")", "")
        .replace("ó", "o")          # Admisión → admision
        .replace("á", "a")          # Farmacia → farmacia
        .replace("é", "e")          # Emergencia → emergencia
        + "@hospital.com"
    )
    st.info(f"Email generado: {email}")
    st.info(f"Password ingresada: {password}")
    # ---------------------------

    user = get_user_by_email(email)
    if user:
        hash_bd = user[1].encode()
        if bcrypt.checkpw(password.encode(), hash_bd):
            st.session_state.user = {"email": user[0], "rol": user[2]}
            st.session_state.page = AREA_PAGE[area]
            st.rerun()
        else:
            st.error("Hash no coincide")
    else:
        st.error("Usuario no encontrado en BD")

if st.session_state.get("page"):
    st.switch_page(st.session_state.page)