# Analizador de Currículums con IA (CV Analyzer)

Aplicación desarrollada en **Streamlit** que compara y evalúa de manera inteligente un currículum vitae en formato PDF contra los requisitos y responsabilidades de un puesto de trabajo. 

Extrae el texto del documento, lo procesa mediante **LangChain** con modelos generativos (OpenAI / Google Gemini) y genera un análisis estructurado y tipado mediante **Pydantic**.

---

## 🚀 Funcionalidades

- **Carga de CV en PDF:** Admite documentos PDF con texto seleccionable y procesa página por página con separadores.
- **Entrada de Requisitos del Puesto:** Área de texto personalizable con botón de carga de vacante de prueba (Desarrollador Python Backend).
- **Extracción Estructurada:** Nombre del candidato, años de experiencia relevante, educación y habilidades técnicas clave.
- **Identificación Cualitativa:** Diagnóstico de fortalezas principales y áreas de mejora o vacíos formativos.
- **Ponderación Objetiva:** Estimación del porcentaje de ajuste al puesto (0 – 100%) con base en:
  - *Experiencia relevante:* 40%
  - *Habilidades técnicas:* 35%
  - *Formación y certificaciones:* 15%
  - *Coherencia profesional:* 10%
- **Recomendación de Contratación:** Categorización automática en *Candidato recomendado* (≥ 70%), *Candidato con potencial* (50–69%) o *No recomendado* (< 50%).
- **Soporte Multi-proveedor:** Compatible con **OpenAI** (`gpt-4o-mini`, `gpt-4o`) y **Google Gemini** (`gemini-3.8-flash`, `gemini-2.5-flash`).
- **Persistencia en Sesión y Exportación:** Conserva el análisis en `st.session_state` e incluye descarga directa en JSON y Markdown.

---

## 📁 Estructura del Módulo

```text
cv_analyzer/
├── README.md                # Documentación del módulo
├── app.py                  # Punto de entrada de Streamlit
├── models/
│   ├── __init__.py
│   └── cv_model.py         # Esquema Pydantic AnalisisCV con validadores
├── prompts/
│   ├── __init__.py
│   └── cv_prompts.py       # Plantilla ChatPromptTemplate y directrices
├── services/
│   ├── __init__.py
│   ├── pdf_processor.py    # Extracción y limpieza de texto del PDF
│   └── cv_evaluator.py     # Construcción de la cadena LCEL e invocación
└── ui/
    ├── __init__.py
    └── streamlit_ui.py     # Interfaz interactiva de Streamlit
```

---

## 🛠️ Ejecución Local

Desde la carpeta raíz del proyecto:

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar la clave de API (en terminal o en archivo .env)
# Para OpenAI:
export OPENAI_API_KEY="tu-clave-aqui"   # Linux/macOS
# o en PowerShell: $env:OPENAI_API_KEY = "tu-clave-aqui"

# Para Gemini:
# export GEMINI_API_KEY="tu-clave-aqui"

# 3. Iniciar Streamlit desde la raíz del repositorio:
streamlit run run_app.py

# O directamente desde la carpeta del módulo:
# cd app/intermedio/cv_analyzer
# python -m streamlit run app.py --server.port=8501
```

Abre en tu navegador: `http://localhost:8501`

