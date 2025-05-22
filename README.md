# 📱 Aplicación de Revisión Preoperacional para Conductores

Este proyecto es una **aplicación web desarrollada con [Flet](https://flet.dev/)** en Python que permite a conductores registrar inspecciones preoperacionales de sus vehículos, adjuntar evidencias, visualizar registros y exportar reportes en PDF. Los datos se almacenan en **MongoDB**, y toda la aplicación se ejecuta en contenedores utilizando Docker.

---

## 🧰 Tecnologías utilizadas

- 🐍 Python 3.9+
- 🎨 Flet (framework para construir interfaces gráficas con Python)
- 🐳 Docker y Docker Compose
- 📦 MongoDB como base de datos NoSQL
- 📄 ReportLab para generación de reportes en PDF

---

## 📁 Estructura del proyecto

```
my_app/
├── data/                    # Datos persistentes de MongoDB (excluidos del repo)
├── exportados/              # PDF generados al exportar las inspecciones
├── src/
│   ├── assets/              # Recursos estáticos (íconos, imágenes, etc.)
│   ├── controlador/         # Lógica del controlador
│   ├── modelo/              # Interacciones con la base de datos
│   ├── storage/             # Gestión de archivos cargados
│   ├── vista/               # Interfaces con Flet
│   └── main.py              # Punto de entrada de la aplicación
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚙️ Requisitos previos

Antes de ejecutar la aplicación asegúrate de tener instalado:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

## 🚀 Instrucciones de instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/Bri0714/Movil-Flet.git
cd Movil-Flet
```

### 2. Crea las carpetas necesarias (si no existen)

```bash
mkdir -p data/db
mkdir -p my_app/exportados
```

Estas carpetas se utilizan como volúmenes para persistencia de datos de MongoDB y almacenamiento de archivos PDF exportados.

### 3. Construye y levanta los servicios

```bash
docker-compose up --build
```

Esto levantará:
- 🛢️ Un contenedor `mongo` corriendo en el puerto 27017
- 🖥️ Un contenedor `flet_app` accesible desde http://localhost:8550

---

## 💻 Uso de la aplicación

1. Accede a la aplicación desde tu navegador en http://localhost:8550.
2. Completa el formulario con los datos del conductor.
3. Adjunta evidencias fotográficas del vehículo.
4. Exporta el reporte en formato PDF.
5. Los reportes se guardan automáticamente en `my_app/exportados/`.

---

## 🧹 Apagar los contenedores

Para detener la aplicación:

```bash
docker-compose down
```

Esto apagará los servicios pero mantendrá los datos persistentes en `data/db`.

---

## ⚠️ Notas importantes

- La carpeta `data/` contiene archivos internos de MongoDB y no debe subirse al repositorio. Ya está excluida por `.gitignore`.
- Los archivos en `exportados/` se generan dinámicamente y tampoco deben ser versionados.
- Si accidentalmente subiste archivos muy pesados, puedes usar [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) para limpiar el historial de Git.

---

## 📄 Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE). Puedes usarlo, modificarlo y distribuirlo libremente con atribución.

---

## 👤 Autor

**Desarrollado por:**
- Brian Alexander Amezquita Parada
- 🔗 [GitHub - Bri0714](https://github.com/Bri0714)
