import bcrypt

# Contraseñas por área (puedes cambiarlas)
contrasenas = {
    "admission@hospital.com": "adm2025!",
    "seguros@hospital.com": "seg2025!",
    "farmacia@hospital.com": "far2025!",
    "laboratorio@hospital.com": "lab2025!",
    "radiodiag@hospital.com": "rad2025!",
    "triage@hospital.com": "tri2025!"
}

for email, pwd in contrasenas.items():
    hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"UPDATE usuarios SET password_hash = '{hashed}' WHERE email = '{email}';")