import streamlit as st
from utils.db import verificar_soat, obtener_lista_espera_pendiente, actualizar_estado_lista, vincular_paciente_soat

# ---------- SEGURIDAD ----------
if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] != "SEGUROS-SOAT":
    st.switch_page("pages/0_login.py")

st.title("🧾 Módulo Seguros-SOAT")
st.markdown("Valide el SOAT del vehículo y atienda pacientes en espera.")

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

# ---------- VALIDACIÓN DE SOAT ----------
st.subheader("Validar SOAT")
with st.form("valida_soat"):
    dni_paciente = st.text_input("DNI del paciente").strip()
    placa = st.text_input("Placa del vehículo").upper()
    validar = st.form_submit_button("Validar SOAT")

if validar:
    if not (dni_paciente and placa):
        st.error("Complete ambos campos")
    else:
        soat = verificar_soat(placa)
        if soat:
            st.success("✅ SOAT vigente encontrado.")
            vincular_paciente_soat(dni_paciente, placa)
            st.info("Paciente vinculado al SOAT correctamente.")
        else:
            st.error("❌ No se encontró SOAT vigente para esa placa.")

# ---------- BOTÓN VOLVER ----------
if st.button("⬅ Volver al menú"):
    st.switch_page("menu.py")