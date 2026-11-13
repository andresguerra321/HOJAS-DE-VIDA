import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError
from pypdf import PdfWriter

from app.intermedio.cv_analyzer.models.cv_model import AnalisisCV
from app.intermedio.cv_analyzer.prompts.cv_prompts import crear_sistema_prompts
from app.intermedio.cv_analyzer.services.cv_evaluator import (
    _enmascarar_secretos,
    crear_evaluador_cv,
    evaluar_candidato,
)
from app.intermedio.cv_analyzer.services.pdf_processor import (
    MAX_PAGINAS_PERMITIDAS,
    MAX_TAMANO_BYTES,
    ResultadoTextoPDF,
    extraer_texto_pdf,
)
from app.intermedio.cv_analyzer.ui.streamlit_ui import (
    generar_informe_markdown,
    obtener_ejemplos_cv_disponibles,
    obtener_evaluacion_principal,
    obtener_recomendacion_final,
)


RAIZ = Path(__file__).resolve().parent.parent


# ==========================================================
# 1. Pruebas del modelo Pydantic AnalisisCV
# ==========================================================
def test_analisis_cv_campos_obligatorios():
    with pytest.raises(ValidationError):
        AnalisisCV(nombre_candidato="Solo Nombre")


def test_analisis_cv_validadores_y_normalizacion():
    modelo = AnalisisCV(
        nombre_candidato="Ana Torres",
        experiencia_años="4 años",
        habilidades_clave="Python",
        education="Ingeniería de Sistemas",
        experiencia_relevante="Backend developer",
        fortalezas=["Liderazgo", "  ", "FastAPI"],
        areas_mejora=None,
        porcentaje_ajuste="125%",
    )
    assert modelo.experiencia_años == 4
    assert modelo.porcentaje_ajuste == 100
    assert modelo.habilidades_clave == ["Python"]
    assert modelo.fortalezas == ["Liderazgo", "FastAPI"]
    assert modelo.areas_mejora == []

    modelo_negativo = AnalisisCV(
        nombre_candidato="Pedro",
        experiencia_años=-3,
        habilidades_clave=[],
        education="Bachiller",
        experiencia_relevante="Sin experiencia",
        fortalezas=[],
        areas_mejora=[],
        porcentaje_ajuste=-15,
    )
    assert modelo_negativo.experiencia_años == 0
    assert modelo_negativo.porcentaje_ajuste == 0


# ==========================================================
# 2. Pruebas del procesador de PDF (dualidad str / tupla y límites)
# ==========================================================
def test_extraer_texto_pdf_real_dual_usage():
    pdf_senior = RAIZ / "ejemplos_cv" / "cv_carlos_mendoza_backend_senior.pdf"
    assert pdf_senior.exists(), "Debe existir el PDF de ejemplo generado"

    resultado = extraer_texto_pdf(str(pdf_senior))
    assert isinstance(resultado, ResultadoTextoPDF)
    assert isinstance(resultado, str)
    assert not resultado.es_error
    assert "Carlos Andrés Mendoza Rivas" in resultado
    assert "--- Página 1 ---" in resultado

    # Desempaquetado como tupla
    texto, error = resultado
    assert error is None
    assert texto == str(resultado)


def test_extraer_texto_pdf_vacio_y_nulo():
    res_none = extraer_texto_pdf(None)
    assert res_none.es_error
    assert str(res_none).startswith("Error:")
    texto, err = res_none
    assert texto == ""
    assert err == str(res_none)

    res_empty = extraer_texto_pdf(b"")
    assert res_empty.es_error
    assert "vacío" in str(res_empty).lower()


def test_extraer_texto_pdf_limite_tamano():
    payload_grande = b"0" * (MAX_TAMANO_BYTES + 10)
    res = extraer_texto_pdf(payload_grande)
    assert res.es_error
    assert "10 MB" in str(res)


def test_extraer_texto_pdf_limite_paginas():
    writer = PdfWriter()
    for _ in range(MAX_PAGINAS_PERMITIDAS + 1):
        writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)

    res = extraer_texto_pdf(buffer)
    assert res.es_error
    assert str(MAX_PAGINAS_PERMITIDAS) in str(res)


def test_extraer_texto_pdf_sin_capa_de_texto():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)

    res = extraer_texto_pdf(buffer)
    assert res.es_error
    assert "texto legible" in str(res).lower()


# ==========================================================
# 3. Pruebas de Prompts y Ponderación
# ==========================================================
def test_crear_sistema_prompts_estructura_y_seguridad():
    prompt = crear_sistema_prompts()
    assert set(prompt.input_variables) == {"descripcion_puesto", "texto_cv"}

    mensajes = prompt.format_messages(
        descripcion_puesto="Python Dev",
        texto_cv="CV contenido",
    )
    assert len(mensajes) == 2
    sys_content = mensajes[0].content
    human_content = mensajes[1].content

    for peso in ("40%", "35%", "15%", "10%"):
        assert peso in sys_content
    assert "ANTI-PROMPT INJECTION" in sys_content
    assert "<descripcion_vacante>" in human_content
    assert "<curriculum_vitae_datos>" in human_content


