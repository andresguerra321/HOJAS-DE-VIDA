import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors


def generar_cv_senior(ruta_archivo: str):
    """Genera un CV de un desarrollador Python Backend Senior con alto ajuste."""
    doc = SimpleDocTemplate(
        ruta_archivo,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563eb'),
        fontName='Helvetica-Bold',
        spaceAfter=12
    )
    seccion_style = ParagraphStyle(
        'Seccion',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    cuerpo_style = ParagraphStyle(
        'Cuerpo',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    story = []

    # Encabezado
    story.append(Paragraph("Carlos Andrés Mendoza Rivas", titulo_style))
    story.append(Paragraph("Ingeniero de Software Senior | Especialista Backend Python & Cloud", subtitulo_style))
    story.append(Paragraph("Bucaramanga, Colombia • Tel: +57 315 889 0123 • Email: carlos.mendoza@email.com • GitHub: github.com/cmendoza", cuerpo_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=10))

    # Perfil Profesional
    story.append(Paragraph("PERFIL PROFESIONAL", seccion_style))
    story.append(Paragraph(
        "Ingeniero de Sistemas con más de 4 años de experiencia profesional sólida en desarrollo backend, "
        "diseño de microservicios e integración de arquitecturas escalables. Experto en Python (FastAPI, Flask, Django), "
        "bases de datos relacionales (PostgreSQL, MySQL), APIs RESTful seguras y despliegues con Docker y Kubernetes. "
        "Pionero en la implementación de asistentes inteligentes y flujos RAG con LangChain en entornos de producción.",
        cuerpo_style
    ))
    story.append(Spacer(1, 8))

    # Experiencia Laboral
    story.append(Paragraph("EXPERIENCIA LABORAL", seccion_style))
    story.append(Paragraph("<b>TechSolutions Latam</b> | Desarrollador Backend Senior (2022 - Presente)", cuerpo_style))
    story.append(Paragraph(
        "• Diseñó y lideró la arquitectura de microservicios con FastAPI y PostgreSQL, procesando más de 2 millones de peticiones diarias.<br/>"
        "• Desarrolló e integró APIs RESTful seguras con autenticación JWT, reducción del tiempo de respuesta en un 38%.<br/>"
        "• Implementó pipelines de CI/CD automatizados con Docker, GitHub Actions y despliegue en AWS.<br/>"
        "• Diseñó servicios con integración de modelos LLM y LangChain para consulta semántica de documentos corporativos.",
        cuerpo_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Innovación Digital S.A.S.</b> | Desarrollador Python Backend (2020 - 2022)", cuerpo_style))
    story.append(Paragraph(
        "• Construcción y mantenimiento de endpoints REST para plataformas de e-commerce y pagos en línea.<br/>"
        "• Optimización de consultas complejas e indexación avanzada en PostgreSQL.<br/>"
        "• Implementación de pruebas automatizadas unitarias y de integración con pytest, alcanzando un 88% de cobertura de código.",
        cuerpo_style
    ))
    story.append(Spacer(1, 8))

    # Educación
    story.append(Paragraph("EDUCACIÓN Y CERTIFICACIONES", seccion_style))
    story.append(Paragraph("<b>Ingeniería de Sistemas e Informática</b> — Universidad Industrial de Santander (UIS), 2019", cuerpo_style))
    story.append(Paragraph("• Certificación: AWS Certified Solutions Architect - Associate (2023)", cuerpo_style))
    story.append(Paragraph("• Diplomado en Inteligencia Artificial Generativa y Procesamiento de Lenguaje Natural (2024)", cuerpo_style))
    story.append(Spacer(1, 8))

    # Habilidades Técnicas
    story.append(Paragraph("HABILIDADES TÉCNICAS", seccion_style))
    story.append(Paragraph(
        "<b>Lenguajes y Frameworks:</b> Python, FastAPI, Django, Flask, SQL, Shell Scripting.<br/>"
        "<b>Bases de Datos:</b> PostgreSQL (avanzado), Redis, SQLite, MongoDB.<br/>"
        "<b>Herramientas & DevOps:</b> Docker, Docker Compose, Git, GitHub Actions, Linux, Postman.<br/>"
        "<b>IA & Automatización:</b> LangChain, OpenAI API, Embeddings vectoriales, n8n.<br/>"
        "<b>Pruebas y Metodologías:</b> Pytest, TDD, Clean Code, Scrum, REST API Design.",
        cuerpo_style
    ))

    doc.build(story)
    print(f"CV Senior generado: {ruta_archivo}")


def generar_cv_junior(ruta_archivo: str):
    """Genera un CV de un perfil Junior/Frontend con ajuste moderado/bajo a backend senior."""
    doc = SimpleDocTemplate(
        ruta_archivo,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0891b2'),
        fontName='Helvetica-Bold',
        spaceAfter=12
    )
    seccion_style = ParagraphStyle(
        'Seccion',
        parent=styles['Heading2'],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    cuerpo_style = ParagraphStyle(
        'Cuerpo',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    story = []

    # Encabezado
    story.append(Paragraph("Laura Sofía Gómez Morales", titulo_style))
    story.append(Paragraph("Desarrolladora Web Junior | Especialidad Frontend & UI", subtitulo_style))
    story.append(Paragraph("Medellín, Colombia • Tel: +57 301 223 4455 • Email: laura.gomez@email.com", cuerpo_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=10))

    # Perfil
    story.append(Paragraph("PERFIL PROFESIONAL", seccion_style))
    story.append(Paragraph(
        "Desarrolladora con 1 año de experiencia enfocada principalmente en desarrollo frontend, "
        "maquetación web responsiva con React, HTML5 y CSS3. Conocimientos iniciales de Python para scripts "
        "sencillos y consumo de servicios web. Interesada en aprender buenas prácticas de backend y bases de datos relacionales.",
        cuerpo_style
    ))
    story.append(Spacer(1, 8))

    # Experiencia
    story.append(Paragraph("EXPERIENCIA LABORAL", seccion_style))
    story.append(Paragraph("<b>Agencia Digital WebCreativa</b> | Desarrolladora Frontend Junior (2023 - Presente)", cuerpo_style))
    story.append(Paragraph(
        "• Creación de interfaces de usuario interactivas con React y Tailwind CSS.<br/>"
        "• Consumo de APIs REST existentes desarrolladas por el equipo backend.<br/>"
        "• Resolución de incidencias visuales y compatibilidad cross-browser.<br/>"
        "• Colaboración en repositorios Git mediante pull requests.",
        cuerpo_style
    ))
    story.append(Spacer(1, 8))

    # Educación
    story.append(Paragraph("EDUCACIÓN", seccion_style))
    story.append(Paragraph("<b>Tecnología en Desarrollo de Software</b> — Instituto Tecnológico Metropolitano (2023)", cuerpo_style))
    story.append(Paragraph("• Curso de Fundamentos de Programación en Python (60 horas, 2023)", cuerpo_style))
    story.append(Spacer(1, 8))

    # Habilidades
    story.append(Paragraph("HABILIDADES TÉCNICAS", seccion_style))
    story.append(Paragraph(
        "<b>Frontend:</b> JavaScript, React, HTML5, CSS3, Tailwind CSS.<br/>"
        "<b>Backend & Bases de Datos:</b> Python básico (scripts), nociones básicas de SQLite y MySQL.<br/>"
        "<b>Herramientas:</b> Git, VS Code, Figma, Postman (básico).",
        cuerpo_style
    ))

    doc.build(story)
    print(f"CV Junior generado: {ruta_archivo}")


if __name__ == "__main__":
    carpeta_destino = os.path.join(os.path.dirname(__file__), "ejemplos_cv")
    os.makedirs(carpeta_destino, exist_ok=True)

    cv_senior = os.path.join(carpeta_destino, "cv_carlos_mendoza_backend_senior.pdf")
    cv_junior = os.path.join(carpeta_destino, "cv_laura_gomez_frontend_junior.pdf")

    generar_cv_senior(cv_senior)
    generar_cv_junior(cv_junior)
    print("¡Archivos de prueba generados en la carpeta ejemplos_cv!")

