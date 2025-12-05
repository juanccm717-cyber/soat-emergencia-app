import streamlit as st
from utils.db import buscar_paciente, verificar_soat, vincular_paciente_soat

# ---------- SEGURIDAD ----------
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("login.py")

rol = st.session_state.user["rol"]
if rol not in ("admin", "admission", "soat"):
    st.error("⛔ No tienes permiso para acceder a este módulo.")
    if st.button("Volver al menú"):
        st.switch_page("menu.py")
    st.stop()

# ---------- TÍTULO ----------
st.title("📋 Módulo Admission / Registro de Paciente y SOAT")
st.markdown("Complete el formulario para registrar al paciente y verificar su SOAT.")

# ---------- FORMULARIO ----------
with st.form("admission"):
    dni = st.text_input("DNI del paciente", max_chars=15).strip()
    nombres = st.text_input("Nombres completos")
    apellidos = st.text_input("Apellidos completos")
    placa = st.text_input("Placa del vehículo").upper()
    enviar = st.form_submit_button("Registrar")

if enviar:
    if not (dni and nombres and apellidos and placa):
        st.error("Complete todos los campos")
    else:
        # 1. Verificar si el paciente ya existe
        paciente = buscar_paciente(dni)
        if paciente:
            st.warning("⚠️ Paciente ya registrado. Se vinculará SOAT si existe.")
        else:
            st.info("✅ Paciente nuevo. Procediendo a registrar...")

        # 2. Verificar SOAT activo
        soat = verificar_soat(placa)
        if not soat:
            st.error("❌ No se encontró SOAT vigente para esa placa.")
        else:
            # 3. Vincular paciente-SOAT
            ok = vincular_paciente_soat(dni, placa)
            if ok:
                st.success("✅ Paciente registrado y vinculado al SOAT correctamente.")
            else:
                st.error("❌ Error al vincular paciente con SOAT.")

# ---------- BOTÓN VOLVER ----------
if st.button("⬅ Volver al menú"):
    st.switch_page("menu.py")