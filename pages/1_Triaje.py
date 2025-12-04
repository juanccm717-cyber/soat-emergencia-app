import streamlit as st
from utils.db import buscar_paciente, registrar_paciente_triage

if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] != "triage":
    st.switch_page("pages/0_login.py")

st.title("📌 Registro de Paciente (Triaje de Emergencia)")
dni = st.text_input("DNI del paciente", max_chars=12).strip()
if dni:
    data = buscar_paciente(dni)
    if 
        st.success(f"✅ Paciente ya registrado: **{data[1]}**")
    else:
        nombre = st.text_input("Nombres y apellidos completos")
        if st.button("Registrar Paciente"):
            if nombre.strip() and registrar_paciente_triage(dni, nombre):
                st.success(f"✅ Paciente registrado: **{nombre}**")