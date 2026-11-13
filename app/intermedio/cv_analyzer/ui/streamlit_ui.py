import html
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    from models.cv_model import AnalisisCV
    from services.pdf_processor import MAX_TAMANO_BYTES, extraer_texto_pdf
    from services.cv_evaluator import crear_evaluador_cv, evaluar_candidato
except (ImportError, ModuleNotFoundError):
    from app.intermedio.cv_analyzer.models.cv_model import AnalisisCV
    from app.intermedio.cv_analyzer.services.pdf_processor import MAX_TAMANO_BYTES, extraer_texto_pdf
    from app.intermedio.cv_analyzer.services.cv_evaluator import crear_evaluador_cv, evaluar_candidato


# Descripción de puesto de ejemplo para pruebas rápidas
EJEMPLO_VACANTE = """Puesto: Desarrollador Python Backend Senior
Requisitos obligatorios:
- Al menos 3 años de experiencia en desarrollo backend con Python.
- Experiencia sólida en diseño, construcción y consumo de APIs REST.
- Manejo de bases de datos relacionales, preferiblemente PostgreSQL.
- Conocimientos en arquitectura de software y buenas prácticas de programación.
- Uso de Git y flujo de trabajo colaborativo.

Requisitos deseables:
- Manejo de contenedores Docker y Docker Compose.
- Pruebas unitarias y automatizadas con pytest.
- Familiaridad con modelos de lenguaje LLM, LangChain o herramientas de IA Generativa.
- Experiencia en despliegue en la nube.

Responsabilidades principales:
- Diseñar e implementar microservicios y endpoints seguros y escalables.
- Integrar APIs externas y flujos automatizados de datos.
- Escribir código limpio, documentado y con cobertura de pruebas.
- Colaborar en la definición de soluciones técnicas y arquitecturas."""

SIDEBAR_SVG_ICON = """
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
    <svg width="44" height="44" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect width="48" height="48" rx="12" fill="#0F172A"/>
        <path d="M15 11H28L35 18V36C35 37.6569 33.6569 39 32 39H15C13.3431 39 12 37.6569 12 36V14C12 12.3431 13.3431 11 15 11Z" fill="#F8FAFC"/>
        <path d="M28 11V18H35L28 11Z" fill="#94A3B8"/>
        <circle cx="21" cy="23" r="3" fill="#2563EB"/>
        <path d="M16.5 31C16.5 28.5147 18.5147 26.5 21 26.5C23.4853 26.5 25.5 28.5147 25.5 31" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round"/>
        <line x1="27.5" y1="22" x2="31" y2="22" stroke="#64748B" stroke-width="2" stroke-linecap="round"/>
        <line x1="27.5" y1="26" x2="31" y2="26" stroke="#64748B" stroke-width="2" stroke-linecap="round"/>
        <line x1="16" y1="34.5" x2="31" y2="34.5" stroke="#CBD5E1" stroke-width="2" stroke-linecap="round"/>
    </svg>
    <div>
        <div style="font-size:1.15rem; font-weight:700; line-height:1.2;">CV Analyzer</div>
        <div style="font-size:0.8rem; opacity:0.75;">Evaluación con IA</div>
    </div>
</div>
"""


def obtener_evaluacion_principal(porcentaje: int) -> tuple[str, str]:
    """Retorna la etiqueta y color para la evaluación principal."""
    if porcentaje >= 80:
        return "Excelente", "#10b981"  # Verde
    elif porcentaje >= 60:
        return "Bueno", "#3b82f6"      # Azul
    elif porcentaje >= 40:
        return "Regular", "#f59e0b"    # Ámbar
    else:
        return "Bajo", "#ef4444"       # Rojo


def obtener_recomendacion_final(porcentaje: int) -> tuple[str, str, str]:
    """Retorna la recomendación de contratación según los umbrales definidos."""
    if porcentaje >= 70:
        return "Candidato recomendado", "✅", "#10b981"
    elif porcentaje >= 50:
        return "Candidato con potencial", "⚠️", "#f59e0b"
    else:
        return "Candidato no recomendado", "❌", "#ef4444"


