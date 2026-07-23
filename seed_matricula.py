from database import get_connection

conn = get_connection()
conn.execute("""
    INSERT INTO actividades (
        actividad_tratamiento, areas_intervienen, finalidad, descripcion,
        categoria_titulares, categorias_datos, datos_sensibles, origen_fuente,
        categoria_destinatarios, base_licitud, transferencia_internacional,
        plazo_conservacion, medidas_seguridad, decisiones_automatizadas,
        requiere_eipd, estado
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    "Gestión de matrícula",
    ["Admisión", "TI"],
    "Gestión del proceso de matrícula de estudiantes nuevos y antiguos",
    "Proceso completo de matrícula que involucra datos personales, académicos y socioeconómicos",
    ["Estudiantes", "Postulantes"],
    ["Identificación", "Académicos", "Socioeconómicos"],
    False,
    "Titular",
    ["MINEDUC", "SENCE"],
    "Obligación legal + Consentimiento",
    "No aplica",
    "10 años desde último acceso",
    "Encriptación en reposo, acceso por roles, MFA",
    "No aplica",
    False,
    "activo"
])
conn.close()
print("✅ Gestión de matrícula creada")
