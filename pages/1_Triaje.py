import streamlit as st
from utils.db import buscar_paciente, registrar_paciente, insertar_lista_espera_triaje

# ---------- SEGURIDAD (admin + triaje) ----------
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("pages/0_login.py")
if st.session_state.user["rol"] not in ["admin", "triage"]:
    st.error("⛔ No tienes permiso para este módulo.")
    if st.button("⬅ Volver al menú"):
        st.session_state.page = "pages/7_Dashboard.py"
        st.rerun()
    st.stop()

st.title("📋 Módulo Triaje")
st.markdown("Registre al paciente con prioridad y añádalo a lista de espera.")

with st.form("triaje"):
    dni_paciente = st.text_input("DNI del paciente", max_chars=12).strip()
    apellidos = st.text_input("Apellidos completos").strip()
    nombres = st.text_input("Nombres completos").strip()
    prioridad = st.selectbox("Nivel de prioridad", ["Leve", "Moderada", "Urgente", "Crítica"])
    dni_profesional = st.text_input("DNI del profesional de triaje", max_chars=12).strip()
    enviar = st.form_submit_button("Registrar")

if enviar:
    if not (dni_paciente and apellidos and nombres and prioridad and dni_profesional):
        st.error("Complete todos los campos")
    else:
        existe = buscar_paciente(dni_paciente)
        if existe:
            st.warning("⚠️ Paciente ya registrado.")
        else:
            ok = registrar_paciente(dni_paciente, apellidos, nombres)
            if ok:
                st.success(f"✅ Paciente registrado con prioridad **{prioridad}**.")
                st.info("➡️ Ahora puede ser atendido por Seguros-SOAT o Admisión.")
            else:
                st.error("❌ Error al registrar paciente.")

if st.button("⬅ Volver al Dashboard"):
    st.session_state.page = "pages/7_Dashboard.py"
    st.rerun()