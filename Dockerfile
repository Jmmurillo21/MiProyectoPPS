# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Copiar todo el proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir flask mysql-connector-python bcrypt

# Exponer el puerto 5000
EXPOSE 5000

# Comando para correr Flask
CMD ["python", "app.py"]
