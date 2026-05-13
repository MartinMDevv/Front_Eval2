# ============================================================
# Dockerfile del Frontend — App Web Flask (Python)
# ============================================================
# Multi-stage build con virtual environment (venv):
#   Stage 1 (builder):    instala dependencias dentro de un venv
#   Stage 2 (production): copia solo el venv listo + el código
#
# ¿Por qué venv y no pip install --user?
#   • Copiar /opt/venv entre stages es trivial (es UNA carpeta).
#   • Con --user habría problemas de PATH entre etapas.
#   • Activamos el venv con ENV PATH para que el binario "python"
#     siempre apunte al de las dependencias.
# ============================================================


# ─── STAGE 1: instalar dependencias en un venv ──────────────
# python:3.11-slim → imagen oficial mínima de Python 3.11
FROM python:3.11-slim AS builder

WORKDIR /app

# Crear un virtual environment aislado en /opt/venv
RUN python -m venv /opt/venv

# Agregar el venv al inicio del PATH:
# así "pip" y "python" usan el binario del venv en los pasos siguientes
ENV PATH="/opt/venv/bin:$PATH"

# Copiar solo el manifiesto de dependencias PRIMERO (cache layer)
COPY requirements.txt .

# Instalar dependencias dentro del venv
#   --no-cache-dir → no guardar caché de pip (imagen más liviana)
RUN pip install --no-cache-dir -r requirements.txt


# ─── STAGE 2: imagen final de producción ────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Crear usuario sin privilegios de root
# -m → crear home directory (algunas libs lo necesitan)
# -u 1001 → UID fijo (no choca con UIDs del host)
RUN useradd -m -u 1001 -s /bin/sh appuser

# Traer el venv completo del stage anterior (con todas las deps)
COPY --from=builder /opt/venv /opt/venv

# Activar el venv también en la imagen final
ENV PATH="/opt/venv/bin:$PATH"

# Otras variables útiles para Python en contenedores:
ENV PYTHONUNBUFFERED=1
# ↑ Hace que print() / logging salgan en tiempo real (no se "bufferiza")
ENV PYTHONDONTWRITEBYTECODE=1
# ↑ Evita crear archivos .pyc dentro del contenedor (innecesarios)

# Copiar el código de la aplicación
# --chown asegura que el usuario no-root sea dueño de los archivos
COPY --chown=appuser:appuser . .

# Eliminar archivos que no deben terminar en la imagen
RUN rm -rf .git .env* __pycache__ *.pyc *.md

# Cambiar al usuario sin privilegios
USER appuser

# Puerto que expone Flask (documentativo)
EXPOSE 5000

# Healthcheck: verifica que Flask responde en la raíz "/"
# Usamos python en vez de curl/wget porque la imagen slim no los trae
# (y así evitamos instalar paquetes extra que aumenten el tamaño).
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/', timeout=5)" || exit 1

# Comando que se ejecuta al arrancar el contenedor
CMD ["python", "app.py"]
