"""
Sesión 1: Desarrollo Convencional (evaluacion_manual.py)
Problema: Determinar el estado académico de un estudiante a partir de tres calificaciones.
Requerimientos:
1. Recibir tres calificaciones numéricas.
2. Validar que cada calificación esté entre 0.0 y 5.0.
3. Calcular el promedio de las tres calificaciones con igual ponderación.
4. Mostrar el estado Aprobado cuando el promedio sea mayor o igual a 3.0.
5. Mostrar el estado Reprobado cuando el promedio sea inferior a 3.0.
6. Lanzar ValueError ante calificaciones fuera del rango.
"""


def evaluar_estudiante(nota1: float, nota2: float, nota3: float) -> dict:
    notas = [nota1, nota2, nota3]

    for n in notas:
        if not isinstance(n, (int, float)) or isinstance(n, bool):
            raise TypeError("Todas las notas deben ser valores numéricos")
        if n < 0.0 or n > 5.0:
            raise ValueError(f"Las notas deben estar entre 0.0 y 5.0. Valor inválido: {n}")

    promedio = sum(notas) / len(notas)
    estado = "Aprobado" if promedio >= 3.0 else "Reprobado"

    return {
        "promedio": round(promedio, 2),
        "estado": estado
    }


if __name__ == "__main__":
    print("=== Pruebas de Desarrollo Convencional (Sesión 1) ===")

    casos_prueba = [
        ("CP01", 4.0, 3.5, 4.5, {"promedio": 4.0, "estado": "Aprobado"}),
        ("CP02", 2.0, 2.5, 3.0, {"promedio": 2.5, "estado": "Reprobado"}),
        ("CP03", 3.0, 3.0, 3.0, {"promedio": 3.0, "estado": "Aprobado"}),
        ("CP04", 5.0, 5.0, 5.0, {"promedio": 5.0, "estado": "Aprobado"}),
        ("CP05", 0.0, 0.0, 0.0, {"promedio": 0.0, "estado": "Reprobado"}),
    ]

    for id_caso, n1, n2, n3, esperado in casos_prueba:
        res = evaluar_estudiante(n1, n2, n3)
        assert res == esperado, f"Fallo en {id_caso}: esperado {esperado}, obtenido {res}"
        print(f"[{id_caso}] Superado -> Entrada: ({n1}, {n2}, {n3}) => {res}")

    # Pruebas de error esperado
    for id_caso, n1, n2, n3 in [("CP06", 6.0, 3.0, 4.0), ("CP07", -1.0, 4.0, 3.0)]:
        try:
            evaluar_estudiante(n1, n2, n3)
            print(f"[{id_caso}] ERROR: Debería haber fallado.")
        except ValueError as e:
            print(f"[{id_caso}] Validación de error superada exitosamente ({e})")

