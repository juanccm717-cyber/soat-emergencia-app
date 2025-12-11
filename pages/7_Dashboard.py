import streamlit as st

# ---------- SEGURIDAD ----------
if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] != "admin":
    st.switch_page("pages/0_login.py")

st.title("🔓 Panel de Administrador")
st.markdown("Acceso total a todos los módulos y estadísticas.")

cols = st.columns(3)
mods = [
    ("📋 Triaje", "pages/1_Triaje.py"),
    ("🧾 Seguros-SOAT", "pages/2_Seguros_SOAT.py"),
    ("🪪 Admission", "pages/3_Admission.py"),
    ("💊 Farmacia", "pages/4_Farmacia.py"),
    ("🧪 Laboratorio", "pages/5_Laboratorio.py"),
    ("📷 Radio Diagnóstico", "pages/6_Radiodiagnostico.py"),
]

for col, (texto, pagina) in zip(cols * 2, mods):
    with col:
        if st.button(texto, key=texto):
            st.session_state.page = pagina
            st.rerun()

if st.button("⬅ Cerrar Sesión"):
    st.session_state.clear()
    st.rerun()