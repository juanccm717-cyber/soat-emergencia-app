import streamlit as st
from utils.db import buscar_ingresante, registrar_ingresante

# Si no hay usuario logueado → login
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("login.py")

# Slug de rol (triage, seguros, admission, etc.)
rol = st.session_state.user["rol"]

# Si no hay ingresante → pedir DNI
if "ingresante" not in st.session_state or st.session_state.ingresante is None:
    st.title("👤 Identificación del Personal Autorizado")
    dni = st.text_input("DNI", max_chars=15).strip()
    if dni:
        data = buscar_ingresante(dni)
        if data:  # <-- aquí faltaba la condición
            st.session_state.ingresante = {"dni": data[0], "nombre": data[1], "cargo": data[2]}
            st.rerun()  # obligatorio para redirigir
        else:
            nombre = st.text_input("Nombres y apellidos completos")
            cargo = st.text_input("Cargo o rol en el hospital")
            if st.button("Registrar como ingresante"):
                if nombre.strip() and cargo.strip() and registrar_ingresante(dni, nombre, cargo):
                    st.session_state.ingresante = {"dni": dni, "nombre": nombre, "cargo": cargo}
                    st.rerun()  # obligatorio
else:
    # Mostrar sidebar y redirigir según rol
    st.sidebar.title(f"🧍 {st.session_state.ingresante['nombre']}")
    destino = {
        "triage": "pages/1_Triage.py",
        "seguros": "pages/2_Seguros_SOAT.py",
        "admission": "pages/3_Admission.py",
        "farmacia": "pages/4_Farmacia.py",
        "laboratorio": "pages/5_Laboratorio.py",
        "radiodiagnostico": "pages/6_Radiodiagnostico.py",
    }.get(rol)

    if destino:
        st.switch_page(destino)
    else:
        st.info("🟢 Bienvenido. No tienes módulos asignados.")
        if st.button("Cerrar Sesión"):
            st.session_state.clear()
            st.rerun()