def obtener_ejemplos_cv_disponibles() -> dict[str, Path]:
    """Descubre los archivos PDF de demostración en la carpeta ejemplos_cv/."""
    carpeta_ejemplos = Path(__file__).resolve().parents[4] / "ejemplos_cv"
    if not carpeta_ejemplos.is_dir():
        return {}

    etiquetas = {
        "cv_carlos_mendoza_backend_senior.pdf": "Carlos Mendoza — Backend Senior (Demo)",
        "cv_laura_gomez_frontend_junior.pdf": "Laura Gómez — Frontend Junior (Demo)",
    }
    disponibles: dict[str, Path] = {}
    for pdf_path in sorted(carpeta_ejemplos.glob("*.pdf")):
        etiqueta = etiquetas.get(pdf_path.name, f"{pdf_path.stem} (Demo)")
        disponibles[etiqueta] = pdf_path
    return disponibles


def generar_informe_markdown(
    analisis: AnalisisCV,
    eval_principal: str,
    recom_texto: str
) -> str:
    """Genera un informe descargable en formato Markdown con los resultados de evaluación."""
    habilidades = "\n".join(f"- {h}" for h in analisis.habilidades_clave) or "- No especificadas"
    fortalezas = "\n".join(f"- {f}" for f in analisis.fortalezas) or "- Sin registros"
    areas_mejora = "\n".join(f"- {m}" for m in analisis.areas_mejora) or "- Sin brechas críticas"

    return f"""# Informe de Evaluación de Candidato

- **Candidato:** {analisis.nombre_candidato}
- **Porcentaje de ajuste:** {analisis.porcentaje_ajuste}%
- **Nivel de evaluación:** {eval_principal}
- **Recomendación:** {recom_texto}
- **Experiencia relevante:** {analisis.experiencia_años} años

## Formación Académica
{analisis.education}

## Resumen de Experiencia Relevante
{analisis.experiencia_relevante}

## Habilidades Clave
{habilidades}

## Principales Fortalezas
{fortalezas}

## Áreas de Oportunidad y Brechas
{areas_mejora}
"""


def _inicializar_estado():
    """Inicializa las claves requeridas en st.session_state."""
    if "analisis_actual" not in st.session_state:
        st.session_state.analisis_actual = None
    if "texto_cv_extraido" not in st.session_state:
        st.session_state.texto_cv_extraido = ""
    if "input_descripcion_puesto" not in st.session_state:
        st.session_state.input_descripcion_puesto = ""
    if "uploader_key_id" not in st.session_state:
        st.session_state.uploader_key_id = 0
    if "cv_demo_seleccionado" not in st.session_state:
        st.session_state.cv_demo_seleccionado = "Ninguno (usar archivo subido)"


def cargar_ejemplo_vacante():
    """Callback para poblar el campo de descripción de vacante con un ejemplo."""
    st.session_state["input_descripcion_puesto"] = EJEMPLO_VACANTE


def limpiar_formulario():
    """Callback para reiniciar completamente el formulario, archivo y análisis."""
    st.session_state.analisis_actual = None
    st.session_state.texto_cv_extraido = ""
    st.session_state["input_descripcion_puesto"] = ""
    st.session_state["cv_demo_seleccionado"] = "Ninguno (usar archivo subido)"
    st.session_state.uploader_key_id += 1


