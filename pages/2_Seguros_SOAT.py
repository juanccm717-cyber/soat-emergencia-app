import streamlit as st
from utils.db import extraer_datos_soat, guardar_soat_desde_pdf

if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] != "seguros":
    st.switch_page("pages/0_login.py")

st.title("📄 Subir Certificado SOAT")
uploaded_file = st.file_uploader("Adjunte el PDF del certificado", type=["pdf"])
if uploaded_file:
    datos = extraer_datos_soat(uploaded_file)
    if all([datos["placa"], datos["fecha_vigencia"], datos["compania"], datos["numero_poliza"]]):
        st.success("✅ Datos extraídos del PDF")
        st.write(f"**Placa:** {datos['placa']}")
        st.write(f"**Titular:** {datos['dni_asegurado']}")
        st.write(f"**Compañía:** {datos['compania']}")
        st.write(f"**Póliza:** {datos['numero_poliza']}")
        st.write(f"**Vigente hasta:** {datos['fecha_vigencia']}")
        if st.button("Registrar SOAT"):
            if guardar_soat_desde_pdf(
                datos["placa"],
                datos["dni_asegurado"],
                datos["fecha_vigencia"],
                datos["compania"],
                datos["numero_poliza"]
            ):
                st.success(f"✅ SOAT registrado para placa {datos['placa']}")
    else:
        st.error("❌ No se extrajeron todos los datos del PDF.")