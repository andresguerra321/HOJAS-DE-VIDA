"""
Sesión 1: Desarrollo Asistido por IA (evaluacion_ia.py)

Prompt utilizado:
"Actúa como un desarrollador Python con experiencia en enseñanza de programación.
Necesito implementar una función para evaluar estudiantes a partir de tres calificaciones.
Cada nota debe estar entre 0.0 y 5.0. El promedio debe calcularse con igual ponderación
y el estudiante aprueba con 3.0 o más. Devuelve un diccionario con el promedio y el estado académico.
Incluye validaciones y explica el funcionamiento del código paso a paso."
"""


def evaluar_estudiante_ia(nota1: float, nota2: float, nota3: float) -> dict:
    """
    Calcula el promedio de tres notas escolares y determina la condición de aprobación.

    Args:
        nota1: Primera calificación (0.0 a 5.0).
        nota2: Segunda calificación (0.0 a 5.0).
        nota3: Tercera calificación (0.0 a 5.0).

    Returns:
        dict: Diccionario con 'promedio' y 'estado' ('Aprobado' o 'Reprobado').

    Raises:
        ValueError: Si alguna calificación está fuera del rango permitido [0.0, 5.0].
    """
    calificaciones = [nota1, nota2, nota3]

    # Validación rigurosa de límites numéricos
    for idx, c in enumerate(calificaciones, start=1):
        if not (0.0 <= c <= 5.0):
            raise ValueError(f"Error de validación: La nota {idx} ({c}) está fuera del rango permitido [0.0, 5.0]")

    promedio = sum(calificaciones) / 3.0
    estado = "Aprobado" if promedio >= 3.0 else "Reprobado"

    return {
        "promedio": round(promedio, 2),
        "estado": estado
    }


if __name__ == "__main__":
    print("=== Pruebas de Desarrollo Asistido por IA (Sesión 1) ===")

    casos_prueba = [
        ("CP01", 4.0, 3.5, 4.5, {"promedio": 4.0, "estado": "Aprobado"}),
        ("CP02", 2.0, 2.5, 3.0, {"promedio": 2.5, "estado": "Reprobado"}),
        ("CP03", 3.0, 3.0, 3.0, {"promedio": 3.0, "estado": "Aprobado"}),
        ("CP04", 5.0, 5.0, 5.0, {"promedio": 5.0, "estado": "Aprobado"}),
        ("CP05", 0.0, 0.0, 0.0, {"promedio": 0.0, "estado": "Reprobado"}),
    ]

    for id_caso, n1, n2, n3, esperado in casos_prueba:
        res = evaluar_estudiante_ia(n1, n2, n3)
        assert res == esperado, f"Fallo en {id_caso}: esperado {esperado}, obtenido {res}"
        print(f"[{id_caso}] Superado -> {res}")

    for id_caso, n1, n2, n3 in [("CP06", 6.0, 3.0, 4.0), ("CP07", -1.0, 4.0, 3.0)]:
        try:
            evaluar_estudiante_ia(n1, n2, n3)
        except ValueError as e:
            print(f"[{id_caso}] Validación correcta: {e}")

