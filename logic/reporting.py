import httpx
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


# ================= Estilos =================
styles = getSampleStyleSheet()

estilo_encabezado = ParagraphStyle(
    "Encabezado",
    parent=styles["Heading1"],
    alignment=TA_CENTER,
    fontSize=20,
    spaceAfter=20,
    textColor=colors.darkblue
)

estilo_subtitulo = ParagraphStyle(
    "Subtitulo",
    parent=styles["Heading2"],
    spaceAfter=10,
    fontSize=14,
    textColor=colors.white,
    backColor=colors.darkblue,
    leftIndent=5,
    rightIndent=5,
    alignment=TA_LEFT
)

estilo_normal = ParagraphStyle(
    "Normal",
    parent=styles["Normal"],
    fontSize=12,
    spaceAfter=8
)

# ================= Funciones HTTP =================
def obtener_datos_usuario(cedula):
    url = f"http://localhost:3000/usuario/get/{cedula}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print("Error usuario:", e)
        return None

def obtener_diagnosticos_usuario(cedula):
    url = f"http://localhost:3000/historial/get/{cedula}"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
        response.raise_for_status()
        return response.json().get("data", [])
    except httpx.HTTPError as e:
        print("Error diagnósticos:", e)
        return []

def obtener_progreso_usuario(cedula):
    url = f"http://localhost:3000/historial/get/{cedula}/progreso"
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
        response.raise_for_status()
        return response.json().get("data", [])
    except httpx.HTTPError as e:
        print("Error progreso:", e)
        return []

# ================= Generar PDF bonito =================
def generar_pdf_paciente(cedula):
    usuario = obtener_datos_usuario(cedula)
    diagnosticos = obtener_diagnosticos_usuario(cedula)
    progreso = obtener_progreso_usuario(cedula)

    ruta_archivo = f"reporte_{cedula}.pdf"
    doc = SimpleDocTemplate(ruta_archivo, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    elementos = []

    # ===== Título =====
    elementos.append(Paragraph("Reporte Médico del Paciente", estilo_encabezado))
    elementos.append(Spacer(1, 10))

    # ===== Datos del paciente =====
    if usuario:
        datos_html = f"""
        <b>Nombre:</b> {usuario.get('nombre', 'N/A')} {usuario.get('apellido', 'N/A')}<br/>
        <b>Edad:</b> {usuario.get('edad', 'N/A')}<br/>
        <b>Sexo:</b> {usuario.get('sexo', 'N/A')}<br/>
        <b>Cédula:</b> {usuario.get('identificacion', 'N/A')}<br/>
        <b>Correo:</b> {usuario.get('correo', 'N/A')}<br/>
        """
        elementos.append(Paragraph(datos_html, estilo_normal))
        elementos.append(Spacer(1, 15))

    # ===== Diagnósticos =====
    elementos.append(Paragraph("Diagnósticos", estilo_subtitulo))
    elementos.append(Spacer(1, 5))
    if diagnosticos:
        for diag in diagnosticos:
            diag_data = diag.get("diagnostico", {})
            nombre = diag_data.get("nombre", "N/A")
            gravedad = diag_data.get("nivel_gravedad", "")
            descripcion = diag_data.get("descripcion", "")
            recomendaciones = diag_data.get("recomendaciones", "")

            elementos.append(Paragraph(f"<b>{nombre}</b> (Gravedad: {gravedad})", estilo_normal))
            elementos.append(Paragraph(f"<b>Descripción:</b> {descripcion}", estilo_normal))
            elementos.append(Paragraph(f"<b>Recomendaciones:</b> {recomendaciones}", estilo_normal))
            elementos.append(Spacer(1, 10))
    else:
        elementos.append(Paragraph("No hay diagnósticos registrados.", estilo_normal))
        elementos.append(Spacer(1, 10))

    # ===== Progreso =====
    elementos.append(Paragraph("Progreso del paciente", estilo_subtitulo))
    elementos.append(Spacer(1, 5))
    if progreso:
        registros = progreso[0].get("progreso", []) if len(progreso) > 0 else []
        if registros:
            # Crear tabla con colores
            data_tabla = [["Fecha", "Progreso"]]
            for reg in registros:
                data_tabla.append([reg.get("fecha", ""), reg.get("progreso", "")])
            tabla = Table(data_tabla, colWidths=[150, 350])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elementos.append(tabla)
            elementos.append(Spacer(1, 10))
        else:
            elementos.append(Paragraph("No hay progreso registrado.", estilo_normal))
            elementos.append(Spacer(1, 10))
    else:
        elementos.append(Paragraph("No hay progreso registrado.", estilo_normal))
        elementos.append(Spacer(1, 10))

    # ===== Mensaje final =====
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph("💙 Mensaje de recuperación", estilo_subtitulo))
    elementos.append(Paragraph("Le deseamos una pronta recuperación. ¡Ánimo y mucha fuerza!", estilo_normal))

    doc.build(elementos)
    return ruta_archivo


# =============== 3. Enviar por correo ==================
def enviar_pdfs(destinatario, remitente, clave, archivos_pdf):
    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = "📩 Reportes Médicos de Pacientes"

    cuerpo = "Hola,\n\nAdjunto encontrarás los reportes médicos generados.\n\nSaludos."
    msg.attach(MIMEText(cuerpo, "plain"))

    # Adjuntar cada PDF
    for archivo in archivos_pdf:
        with open(archivo, "rb") as f:
            adjunto = MIMEApplication(f.read(), Name=archivo)
            adjunto["Content-Disposition"] = f'attachment; filename="{archivo}"'
            msg.attach(adjunto)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(remitente, clave)  # contraseña de aplicación
        server.send_message(msg)

    print(f"✅ Correo enviado a {destinatario} con {len(archivos_pdf)} PDF(s).")

