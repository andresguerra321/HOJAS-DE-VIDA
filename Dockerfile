# Usar imagen base ligera oficial
FROM python:3.12-slim

# Evitar escritura de archivos .pyc y habilitar salida en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# Instalar dependencias del sistema y limpiar caché en una sola capa
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación (excluyendo .env según .dockerignore)
COPY . .

# SEGURIDAD: Crear y usar un usuario no privilegiado (Principio de menor privilegio)
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser -s /sbin/nologin appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

# Verificación de salud del contenedor
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/intermedio/cv_analyzer/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
