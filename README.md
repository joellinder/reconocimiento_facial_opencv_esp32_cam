<h1 align="center">Sistema de Reconocimiento Facial con Flask</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/Flask-Framework-green" alt="Flask">
  <img src="https://img.shields.io/badge/OpenCV-4.x-orange" alt="OpenCV">
  <img src="https://img.shields.io/badge/face_recognition-1.x-red" alt="Face Recognition">
</p>

<h2>📌 Descripción</h2>
<p>
Este proyecto implementa un <strong>sistema de detección y reconocimiento facial en tiempo real</strong> utilizando 
<strong>Flask</strong>, <strong>OpenCV</strong> y la librería <strong>face_recognition</strong>.  
Está diseñado para trabajar con una <strong>cámara ESP32-CAM</strong>, permitiendo gestionar usuarios autorizados, registrar intrusos y visualizar transmisiones en vivo desde una interfaz web.
</p>

<hr>

<h2>📹 Video de Demostración</h2>
<p>
Puedes ver el sistema en funcionamiento aquí:  
<a href="video_demo.mp4" target="_blank">🎥 Ver Video Demo</a>  
<em>(Incluye el archivo <code>video_demo.mp4</code> en la carpeta raíz del repositorio)</em>
</p>

<hr>

<h2>🏗 Arquitectura</h2>
<ul>
  <li><strong>Capa Web (Flask)</strong>: Autenticación, vistas HTML, API JSON.</li>
  <li><strong>Motor de Reconocimiento</strong>: Procesamiento de video, detección y comparación de rostros.</li>
  <li><strong>Persistencia</strong>: Base de datos SQLite + almacenamiento en sistema de archivos.</li>
  <li><strong>Dispositivo de captura</strong>: ESP32-CAM como fuente de video MJPEG.</li>
</ul>

<hr>

<h2>💻 Requisitos</h2>

<h3>Hardware</h3>
<ul>
  <li>PC o servidor con <strong>Python 3.8+</strong></li>
  <li><strong>ESP32-CAM</strong> con firmware MJPEG</li>
  <li>Cámara ≥ 640x480 px</li>
  <li>Espacio suficiente para imágenes y base de datos</li>
</ul>

<h3>Software</h3>
<ul>
  <li>Linux, Windows o macOS</li>
  <li>Python 3.8+</li>
  <li>Navegador web (Chrome, Firefox, Edge)</li>
  <li>Dependencias en <code>requirements.txt</code></li>
</ul>

<hr>

<h2>⚙️ Instalación</h2>
<pre>
# 1. Clonar repositorio
git clone https://github.com/usuario/sistema-reconocimiento-facial.git
cd sistema-reconocimiento-facial

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
export SECRET_KEY="clave_segura"
export ESP32_STREAM_URL="http://ip_esp32:puerto"

# 5. Crear carpetas necesarias
mkdir -p data/autorizados data/intrusos

# 6. Ejecutar aplicación
python app.py
</pre>

<hr>

<h2>🔧 Configuración</h2>
<ul>
  <li><code>SECRET_KEY</code>: clave para sesiones Flask.</li>
  <li><code>ESP32_STREAM_URL</code>: URL del stream MJPEG de la ESP32-CAM.</li>
  <li><code>AUTH_TOLERANCE</code> y <code>INTRUSO_TOLERANCE</code>: tolerancias para la coincidencia facial.</li>
  <li><code>Debug</code>: desactivar en producción.</li>
</ul>

<hr>

<h2>🚀 Uso</h2>
<ol>
  <li>Abrir el navegador y acceder a la URL del servidor.</li>
  <li>Iniciar sesión con credenciales válidas.</li>
  <li>Acceder a la sección de transmisión para ver la cámara.</li>
  <li>Registrar usuarios autorizados cargando una imagen o desde la cámara.</li>
  <li>Revisar y gestionar registros de intrusos.</li>
  <li>Administrar usuarios (solo rol administrador).</li>
</ol>

<hr>

<h2>🛠 Mantenimiento</h2>
<ul>
  <li>Respaldar la base de datos y carpetas <code>data</code>.</li>
  <li>Rotar <code>SECRET_KEY</code> periódicamente.</li>
  <li>Actualizar dependencias con precaución.</li>
  <li>Limpiar imágenes obsoletas.</li>
</ul>

<hr>

<h2>🔒 Seguridad</h2>
<ul>
  <li>Cambiar credenciales por defecto.</li>
  <li>Usar HTTPS para transmisión.</li>
  <li>Restringir acceso a la interfaz de administración.</li>
  <li>Implementar CSRF en formularios.</li>
</ul>

<hr>

<h2>📂 Estructura del Proyecto</h2>
<pre>
├── app.py
├── requirements.txt
├── static/
├── templates/
├── data/
│   ├── autorizados/
│   └── intrusos/
├── database.sqlite
└── video_demo.mp4
</pre>

<hr>

<h2>👨‍💻 Autor</h2>
<p>
<strong>Equipo de Desarrollo</strong><br>
📅 Versión 1.6 – Agosto 2025
</p>