def main():
    st.set_page_config(
        page_title="Analizador de Currículums con IA",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Estilos CSS con contraste explícito compatible con modo claro y modo oscuro
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f8fafc;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.82rem;
        color: #475569;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .metric-sub {
        color: #475569;
        font-size: 0.8rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        margin: 4px 4px 4px 0;
        border-radius: 9999px;
        background-color: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .fortaleza-item {
        background-color: #f0fdf4;
        color: #14532d;
        border-left: 4px solid #22c55e;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-size: 0.95rem;
    }
    .mejora-item {
        background-color: #fffbeb;
        color: #78350f;
        border-left: 4px solid #f59e0b;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-size: 0.95rem;
    }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #f8fafc;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

    _inicializar_estado()
    ejemplos_cv = obtener_ejemplos_cv_disponibles()

    # ==========================
    # BARRA LATERAL (Configuración)
    # ==========================
    with st.sidebar:
        st.markdown(SIDEBAR_SVG_ICON, unsafe_allow_html=True)
        st.caption("Ajustes del modelo y evaluación")

        default_idx = 1 if (
            not os.getenv("OPENAI_API_KEY")
            and (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        ) else 0

        proveedor = st.selectbox(
            "Proveedor de IA",
            options=["OpenAI", "Google Gemini"],
            index=default_idx,
            help="Selecciona el proveedor del modelo de lenguaje."
        )

        if proveedor == "OpenAI":
            modelo = st.selectbox(
                "Modelo OpenAI",
                options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                index=0
            )
            env_key = os.getenv("OPENAI_API_KEY", "")
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=env_key,
                help="Clave de API de OpenAI (almacenada únicamente en memoria durante la sesión)"
            )
        else:
            modelo = st.selectbox(
                "Modelo Gemini",
                options=["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"],
                index=0
            )
            env_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
            api_key = st.text_input(
                "Google Gemini API Key",
                type="password",
                value=env_key,
                help="Clave de API de Google Gemini (almacenada únicamente en memoria durante la sesión)"
            )

        temperatura = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05,
            help="Valores bajos (0.1 - 0.3) garantizan análisis objetivos y determinísticos."
        )

        st.divider()

        with st.expander("ℹ️ Criterios de Ponderación"):
            st.markdown("""
            El modelo calcula el porcentaje de ajuste evaluando:
            - **Experiencia relevante:** 40%
            - **Habilidades técnicas:** 35%
            - **Formación y certificaciones:** 15%
            - **Coherencia profesional:** 10%
            """)

        with st.expander("📊 Escala de Calificación"):
            st.markdown("""
            **Evaluación Principal:**
            - **80 – 100%:** 🟢 Excelente
            - **60 – 79%:** 🔵 Bueno
            - **40 – 59%:** 🟡 Regular
            - **0 – 39%:** 🔴 Bajo

            **Recomendación Final:**
            - **70 – 100%:** ✅ Recomendado
            - **50 – 69%:** ⚠️ Con potencial
            - **0 – 49%:** ❌ No recomendado
            """)

        with st.expander("🔒 Seguridad & Privacidad"):
            st.markdown("""
            - **Protección Anti-Prompt Injection:** Aislamiento de datos con etiquetas y directrices de rechazo de órdenes dentro del CV.
            - **Límite DoS:** Máximo 10 MB y 20 páginas por documento.
            - **Sanitización XSS:** Escape de entidades HTML antes de renderizar.
            - **Habeas Data:** Las credenciales y textos no se almacenan de forma permanente sin autorización previa.
            """)

        st.divider()

        st.button(
            "🗑️ Limpiar todo / Reiniciar",
            use_container_width=True,
            on_click=limpiar_formulario
        )

    # ==========================
    # ENCABEZADO PRINCIPAL
    # ==========================
    st.markdown("""
    <div class="header-box">
        <h1 style="margin:0; font-size: 2rem; color: #f8fafc;">📋 Analizador de Currículums con Inteligencia Artificial</h1>
        <p style="margin-top: 8px; margin-bottom: 0; color: #cbd5e1; font-size: 1.05rem;">
            Compara objetivamente un currículum en PDF frente a la descripción de un puesto mediante
            extracción inteligente, modelos LLM y análisis estructurado.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================
    # SECCIÓN DE ENTRADA
    # ==========================
    col_izq, col_der = st.columns([1, 1], gap="large")

    with col_izq:
        st.subheader("1. Currículum Vitae (PDF)")
        archivo_cargado = st.file_uploader(
            "Carga el archivo PDF del candidato (máx. 10 MB, hasta 20 páginas)",
            type=["pdf"],
            key=f"pdf_uploader_{st.session_state.uploader_key_id}",
            help="Sube un archivo en formato PDF con texto seleccionable. Documentos escaneados como imagen sin OCR no son procesables."
        )

        if archivo_cargado:
            tam_kb = round(archivo_cargado.size / 1024, 1)
            if archivo_cargado.size > MAX_TAMANO_BYTES:
                st.error("❌ El archivo supera el tamaño máximo permitido de 10 MB por motivos de seguridad.")
            else:
                st.success(f"📄 Archivo cargado: **{html.escape(archivo_cargado.name)}** ({tam_kb} KB)")

        ruta_demo_seleccionada = None
        if ejemplos_cv:
            opciones_demo = ["Ninguno (usar archivo subido)"] + list(ejemplos_cv.keys())
            if st.session_state.cv_demo_seleccionado not in opciones_demo:
                st.session_state.cv_demo_seleccionado = "Ninguno (usar archivo subido)"

            seleccion_demo = st.selectbox(
                "O prueba rápidamente con un CV de demostración:",
                options=opciones_demo,
                key="cv_demo_seleccionado",
                help="Permite evaluar inmediatamente la aplicación sin subir un archivo externo."
            )
            if seleccion_demo != "Ninguno (usar archivo subido)":
                ruta_demo_seleccionada = ejemplos_cv[seleccion_demo]
                if archivo_cargado:
                    st.info("ℹ️ Se priorizará el archivo PDF que subiste arriba sobre el CV de demostración.")
                else:
                    st.info(f"📄 Usando CV de demostración: **{html.escape(ruta_demo_seleccionada.name)}**")

    with col_der:
        st.subheader("2. Descripción del Puesto y Requisitos")

        col_desc_header, col_btn_ejemplo = st.columns([3, 2])
        with col_btn_ejemplo:
            st.button(
                "📝 Cargar vacante de ejemplo",
                help="Llena el campo con un perfil de Desarrollador Python",
                on_click=cargar_ejemplo_vacante
            )

        descripcion_puesto = st.text_area(
            "Ingresa los requisitos, experiencia, habilidades y responsabilidades buscadas:",
            height=200,
            placeholder="Puesto: Ingeniero de Software...\nRequisitos obligatorios: 3 años de experiencia...\nHabilidades técnicas: Python, APIs, SQL...",
            key="input_descripcion_puesto"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================
    # BOTÓN DE ANÁLISIS
    # ==========================
    btn_analizar = st.button(
        "🔍 Analizar Candidato",
        type="primary",
        use_container_width=True
    )

    if btn_analizar:
        fuente_pdf = archivo_cargado if archivo_cargado is not None else (
            str(ruta_demo_seleccionada) if ruta_demo_seleccionada is not None else None
        )

        if fuente_pdf is None:
            st.error("⚠️ Debes cargar un archivo PDF o seleccionar un CV de demostración.")
            return

        if not descripcion_puesto or not descripcion_puesto.strip():
            st.error("⚠️ Debes ingresar la descripción y requisitos de la vacante.")
            return

        if not api_key or not api_key.strip():
            st.error(
                f"⚠️ Falta la clave de API para {proveedor}. "
                "Por favor ingrésala en la barra lateral o configúrala en el archivo .env."
            )
            return

        # Paso 1: Extracción de texto del PDF con controles de seguridad
        with st.status("Procesando documento PDF con controles de seguridad...", expanded=True) as status:
            st.write("Verificando integridad y extrayendo texto...")
            resultado_pdf = extraer_texto_pdf(fuente_pdf)

            if resultado_pdf.es_error:
                status.update(label="Fallo en la lectura del PDF", state="error", expanded=True)
                st.error(f"❌ {resultado_pdf.error}")
                return

            texto_cv = resultado_pdf.texto
            st.write(f"Texto procesado y sanitizado ({len(texto_cv)} caracteres).")
            st.session_state.texto_cv_extraido = texto_cv

            # Paso 2: Evaluación con IA y protección anti-inyección
            st.write(f"Invocando modelo {modelo} ({proveedor}) con salida estructurada Pydantic...")
            try:
                cadena = crear_evaluador_cv(
                    api_key=api_key,
                    provider=proveedor,
                    model_name=modelo,
                    temperature=temperatura
                )
                analisis = evaluar_candidato(
                    cadena,
                    texto_cv,
                    descripcion_puesto,
                    raise_on_error=True
                )
                st.session_state.analisis_actual = analisis
                status.update(label="¡Análisis completado exitosamente!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="Error durante la evaluación", state="error", expanded=True)
                st.error(f"❌ {str(e)}")
                return

    # ==========================
    # PRESENTACIÓN DE RESULTADOS (Con Sanitización XSS)
    # ==========================
    if st.session_state.analisis_actual:
        analisis: AnalisisCV = st.session_state.analisis_actual
        pct = analisis.porcentaje_ajuste

        eval_principal, color_eval = obtener_evaluacion_principal(pct)
        recom_texto, recom_icono, color_recom = obtener_recomendacion_final(pct)

        nombre_sanitizado = html.escape(analisis.nombre_candidato or "No identificado")
        eval_sanitizada = html.escape(eval_principal)
        recom_sanitizada = html.escape(recom_texto)

        st.divider()
        st.subheader("📊 Informe de Evaluación del Candidato")

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-label">AJUSTE AL PUESTO</span>
                <div style="font-size: 2.2rem; font-weight: 700; color: {color_eval}; margin: 4px 0;">{pct}%</div>
                <span style="background-color: {color_eval}22; color: {color_eval}; padding: 2px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;">
                    Nivel: {eval_sanitizada}
                </span>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-label">RECOMENDACIÓN</span>
                <div style="font-size: 1.6rem; font-weight: 700; color: {color_recom}; margin: 8px 0;">
                    {recom_icono}
                </div>
                <span style="background-color: {color_recom}22; color: {color_recom}; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 0.8rem;">
                    {recom_sanitizada}
                </span>
            </div>
            """, unsafe_allow_html=True)

        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-label">EXPERIENCIA RELEVANTE</span>
                <div style="font-size: 2.2rem; font-weight: 700; color: #0284c7; margin: 4px 0;">
                    {analisis.experiencia_años} <span style="font-size: 1.1rem; font-weight:400;">años</span>
                </div>
                <span class="metric-sub">Alineada al rol</span>
            </div>
            """, unsafe_allow_html=True)

        with m4:
            st.markdown(f"""
            <div class="metric-card">
                <span class="metric-label">CANDIDATO</span>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 8px 0; word-break: break-word;">
                    {nombre_sanitizado}
                </div>
                <span class="metric-sub">Perfil extraído</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(pct / 100.0, text=f"Porcentaje de compatibilidad ponderada: {pct}%")

        st.markdown("<br>", unsafe_allow_html=True)
        col_prof1, col_prof2 = st.columns([1, 1], gap="medium")

        with col_prof1:
            st.markdown("#### 🎓 Formación Académica y Certificaciones")
            st.info(analisis.education or "No especificada en el documento")

        with col_prof2:
            st.markdown("#### 💼 Resumen de Experiencia Relevante")
            st.write(analisis.experiencia_relevante or "Sin descripción disponible")

        st.markdown("#### 🛠️ Habilidades Técnicas y Profesionales Identificadas")
        if analisis.habilidades_clave:
            badges_html = "".join([
                f'<span class="badge-pill">{html.escape(str(h))}</span>'
                for h in analisis.habilidades_clave
            ])
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.write("No se identificaron habilidades técnicas específicas en el texto.")

        st.markdown("<br>", unsafe_allow_html=True)

        col_fort, col_mej = st.columns([1, 1], gap="large")

        with col_fort:
            st.markdown("#### 🌟 Principales Fortalezas")
            if analisis.fortalezas:
                for f in analisis.fortalezas:
                    st.markdown(
                        f'<div class="fortaleza-item">✔ <strong>{html.escape(str(f))}</strong></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.write("Sin fortalezas destacadas registradas.")

        with col_mej:
            st.markdown("#### 🎯 Áreas de Oportunidad y Brechas")
            if analisis.areas_mejora:
                for m in analisis.areas_mejora:
                    st.markdown(
                        f'<div class="mejora-item">⚠ <strong>{html.escape(str(m))}</strong></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.write("No se identificaron brechas críticas frente a la vacante.")

        # Acciones de guardado y exportación
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn_save, col_btn_json, col_btn_md, _ = st.columns([1.2, 1.2, 1.3, 1.3])
        with col_btn_save:
            if st.button("💾 Guardar Análisis", type="secondary", use_container_width=True):
                st.warning(
                    "⚠️ Funcionalidad en desarrollo: la persistencia en base de datos PostgreSQL "
                    "estará disponible en la próxima versión del módulo."
                )

        nombre_archivo_base = "".join(
            ch if ch.isalnum() or ch in ("-", "_") else "_"
            for ch in (analisis.nombre_candidato or "candidato").lower()
        ).strip("_") or "candidato"

        with col_btn_json:
            st.download_button(
                label="📥 Descargar JSON",
                data=analisis.model_dump_json(indent=2),
                file_name=f"evaluacion_{nombre_archivo_base}.json",
                mime="application/json",
                use_container_width=True
            )

        with col_btn_md:
            informe_md = generar_informe_markdown(analisis, eval_principal, recom_texto)
            st.download_button(
                label="📄 Descargar Informe (.md)",
                data=informe_md,
                file_name=f"informe_{nombre_archivo_base}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with st.expander("📄 Ver texto completo extraído del CV"):
            st.text_area(
                "Texto extraído del PDF:",
                value=st.session_state.texto_cv_extraido,
                height=220,
                disabled=True
            )


if __name__ == "__main__":
    main()
