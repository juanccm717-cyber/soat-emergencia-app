import streamlit as st

if "user" not in st.session_state or st.session_state.user is None or st.session_state.user["rol"] != "farmacia":
    st.switch_page("pages/0_login.py")

st.title("💊 Farmacia")
st.info("Módulo en desarrollo. Próximamente: dispensación autorizada por SOAT.")