# ==========================================================
# 4. Pruebas del Evaluador de CV (2 y 3 argumentos + except)
# ==========================================================
def _analisis_ejemplo(pct: int = 85) -> AnalisisCV:
    return AnalisisCV(
        nombre_candidato="Carlos Mendoza",
        experiencia_años=4,
        habilidades_clave=["Python", "FastAPI", "PostgreSQL"],
        education="Ingeniería de Sistemas",
        experiencia_relevante="4 años construyendo APIs REST.",
        fortalezas=["Dominio de Python", "Experiencia en Docker"],
        areas_mejora=["Sin mención de Kafka"],
        porcentaje_ajuste=pct,
    )


def test_evaluar_candidato_3_argumentos():
    esperado = _analisis_ejemplo(88)
    cadena_mock = MagicMock()
    cadena_mock.invoke.return_value = esperado

    resultado = evaluar_candidato(cadena_mock, "Texto del CV", "Vacante Python")
    assert resultado == esperado
    cadena_mock.invoke.assert_called_once_with({
        "texto_cv": "Texto del CV",
        "descripcion_puesto": "Vacante Python",
    })


def test_evaluar_candidato_2_argumentos_con_mock():
    esperado = _analisis_ejemplo(75)
    cadena_mock = MagicMock()
    cadena_mock.invoke.return_value = esperado.model_dump()

    with patch(
        "app.intermedio.cv_analyzer.services.cv_evaluator.crear_evaluador_cv",
        return_value=cadena_mock,
    ) as mock_factory:
        resultado = evaluar_candidato("Texto del CV", "Vacante Python", provider="OpenAI")
        mock_factory.assert_called_once()
        assert isinstance(resultado, AnalisisCV)
        assert resultado.porcentaje_ajuste == 75


def test_evaluar_candidato_bloque_except_corregido():
    cadena_fallida = MagicMock()
    cadena_fallida.invoke.side_effect = RuntimeError("Fallo con sk-1234567890abcdef1234")

    # Modo fallback (por defecto) debe construir AnalisisCV válido sin typos
    res_fallback = evaluar_candidato(cadena_fallida, "CV válido", "Puesto válido")
    assert isinstance(res_fallback, AnalisisCV)
    assert res_fallback.porcentaje_ajuste == 0
    assert len(res_fallback.fortalezas) >= 1
    assert "sk-***REDACTED***" in res_fallback.experiencia_relevante
    assert "sk-1234567890abcdef1234" not in res_fallback.experiencia_relevante

    # Modo raise_on_error=True debe propagar RuntimeError enmascarando secretos
    with pytest.raises(RuntimeError) as exc_info:
        evaluar_candidato(
            cadena_fallida, "CV válido", "Puesto válido", raise_on_error=True
        )
    assert "sk-***REDACTED***" in str(exc_info.value)
    assert "sk-1234567890abcdef1234" not in str(exc_info.value)


def test_enmascarar_secretos():
    msg = "Error auth key=AIzaSyDummyKey12345678901234567890"
    sanitizado = _enmascarar_secretos(msg)
    assert "AIzaSyDummyKey" not in sanitizado
    assert "AIza***REDACTED***" in sanitizado


def test_crear_evaluador_cv_sin_clave(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError):
        crear_evaluador_cv(provider="OpenAI")

    with pytest.raises(ValueError):
        crear_evaluador_cv(provider="Google Gemini")


# ==========================================================
# 5. Pruebas de Lógica UI y Exportación
# ==========================================================
@pytest.mark.parametrize("pct,esperado", [
    (95, "Excelente"),
    (80, "Excelente"),
    (79, "Bueno"),
    (60, "Bueno"),
    (59, "Regular"),
    (40, "Regular"),
    (39, "Bajo"),
    (0, "Bajo"),
])
def test_umbrales_evaluacion_principal(pct, esperado):
    etiqueta, _ = obtener_evaluacion_principal(pct)
    assert etiqueta == esperado


@pytest.mark.parametrize("pct,esperado", [
    (100, "Candidato recomendado"),
    (70, "Candidato recomendado"),
    (69, "Candidato con potencial"),
    (50, "Candidato con potencial"),
    (49, "Candidato no recomendado"),
    (0, "Candidato no recomendado"),
])
def test_umbrales_recomendacion_final(pct, esperado):
    recom, _, _ = obtener_recomendacion_final(pct)
    assert recom == esperado


def test_ejemplos_cv_descubiertos_e_informe_markdown():
    ejemplos = obtener_ejemplos_cv_disponibles()
    assert len(ejemplos) >= 2

    analisis = _analisis_ejemplo(85)
    md = generar_informe_markdown(analisis, "Excelente", "Candidato recomendado")
    assert "# Informe de Evaluación de Candidato" in md
    assert "Carlos Mendoza" in md
    assert "85%" in md

