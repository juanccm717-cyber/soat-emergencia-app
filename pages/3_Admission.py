# pages/3_Admission.py
import streamlit as st
from utils.db import buscar_paciente, verificar_soat, vincular_paciente_soat

if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] != "admission":
    st.switch_page("login.py")

st.title("🔗 Vincular SOAT con Nota de Ingreso")
dni = st.text_input("DNI del paciente (registrado en Triaje)", max_chars=12).strip()
if dni:
    paciente = buscar_paciente(dni)
    if paciente:
        st.write(f"**Paciente:** {paciente[1]}")
        placa = st.text_input("Placa SOAT (registrada)").strip().upper()
        if placa and verificar_soat(placa):
            nota = st.text_input("Número de nota de ingreso").strip()
            if st.button("Vincular"):
                if nota and vincular_paciente_soat(dni, placa, nota):
                    st.success("✅ Vinculación exitosa")
        elif placa:
            st.error("❌ Placa SOAT no registrada o vencida.")
    else:
        st.error("❌ Paciente no registrado en Triaje.")