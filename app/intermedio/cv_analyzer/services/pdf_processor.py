import io
from typing import Iterator, Optional, Union

# Constantes de seguridad y protección de recursos (Anti-DoS)
MAX_TAMANO_BYTES = 10 * 1024 * 1024   # Límite de 10 MB por archivo
MAX_PAGINAS_PERMITIDAS = 20          # Un CV profesional no excede 20 páginas
MAX_CARACTERES_TOTALES = 35000       # Prevenir desbordamiento de ventana de contexto y Financial DoS


class ResultadoTextoPDF(str):
    """
    Resultado compatible de forma dual:
    - Como cadena (`str`): contiene el texto extraído o el mensaje de error (iniciando con 'Error: ').
    - Como tupla desempaquetable (`texto, error = extraer_texto_pdf(...)`): produce `(texto, error)`.
    """
    texto: str
    error: Optional[str]
    es_error: bool

    def __new__(cls, texto: str = "", error: Optional[str] = None) -> "ResultadoTextoPDF":
        if error is not None:
            error_msg = error if error.startswith("Error:") else f"Error: {error}"
            instance = super().__new__(cls, error_msg)
            instance.texto = ""
            instance.error = error_msg
            instance.es_error = True
            return instance

        instance = super().__new__(cls, texto)
        instance.texto = texto
        instance.error = None
        instance.es_error = False
        return instance

    def __iter__(self) -> Iterator[Optional[str]]:
        yield self.texto
        yield self.error


def _error_pdf(mensaje: str) -> ResultadoTextoPDF:
    """Construye un resultado de error estandarizado."""
    return ResultadoTextoPDF(texto="", error=mensaje)


def extraer_texto_pdf(archivo_pdf: Union[io.BytesIO, bytes, str, object]) -> ResultadoTextoPDF:
    """
    Extrae el texto de un archivo PDF en memoria recorriendo cada una de sus páginas
    y aplicando controles estrictos de seguridad contra Denegación de Servicio (DoS),
    archivos sobredimensionados y desbordamiento de contexto.

    Soporta tanto uso directo como `str` (`texto = extraer_texto_pdf(archivo)`)
    como desempaquetado (`texto, error = extraer_texto_pdf(archivo)`).

    Args:
        archivo_pdf: Archivo PDF en formato UploadedFile (Streamlit), BytesIO, bytes o ruta de archivo.

    Returns:
        ResultadoTextoPDF: Subclase de `str` con soporte de desempaquetado `(texto, error)`.
    """
    if archivo_pdf is None:
        return _error_pdf("No se ha proporcionado ningún archivo PDF para procesar.")

    stream = None
    try:
        # 1. Control de tamaño máximo de archivo
        if isinstance(archivo_pdf, bytes):
            if not archivo_pdf:
                return _error_pdf("El archivo PDF cargado está vacío (0 bytes).")
            if len(archivo_pdf) > MAX_TAMANO_BYTES:
                return _error_pdf(
                    f"El archivo excede el tamaño máximo de seguridad permitido ({MAX_TAMANO_BYTES // (1024 * 1024)} MB)."
                )
            stream = io.BytesIO(archivo_pdf)
        elif hasattr(archivo_pdf, "read"):
            if hasattr(archivo_pdf, "size") and isinstance(archivo_pdf.size, (int, float)) and archivo_pdf.size > MAX_TAMANO_BYTES:
                return _error_pdf(
                    f"El archivo cargado ({round(archivo_pdf.size / (1024 * 1024), 1)} MB) "
                    f"excede el límite máximo permitido de {MAX_TAMANO_BYTES // (1024 * 1024)} MB."
                )

            contenido = archivo_pdf.read()
            if hasattr(archivo_pdf, "seek"):
                archivo_pdf.seek(0)

            if not contenido:
                return _error_pdf("El archivo PDF cargado está vacío (0 bytes).")

            if len(contenido) > MAX_TAMANO_BYTES:
                return _error_pdf(
                    f"El archivo cargado excede el límite de tamaño seguro ({MAX_TAMANO_BYTES // (1024 * 1024)} MB)."
                )

            stream = io.BytesIO(contenido)
        elif isinstance(archivo_pdf, str):
            with open(archivo_pdf, "rb") as f:
                contenido = f.read()
                if not contenido:
                    return _error_pdf("El archivo PDF en disco está vacío (0 bytes).")
                if len(contenido) > MAX_TAMANO_BYTES:
                    return _error_pdf(
                        f"El archivo en disco supera el límite permitido ({MAX_TAMANO_BYTES // (1024 * 1024)} MB)."
                    )
                stream = io.BytesIO(contenido)
        else:
            return _error_pdf("Formato o tipo de archivo no válido para procesamiento seguro.")

        # 2. Inicialización de motor de lectura seguro
        lector = None
        try:
            import pypdf
            lector = pypdf.PdfReader(stream)
        except Exception:
            try:
                import PyPDF2
                stream.seek(0)
                lector = PyPDF2.PdfReader(stream)
            except Exception as e_init:
                return _error_pdf(f"Error al procesar la estructura interna del PDF: {type(e_init).__name__}")

        if lector is None or len(lector.pages) == 0:
            return _error_pdf("El archivo PDF no contiene páginas legibles o está corrupto.")

        # 3. Control de cantidad máxima de páginas
        total_paginas = len(lector.pages)
        if total_paginas > MAX_PAGINAS_PERMITIDAS:
            return _error_pdf(
                f"El documento contiene {total_paginas} páginas. Por motivos de seguridad y "
                f"enfoque en hojas de vida, solo se procesan documentos de hasta {MAX_PAGINAS_PERMITIDAS} páginas."
            )

        # 4. Extracción página por página con control de longitud
        paginas_texto = []
        caracteres_acumulados = 0

        for indice, pagina in enumerate(lector.pages):
            try:
                texto_pagina = pagina.extract_text() or ""
                texto_limpio = texto_pagina.strip()

                if texto_limpio:
                    if caracteres_acumulados + len(texto_limpio) > MAX_CARACTERES_TOTALES:
                        espacio_restante = MAX_CARACTERES_TOTALES - caracteres_acumulados
                        if espacio_restante > 0:
                            paginas_texto.append(
                                f"--- Página {indice + 1} (Truncada por límite de seguridad) ---\n"
                                f"{texto_limpio[:espacio_restante]}\n[AVISO: Contenido truncado por longitud máxima de seguridad]"
                            )
                        break

                    paginas_texto.append(f"--- Página {indice + 1} ---\n{texto_limpio}")
                    caracteres_acumulados += len(texto_limpio)

            except Exception:
                paginas_texto.append(f"--- Página {indice + 1} ---\n[Aviso: Página no procesable]")

        texto_completo = "\n\n".join(paginas_texto).strip()

        if not texto_completo:
            return _error_pdf(
                "El archivo PDF no contiene texto legible extraíble. "
                "Es probable que corresponda a un documento escaneado exclusivamente como imagen "
                "(requiere OCR previo) o con cifrado de capas de texto."
            )

        return ResultadoTextoPDF(texto=texto_completo, error=None)

    except Exception as e:
        return _error_pdf(f"Error de lectura al procesar el archivo: {type(e).__name__}")

    finally:
        if stream is not None:
            try:
                stream.close()
            except Exception:
                pass
