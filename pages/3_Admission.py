import streamlit as st
from utils.db import buscar_paciente, verificar_soat, vincular_paciente_soat, obtener_lista_espera_pendiente, actualizar_estado_lista

# ---------- SEGURIDAD ----------
if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] not in ("admin", "admission"):
    st.switch_page("pages/0_login.py")

st.title("🪪 Módulo Admission / Registro de Paciente y SOAT")
st.markdown("Valide SOAT y complete datos del paciente.")

# ---------- LISTA DE ESPERA ----------
pendientes = obtener_lista_espera_pendiente()
if pendientes:
    st.subheader("📋 Pacientes en espera de validación de SOAT")
    for p in pendientes:
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            if st.button("✅ Atender", key=p["id"]):
                actualizar_estado_lista(p["id"], "atendido")
                st.rerun()
        with col2:
            st.write(f"{p['dni_paciente']} | Prioridad: {p['prioridad']}")
        with col3:
            st.write(f"Hora: {p['created_at']}")
else:
    st.info("No hay pacientes en espera.")

# ---------- REGISTRO / VALIDACIÓN ----------
st.subheader("Registro y validación de SOAT")
with st.form("admission"):
    dni_paciente = st.text_input("DNI del paciente", max_chars=12).strip()
    nombres = st.text_input("Nombres completos").strip()
    apellidos = st.text_input("Apellidos completos").strip()
    placa = st.text_input("Placa del vehículo").upper()
    registrar = st.form_submit_button("Registrar y validar")

if registrar:
    if not (dni_paciente and nombres and apellidos and placa):
        st.error("Complete todos los campos")
    else:
        # 1. Verificar SOAT
        soat = verificar_soat(placa)
        if soat:
            st.success("✅ SOAT vigente encontrado.")
            vincular_paciente_soat(dni_paciente, placa)
            st.info("Paciente registrado y vinculado al SOAT correctamente.")
        else:
            st.error("❌ No se encontró SOAT vigente para esa placa.")

# ---------- BOTÓN VOLVER ----------
if st.button("⬅ Volver al menú"):
    st.switch_page("menu.py")