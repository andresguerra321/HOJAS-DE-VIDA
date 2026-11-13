"""
Sesión 0: Bases de Datos Vectoriales y Embeddings
Caso Práctico: Embotelladora Santander S.A.S. (Recuperación Semántica con Chroma)
"""

DOCUMENTOS_SANTANDER = [
    {
        "id": "descuentos_autoservicio",
        "canal": "autoservicio",
        "texto": """Embotelladora Santander S.A.S. Política de descuentos para el canal autoservicio:
supermercados y grandes superficies en Colombia. El descuento base es del 8% sobre el precio de lista de los productos del portafolio estándar. Se permite negociar hasta un 12% de descuento en acuerdos anuales con compromiso de volumen de compra.
Los descuentos adicionales deben estar asociados a exhibiciones especiales o cabeceras de góndola aprobadas por el área de Mercadeo Comercial.
Los precios de lista se expresan en pesos colombianos (COP)."""
    },
    {
        "id": "descuentos_tradicional",
        "canal": "tradicional",
        "texto": """Embotelladora Santander S.A.S. Política de descuentos para el canal tradicional:
tiendas de barrio, pequeños comercios, cafeterías y restaurantes. El descuento base es del 5% sobre el precio de lista para compras de cajas surtidas.
Se permite otorgar hasta un 7% de descuento cuando el cliente alcanza el volumen mínimo mensual definido para su zona comercial.
El volumen mínimo debe consultarse en la tabla vigente de la zona; este documento no establece una cantidad específica.
Los precios de lista se expresan en pesos colombianos (COP)."""
    },
    {
        "id": "descuentos_mayoristas",
        "canal": "mayoristas",
        "texto": """Embotelladora Santander S.A.S. Política de descuentos para mayoristas y distribuidores regionales.
El descuento base es del 10% sobre el precio de lista para una compra mínima de una estiba completa de producto.
Se permite otorgar hasta un 15% de descuento a clientes que superen el volumen trimestral pactado en su acuerdo comercial.
Todo descuento superior al 12% requiere aprobación de Finanzas y de la Dirección Comercial, incluso cuando el cliente cumpla la condición de volumen trimestral.
Los precios de lista se expresan en pesos colombianos (COP)."""
    },
    {
        "id": "descuentos_cadenas_regionales",
        "canal": "cadenas_regionales",
        "texto": """Embotelladora Santander S.A.S. Política de descuentos para cadenas regionales de supermercados.
Aplica a cadenas de autoservicio con presencia en varias ciudades o municipios de una región.
El descuento base es del 9% sobre el precio de lista.
Se permite negociar hasta un 14% de descuento cuando la cadena garantiza exclusividad del portafolio en las categorías acordadas.
Los acuerdos deben formalizarse mediante contratos anuales e incluir una revisión de rentabilidad por referencia de producto (SKU).
Los precios de lista se expresan en pesos colombianos (COP)."""
    },
    {
        "id": "combos_multisabor",
        "canal": "multicanal",
        "texto": """Embotelladora Santander S.A.S. Lineamientos para combos y promociones de distintos sabores.
Los combos deben incluir al menos tres sabores de la misma familia de producto.
El descuento del combo no debe superar el 10% de la suma de los precios individuales de los productos que lo componen.
Los combos aplican únicamente al canal tradicional y al canal autoservicio, incluidas las cadenas regionales de supermercados.
No se permite ofrecer estos combos a mayoristas ni a distribuidores regionales.
El límite del 10% corresponde al descuento del combo y no constituye una autorización automática para acumularlo con otros descuentos."""
    },
    {
        "id": "lanzamientos_nuevos_productos",
        "canal": "lanzamientos",
        "texto": """Embotelladora Santander S.A.S. Política de precios y descuentos para lanzamientos de productos.
Durante los primeros tres meses, el precio de lanzamiento, antes de aplicar descuentos, debe ser igual o superior al precio de lista estándar.
Se permite un descuento promocional máximo del 5% para introducir el producto en cadenas clave.
Finalizados los tres meses del periodo de lanzamiento, los descuentos deben ajustarse a la política del canal comercial correspondiente.
Los precios se expresan en pesos colombianos (COP)."""
    },
    {
        "id": "lineamientos_generales_descuentos",
        "canal": "general",
        "texto": """Embotelladora Santander S.A.S. Lineamientos generales de rentabilidad y control de descuentos.
Ningún cliente puede acumular más de tres tipos de descuentos simultáneos sobre una misma referencia de producto (SKU).
El margen bruto mínimo después de aplicar los descuentos debe ser del 18%.
El área de Finanzas revisa trimestralmente la rentabilidad por cliente y puede bloquear esquemas comerciales que no sean sostenibles.
El cumplimiento del margen mínimo no autoriza a superar los límites de descuento establecidos para cada canal."""
    }
]


def simular_recuperacion_semantica():
    """Demostración conceptual de recuperación semántica con las consultas del caso."""
    consultas = [
        "¿Qué descuento máximo puedo ofrecer a un distribuidor que compra una estiba completa de gaseosas?",
        "¿Puedo ofrecer combos de distintos sabores a una tienda de barrio?",
        "¿Qué restricciones aplican a los descuentos de lanzamiento de una bebida en una cadena regional?",
    ]

    print("=== CASO EMBOTELLADORA SANTANDER S.A.S. ===")
    print(f"Total de políticas registradas: {len(DOCUMENTOS_SANTANDER)}\n")

    for i, q in enumerate(consultas, start=1):
        print(f"Consulta {i}: '{q}'")
        if "distribuidor" in q.lower() or "estiba" in q.lower():
            doc = next(d for d in DOCUMENTOS_SANTANDER if d["id"] == "descuentos_mayoristas")
        elif "combo" in q.lower() or "tienda" in q.lower():
            doc = next(d for d in DOCUMENTOS_SANTANDER if d["id"] == "combos_multisabor")
        else:
            doc = next(d for d in DOCUMENTOS_SANTANDER if d["id"] == "lanzamientos_nuevos_productos")

        print(f"-> Top 1 Recuperado: [{doc['id']}] (Canal: {doc['canal']})")
        print(f"   Contenido clave: {doc['texto'][:160]}...\n")


if __name__ == "__main__":
    simular_recuperacion_semantica()

