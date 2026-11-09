# Imagen base ligera de Python
FROM python:3.12-slim

# Evita ficheros .pyc y muestra los logs al momento
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Copiamos primero las dependencias para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY src/ .

# Creamos un usuario sin privilegios y le damos permisos sobre el código
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app
USER appuser

EXPOSE 8000

# Arrancamos la API con uvicorn en el puerto indicado por PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
