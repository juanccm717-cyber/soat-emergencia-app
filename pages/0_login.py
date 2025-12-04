import streamlit as st
from utils.db import autenticar_usuario

st.set_page_config(page_title="SOATAPP", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None
if "ingresante" not in st.session_state:
    st.session_state.ingresante = None

st.title("🔐 SOATAPP - Inicio de Sesión")

# Lista de áreas (rol)
roles_nombres = {
    "admission": "Admisión",
    "seguros": "Seguros (Sub-Oficina)",
    "farmacia": "Farmacia",
    "laboratorio": "Laboratorio",
    "radiodiagnostico": "Radiodiagnóstico",
    "triage": "Triaje de Emergencia"
}

rol_seleccionado = st.selectbox(
    "Seleccione su área de trabajo",
    options=list(roles_nombres.keys()),
    format_func=lambda x: roles_nombres[x]
)

# Contraseña fija por área (deben coincidir con las hasheadas en Neon)
contrasenas_area = {
    "admission": "adm2025!",
    "seguros": "seg2025!",
    "farmacia": "far2025!",
    "laboratorio": "lab2025!",
    "radiodiagnostico": "rad2025!",
    "triage": "tri2025!"
}

password = st.text_input("Contraseña", type="password")

if st.button("Iniciar Sesión"):
    # Email ficticio basado en el rol
    email_ficticio = f"{rol_seleccionado}@hospital.com"
    if password == contrasenas_area[rol_seleccionado]:
        user = autenticar_usuario(email_ficticio, password)
        if user:
            st.session_state.user = user
            st.switch_page("pages/1_Triage.py")
        else:
            st.error("❌ Usuario no registrado en la base de datos.")
    else:
        st.error("❌ Contraseña incorrecta para esta área.")