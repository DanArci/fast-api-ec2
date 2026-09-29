# Base image oficial de Python para ejecutar la aplicación FastAPI.
FROM python:3.12-slim

# Definimos el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copiamos primero el archivo de dependencias para aprovechar la caché de Docker.
COPY requirements.txt ./

# Actualizamos pip e instalamos las dependencias del proyecto.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente de la aplicación.
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponemos el puerto que utilizará FastAPI/Uvicorn.
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Comando de arranque de la API.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]