"""
Sesión 2: Diseño y Optimización de Instrucciones mediante Prompt Engineering

Implementación de referencia para el cálculo de compras con validación estricta.
"""


def calcular_total_carrito(carrito: list) -> int:
    """
    Calcula el total de una compra a partir de los productos registrados en un carrito.
    Aplica las reglas y criterios de aceptación definidos en la Sesión 2.
    """
    if not isinstance(carrito, list):
        raise TypeError("El carrito debe ser una lista")

    total = 0

    for producto in carrito:
        if not isinstance(producto, dict):
            raise TypeError("Cada producto debe ser un diccionario")

        campos = ("nombre", "precio", "cantidad")
        if any(campo not in producto for campo in campos):
            raise ValueError("Faltan datos obligatorios del producto (nombre, precio, cantidad)")

        nombre = producto["nombre"]
        precio = producto["precio"]
        cantidad = producto["cantidad"]

        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("Nombre de producto inválido o vacío")

        if isinstance(precio, bool) or not isinstance(precio, (int, float)) or precio <= 0:
            raise ValueError(f"Precio inválido para '{nombre}': debe ser un número positivo")

        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError(f"Cantidad inválida para '{nombre}': debe ser un entero positivo")

        total += int(precio * cantidad)

    return total


if __name__ == "__main__":
    print("=== Pruebas de Cálculo de Compras (Sesión 2) ===")

    # CP01: Dos productos válidos
    c1 = [
        {"nombre": "Arroz", "precio": 10000, "cantidad": 2},
        {"nombre": "Leche", "precio": 5000, "cantidad": 3}
    ]
    assert calcular_total_carrito(c1) == 35000
    print("[CP01] Carrito normal superado: $35.000")

    # CP02: Carrito vacío
    assert calcular_total_carrito([]) == 0
    print("[CP02] Carrito vacío superado: $0")

    # CP03: Precio negativo
    try:
        calcular_total_carrito([{"nombre": "Pan", "precio": -2000, "cantidad": 1}])
    except ValueError:
        print("[CP03] Rechazo de precio negativo superado")

    # CP04: Cantidad decimal
    try:
        calcular_total_carrito([{"nombre": "Carne", "precio": 15000, "cantidad": 1.5}])
    except ValueError:
        print("[CP04] Rechazo de cantidad decimal superado")

    # CP05: Producto sin nombre
    try:
        calcular_total_carrito([{"nombre": "   ", "precio": 4000, "cantidad": 2}])
    except ValueError:
        print("[CP05] Rechazo de nombre vacío superado")

