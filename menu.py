import streamlit as st
from utils.db import buscar_ingresante, registrar_ingresante

# ---------- SEGURIDAD ----------
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("login.py")

# ---------- MAPA OFICIAL (7 roles) ----------
PAGES = {
    "admin": [           # ADMINISTRADOR → todos los módulos
        "pages/1_Triage.py",
        "pages/2_Seguros_SOAT.py",
        "pages/3_Admission.py",
        "pages/4_Farmacia.py",
        "pages/5_Laboratorio.py",
        "pages/6_Radiodiagnostico.py",
    ],
    "triage":    ["pages/1_Triage.py"],
    "seguros":   ["pages/2_Seguros_SOAT.py"],
    "admission": ["pages/3_Admission.py"],
    "farmacia":  ["pages/4_Farmacia.py"],
    "laboratorio":["pages/5_Laboratorio.py"],
    "radiodiagnostico":["pages/6_Radiodiagnostico.py"],
}

# ---------- IDENTIFICACIÓN DEL PERSONAL ----------
if "ingresante" not in st.session_state or st.session_state.ingresante is None:
    st.title("👤 Identificación del Personal Autorizado")
    dni = st.text_input("DNI", max_chars=15).strip()
    if dni:
        data = buscar_ingresante(dni)
        if data:
            st.session_state.ingresante = {"dni": data[0], "nombre": data[1], "cargo": data[2]}
            st.rerun()
        else:
            nombre = st.text_input("Nombres y apellidos completos")
            cargo = st.text_input("Cargo o rol en el hospital")
            if st.button("Registrar como ingresante"):
                if nombre.strip() and cargo.strip() and registrar_ingresante(dni, nombre, cargo):
                    st.session_state.ingresante = {"dni": dni, "nombre": nombre, "cargo": cargo}
                    st.rerun()
else:
    # ---------- MENÚ POR ROL ----------
    rol   = st.session_state.user["rol"]
    nombre = st.session_state.ingresante["nombre"]
    st.sidebar.title(f"🧍 {nombre}")

    if rol == "admin":
        st.success("🔓 Modo Administrador – acceso total")
        cols = st.columns(3)
        mods = [
            ("📋 Triaje", "pages/1_Triage.py"),
            ("🧾 Seguros-SOAT", "pages/2_Seguros_SOAT.py"),
            ("🪪 Admission", "pages/3_Admission.py"),
            ("💊 Farmacia", "pages/4_Farmacia.py"),
            ("🧪 Laboratorio", "pages/5_Laboratorio.py"),
            ("📷 Radio Diagnóstico", "pages/6_Radiodiagnostico.py"),
        ]
        for col, (texto, pagina) in zip(cols * 2, mods):
            with col:
                if st.button(texto):
                    st.session_state.page = pagina
                    st.rerun()
    else:
        # Usuario normal → una sola página
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

# ---------- NAVEGACIÓN EXTRA (opcional) ----------
if st.session_state.get("page"):
    st.switch_page(st.session_state.page)