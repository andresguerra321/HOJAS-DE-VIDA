# Analizador de Currículums con Inteligencia Artificial

Proyecto integral de evaluación automatizada de candidatos desarrollado con **Python 3.12**, **Streamlit**, **LangChain (LCEL)** y modelos de lenguaje de gran escala (**OpenAI** y **Google Gemini**).

Esta solución compara objetivamente un currículum vitae en formato PDF contra la descripción y requerimientos de una vacante laboral, extrayendo los datos de forma estructurada con esquemas tipados en **Pydantic**.

---

## 🏗️ Arquitectura del Proyecto

Siguiendo las especificaciones técnicas del programa de formación:

```text
analisis-hojas-de-vida/
├── requirements.txt                 # Dependencias del proyecto
├── Dockerfile                       # Imagen base con Python 3.12 y librerías
├── docker-compose.yml               # Orquestación con PostgreSQL
├── .env.example                     # Plantilla de variables de entorno
├── .env                             # Configuración local de claves de API
├── run_app.py                       # Lanzador raíz conveniente
├── crear_cv_ejemplo.py              # Generador de CVs en PDF para pruebas
├── ejemplos_cv/                     # CVs generados listos para probar
│   ├── cv_carlos_mendoza_backend_senior.pdf
│   └── cv_laura_gomez_frontend_junior.pdf
└── app/
    └── intermedio/
        └── cv_analyzer/
            ├── README.md            # Documentación específica del módulo
            ├── app.py               # Punto de entrada oficial del módulo
            ├── models/
            │   ├── __init__.py
            │   └── cv_model.py      # Esquema Pydantic AnalisisCV y validadores
            ├── prompts/
            │   ├── __init__.py
            │   └── cv_prompts.py    # Plantilla de prompts y ponderaciones
            ├── services/
            │   ├── __init__.py
            │   ├── pdf_processor.py # Extracción de texto con PyPDF2 / pypdf
            │   └── cv_evaluator.py  # Cadena LCEL con with_structured_output
            └── ui/
                ├── __init__.py
                └── streamlit_ui.py  # Interfaz gráfica interactiva en Streamlit
```

---

## 🎯 Criterios y Ponderación de Evaluación

El modelo calcula el porcentaje de compatibilidad (0% a 100%) aplicando estrictamente:

| Criterio | Peso asignado | Aspectos evaluados |
| :--- | :---: | :--- |
| **Experiencia relevante** | **40 %** | Años en roles afines, nivel de responsabilidad e impacto demostrado. |
| **Habilidades técnicas** | **35 %** | Dominio de lenguajes, frameworks, bases de datos y herramientas solicitadas. |
| **Formación y certificaciones** | **15 %** | Título profesional, nivel académico y certificaciones vigentes. |
| **Coherencia profesional** | **10 %** | Estabilidad laboral, progresión de carrera y claridad expositiva. |

### Escala de Decisión

- **Evaluación Principal:**
  - `80 – 100%`: 🟢 Excelente
  - `60 – 79%`: 🔵 Bueno
  - `40 – 59%`: 🟡 Regular
  - `0 – 39%`: 🔴 Bajo

- **Recomendación de Contratación:**
  - `70 – 100%`: ✅ **Candidato recomendado**
  - `50 – 69%`: ⚠️ **Candidato con potencial**
  - `0 – 49%`: ❌ **Candidato no recomendado**

---

## 🚀 Puesta en Marcha

### 1. Requisitos Previos

- Python 3.12 instalado.
- Clave de API de **OpenAI** (`OPENAI_API_KEY`) o de **Google Gemini** (`GEMINI_API_KEY`).

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configuración de Credenciales

Copia el archivo `.env.example` a `.env` y configura tus credenciales:

```env
OPENAI_API_KEY=tu_api_key_de_openai
GEMINI_API_KEY=tu_api_key_de_gemini
GOOGLE_API_KEY=tu_api_key_de_gemini
```

> **Nota:** La aplicación también permite ingresar la clave directamente desde la barra lateral de la interfaz web en tiempo de ejecución.

### 4. Generar CVs de Prueba (Opcional)

Puedes generar 2 CVs en PDF con perfiles reales para pruebas ejecutando:

```bash
python crear_cv_ejemplo.py
```

Esto generará en la carpeta `ejemplos_cv/`:
- `cv_carlos_mendoza_backend_senior.pdf`: Perfil Senior Backend con alto ajuste a puestos de Python.
- `cv_laura_gomez_frontend_junior.pdf`: Perfil Junior con ajuste moderado/bajo.

### 5. Iniciar la Aplicación

Tienes dos opciones para iniciar Streamlit:

**Opción A (Desde la raíz):**
```bash
streamlit run run_app.py
```

**Opción B (Desde la carpeta del módulo, según el estándar del proyecto):**
```bash
cd app/intermedio/cv_analyzer
streamlit run app.py
```

Abre tu navegador en: **`http://localhost:8501`**

---

## 🐳 Despliegue con Docker

### Con Docker Compose (Entorno Completo)

```bash
docker compose up --build -d
```

Abre `http://localhost:8501` en el navegador.

Para detener el contenedor:
```bash
docker compose down
```

---

## 🧪 Flujo de Trabajo en la Interfaz

1. **Carga el CV en PDF:** Sube uno de los PDFs de `ejemplos_cv/` o tu propia hoja de vida.
2. **Ingresa la Vacante:** Puedes escribir tu propia descripción o hacer clic en **"📝 Cargar vacante de ejemplo"** para probar instantáneamente con un puesto de *Desarrollador Python Backend Senior*.
3. **Selecciona Modelo y Proveedor:** En la barra lateral, elige entre OpenAI (`gpt-4o-mini`, `gpt-4o`) o Google Gemini (`gemini-1.5-flash`).
4. **Haz clic en "🔍 Analizar Candidato":** La aplicación procesará el documento, invocará la cadena LCEL con `with_structured_output` y mostrará:
   - Tarjetas métricas con porcentaje de ajuste, recomendación, años de experiencia y nombre extraído.
   - Resumen de experiencia laboral y formación académica.
   - Habilidades técnicas identificadas como etiquetas interactivas.
   - Columnas comparativas con **Principales Fortalezas** y **Áreas de Oportunidad / Brechas**.
   - Visor colapsable del texto extraído del PDF.

