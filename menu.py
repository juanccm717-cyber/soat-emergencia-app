# menu.py
import streamlit as st
from utils.db import buscar_ingresante, registrar_ingresante

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("login.py")

if "ingresante" not in st.session_state or st.session_state.ingresante is None:
    st.title("👤 Identificación del Personal Autorizado")
    dni = st.text_input("DNI", max_chars=15).strip()
    if dni:
        data = buscar_ingresante(dni)
        if 
            st.session_state.ingresante = {"dni": data[0], "nombre": data[1], "cargo": data[2]}
            st.switch_page("pages/1_Triaje.py")
        else:
            nombre = st.text_input("Nombres y apellidos completos")
            cargo = st.text_input("Cargo o rol en el hospital")
            if st.button("Registrar como ingresante"):
                if nombre.strip() and cargo.strip() and registrar_ingresante(dni, nombre, cargo):
                    st.session_state.ingresante = {"dni": dni, "nombre": nombre, "cargo": cargo}
                    st.switch_page("pages/1_Triaje.py")
else:
    st.sidebar.title(f"🧍 {st.session_state.ingresante['nombre']}")
    rol = st.session_state.user["rol"]
    if rol == "triage":
        st.switch_page("pages/1_Triaje.py")
    elif rol == "seguros":
        st.switch_page("pages/2_Seguros_SOAT.py")
    elif rol == "admission":
        st.switch_page("pages/3_Admission.py")
    else:
        st.info("🟢 Bienvenido. No tienes módulos asignados.")
        if st.button("Cerrar Sesión"):
            st.session_state.clear()
            st.switch_page("login.py")