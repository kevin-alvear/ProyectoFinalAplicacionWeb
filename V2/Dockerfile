# library_project/Dockerfile

# 1. Usar una imagen oficial de Python como base
FROM python:3.10-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requerimientos primero (para aprovechar el caché de Docker)
#    Nota: Asumimos que requirements.txt estará dentro de la carpeta backend
COPY ./backend/requirements.txt /app/requirements.txt

# 4. Instalar las dependencias de Python
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 5. Copiar todo el código de tu aplicación (la carpeta backend) al contenedor
COPY ./backend /app/backend

# 6. Comando para ejecutar tu aplicación con Uvicorn
#    --host 0.0.0.0 es CRUCIAL para que sea visible fuera del contenedor.
#    --reload es genial para desarrollo, reinicia el servidor al detectar cambios.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]