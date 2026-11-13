from typing import Any, List, Union
from pydantic import BaseModel, Field, field_validator


class AnalisisCV(BaseModel):
    """
    Modelo estructurado para representar la evaluación integral de un currículum vitae (CV)
    frente a la descripción y requerimientos de una vacante laboral.
    Todos los campos son obligatorios.
    """
    nombre_candidato: str = Field(
        ...,
        description="Nombre completo del candidato extraído del currículum vitae"
    )
    experiencia_años: int = Field(
        ...,
        description="Años totales estimados de experiencia profesional relevante"
    )
    habilidades_clave: List[str] = Field(
        ...,
        description="Lista de habilidades técnicas y profesionales clave que posee el candidato relevantes para la vacante"
    )
    education: str = Field(
        ...,
        description="Nivel educativo máximo, título obtenido e institución académica"
    )
    experiencia_relevante: str = Field(
        ...,
        description="Resumen conciso de la trayectoria y experiencia laboral directamente aplicable a las responsabilidades del puesto"
    )
    fortalezas: List[str] = Field(
        ...,
        description="Lista de fortalezas principales y ventajas competitivas del candidato frente al perfil buscado"
    )
    areas_mejora: List[str] = Field(
        ...,
        description="Lista de áreas de oportunidad, brechas técnicas o requisitos no cumplidos frente a la vacante"
    )
    porcentaje_ajuste: int = Field(
        ...,
        ge=0,
        le=100,
        description="Porcentaje numérico de ajuste global del candidato al puesto (escala del 0 al 100)"
    )

    @field_validator("porcentaje_ajuste", mode="before")
    @classmethod
    def validar_porcentaje(cls, v: Union[int, float, str]) -> int:
        """Asegura que el porcentaje sea un entero entre 0 y 100."""
        if isinstance(v, bool):
            return 0
        if isinstance(v, str):
            cleaned = v.strip().replace("%", "").replace(",", ".")
            try:
                val = int(round(float(cleaned)))
            except ValueError:
                digits = "".join(ch for ch in v if ch.isdigit())
                val = int(digits) if digits else 0
        else:
            val = int(round(float(v)))
        return max(0, min(100, val))

    @field_validator("experiencia_años", mode="before")
    @classmethod
    def validar_experiencia(cls, v: Union[int, float, str]) -> int:
        """Asegura que los años de experiencia sean un entero no negativo."""
        if isinstance(v, bool):
            return 0
        if isinstance(v, str):
            cleaned = v.strip().replace(",", ".")
            try:
                val = int(round(float(cleaned)))
            except ValueError:
                digits = "".join(ch for ch in v if ch.isdigit())
                val = int(digits) if digits else 0
        else:
            val = int(round(float(v)))
        return max(0, val)

    @field_validator("habilidades_clave", "fortalezas", "areas_mejora", mode="before")
    @classmethod
    def validar_listas(cls, v: Any) -> List[str]:
        """Normaliza listas de texto: convierte cadenas simples en lista y limpia vacíos."""
        if v is None:
            return []
        if isinstance(v, str):
            limpio = v.strip()
            return [limpio] if limpio else []
        if isinstance(v, (list, tuple, set)):
            return [str(item).strip() for item in v if str(item).strip()]
        limpio = str(v).strip()
        return [limpio] if limpio else []
