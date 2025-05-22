# Usa una imagen oficial de Python
FROM python:3.9-slim

# Instala las dependencias necesarias para GTK y GStreamer
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libx11-xcb1 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-base \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Establece la variable de entorno PYTHONPATH
ENV PYTHONPATH=/app

# Expone el puerto en el que se ejecutará Flet
EXPOSE 8550

# Comando para ejecutar la aplicación Flet
CMD ["python", "src/main.py"]
# Comando para ejecutar la aplicación Flet
#CMD ["flet", "run", "src/main.py", "-d", "--port", "8550", "--host", "0.0.0.0"]
# Usa el flag --android y deja que CLI determine el entrypoint
#CMD ["flet", "run", "--android", "src/main.py"]
#CMD ["flet","run","--android","src/main.py","--host","0.0.0.0","--port","8550"]
