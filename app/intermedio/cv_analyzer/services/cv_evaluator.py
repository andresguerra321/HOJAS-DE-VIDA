import logging
import os
import re
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

try:
    from models.cv_model import AnalisisCV
    from prompts.cv_prompts import crear_sistema_prompts
except (ImportError, ModuleNotFoundError):
    from app.intermedio.cv_analyzer.models.cv_model import AnalisisCV
    from app.intermedio.cv_analyzer.prompts.cv_prompts import crear_sistema_prompts


def _detectar_proveedor_predeterminado() -> str:
    """Detecta automáticamente el proveedor según las claves configuradas en el entorno."""
    if os.getenv("OPENAI_API_KEY"):
        return "OpenAI"
    if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
        return "Google Gemini"
    return "OpenAI"


def _enmascarar_secretos(mensaje: str, clave_extra: Optional[str] = None) -> str:
    """Oculta posibles claves de API en mensajes de error para evitar fugas."""
    texto = str(mensaje)
    posibles_claves = [
        clave_extra,
        os.getenv("OPENAI_API_KEY"),
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("GEMINI_API_KEY"),
    ]
    for clave in posibles_claves:
        if clave and len(clave) > 6 and clave in texto:
            texto = texto.replace(clave, "***REDACTED***")

    # Enmascarar patrones comunes de tokens (sk-..., AIza..., AQ....)
    texto = re.sub(r"\bsk-[A-Za-z0-9_\-]{12,}\b", "sk-***REDACTED***", texto)
    texto = re.sub(r"\bAIza[0-9A-Za-z\-_]{20,}\b", "AIza***REDACTED***", texto)
    texto = re.sub(r"\bAQ\.[0-9A-Za-z\-_]{20,}\b", "AQ.***REDACTED***", texto)
    return texto


def crear_evaluador_cv(
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.2
):
    """
    Configura y retorna la cadena ejecutable (Runnable) para evaluación de CVs.
    Utiliza el método with_structured_output() con el modelo Pydantic AnalisisCV.

    Args:
        api_key: Clave de API del proveedor (OpenAI o Google).
        provider: Nombre del proveedor ("OpenAI" o "Google Gemini"). Si es None, se autodetecta.
        model_name: Nombre específico del modelo (ej. "gpt-4o-mini", "gemini-3.8-flash").
        temperature: Temperatura del modelo para respuestas determinísticas y consistentes.

    Returns:
        Runnable: Cadena LCEL compuesta por (chat_prompt | modelo_estructurado).
    """
    prompt = crear_sistema_prompts()
    selected_provider = provider or _detectar_proveedor_predeterminado()

    if selected_provider == "Google Gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        effective_key = (
            api_key
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )
        if not effective_key:
            raise ValueError(
                "Falta la clave de API para Google Gemini. "
                "Configura la variable GEMINI_API_KEY o ingresa la clave en la barra lateral."
            )

        selected_model = model_name or "gemini-3.8-flash"
        llm = ChatGoogleGenerativeAI(
            model=selected_model,
            temperature=temperature,
            google_api_key=effective_key
        )
    else:
        from langchain_openai import ChatOpenAI

        effective_key = api_key or os.getenv("OPENAI_API_KEY")
        if not effective_key:
            raise ValueError(
                "Falta la clave de API para OpenAI. "
                "Configura la variable OPENAI_API_KEY en tu entorno o en el archivo .env, "
                "o ingresa la clave en la barra lateral."
            )

        selected_model = model_name or "gpt-4o-mini"
        llm = ChatOpenAI(
            model=selected_model,
            temperature=temperature,
            api_key=effective_key
        )

    modelo_estructurado = llm.with_structured_output(AnalisisCV)
    return prompt | modelo_estructurado


def evaluar_candidato(
    *args,
    raise_on_error: bool = False,
    **kwargs
) -> AnalisisCV:
    """
    Evalúa un currículum frente a una descripción de puesto retornando una instancia validada de AnalisisCV.

    Soporta dos formas de invocación:
      1. `evaluar_candidato(texto_cv, descripcion_puesto, ...)` (crea la cadena automáticamente)
      2. `evaluar_candidato(cadena, texto_cv, descripcion_puesto)` (usa una cadena ya configurada)

    Args:
        raise_on_error: Si es True, propaga RuntimeError ante fallos del modelo.
                        Si es False, retorna un objeto AnalisisCV de respaldo válido con el detalle del error.

    Returns:
        AnalisisCV: Objeto estructurado y validado con los resultados.
    """
    cadena = kwargs.pop("cadena", None)
    texto_cv = kwargs.pop("texto_cv", None)
    descripcion_puesto = kwargs.pop("descripcion_puesto", None)

    if len(args) == 3:
        cadena, texto_cv, descripcion_puesto = args
    elif len(args) == 2:
        texto_cv, descripcion_puesto = args
    elif len(args) == 1:
        if cadena is not None and texto_cv is None:
            texto_cv = args[0]
        elif texto_cv is None:
            texto_cv = args[0]
    elif len(args) > 3:
        raise TypeError("evaluar_candidato acepta como máximo 3 argumentos posicionales.")

    if not texto_cv or not str(texto_cv).strip():
        raise ValueError("El texto del currículum vitae no puede estar vacío.")

    if not descripcion_puesto or not str(descripcion_puesto).strip():
        raise ValueError("La descripción del puesto no puede estar vacía.")

    api_key_usada = kwargs.get("api_key")

    try:
        if cadena is None:
            cadena = crear_evaluador_cv(
                api_key=kwargs.get("api_key"),
                provider=kwargs.get("provider"),
                model_name=kwargs.get("model_name"),
                temperature=kwargs.get("temperature", 0.2),
            )

        resultado = cadena.invoke({
            "texto_cv": str(texto_cv),
            "descripcion_puesto": str(descripcion_puesto)
        })

        if isinstance(resultado, dict):
            return AnalisisCV(**resultado)

        if isinstance(resultado, AnalisisCV):
            return resultado

        raise TypeError(f"El modelo devolvió un tipo no esperado: {type(resultado).__name__}")

    except Exception as e:
        mensaje_seguro = _enmascarar_secretos(str(e), api_key_usada)
        logger.error("Error al evaluar candidato con IA: %s", mensaje_seguro)

        if raise_on_error:
            raise RuntimeError(
                f"Fallo en la evaluación del candidato mediante el modelo de IA: {mensaje_seguro}"
            ) from e

        return AnalisisCV(
            nombre_candidato="Error en evaluación",
            experiencia_años=0,
            habilidades_clave=["Error en procesamiento"],
            education="No disponible por error durante el análisis",
            experiencia_relevante=(
                f"No fue posible completar la evaluación automática del candidato. "
                f"Detalle técnico: {mensaje_seguro}"
            ),
            fortalezas=["Requiere revisión manual o reintento de evaluación"],
            areas_mejora=[
                "Verificar clave de API, cuota disponible o conectividad con el modelo",
                f"Error reportado: {mensaje_seguro}",
            ],
            porcentaje_ajuste=0,
        )
