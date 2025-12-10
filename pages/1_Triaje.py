import streamlit as st
from utils.db import buscar_paciente, registrar_paciente_triage, insertar_lista_espera_triaje

# ---------- SEGURIDAD ----------
if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] != "TRIAJE":
    st.switch_page("pages/0_login.py")

# ---------- TÍTULO ----------
st.title("📌 Registro de Paciente (Triaje de Emergencia)")
st.markdown("**Orden de ingreso**: este registro **inicia** el proceso hospitalario.")

# ---------- FORMULARIO ----------
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
            st.warning("⚠️ Paciente ya registrado en triaje.")
        else:
            ok = registrar_paciente_triage(dni_paciente, apellidos, nombres, prioridad, dni_profesional)
            if ok:
                lista_ok = insertar_lista_espera_triaje(dni_paciente, prioridad, dni_profesional)
                if lista_ok:
                    st.success(f"✅ Paciente registrado con prioridad **{prioridad}** y **añadido a lista de espera**.")
                    st.info("➡️ Ahora puede ser atendido por **Seguros-SOAT** o **Admisión** para validar su SOAT.")
                else:
                    st.error("❌ Error al añadir a lista de espera.")
            else:
                st.error("❌ Error al registrar paciente.")

# ---------- BOTÓN VOLVER ----------
if st.button("⬅ Volver al menú"):
    st.switch_page("menu.py")