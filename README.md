# Prototipo PLM

Este repositorio contiene un prototipo PLM con backend en FastAPI, pruebas en pytest, y componentes para integrar modelos de IA, simulación y análisis de proteínas.

Quick start (Windows, PowerShell)

1. Crear y activar entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

2. Instalar dependencias (nota: paquetes como PyTorch/TensorFlow son grandes):

```powershell
python -m pip install -r requirements.txt
```

Si tienes GPU y quieres builds con CUDA, instala PyTorch/TensorFlow según sus guías oficiales.

3. Ejecutar tests:

```powershell
python -m pytest -q
```

4. Iniciar servicios opcionales con Docker Compose (MongoDB):

```powershell
docker compose up -d
```

5. Correr backend local (desde `backend/`):

```powershell
& '.\.venv\Scripts\python.exe' -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

6. Correr Streamlit (UI rápido):

```powershell
streamlit run streamlit_app.py
```

Notas y recomendaciones
- MongoDB: configura `MONGO_URI` en `.env` para apuntar a Atlas si quieres entorno remoto.
- Colab / SageMaker: para trabajos pesados, usa notebooks dedicados; ver `notebooks/` para plantillas.
- Docker: este repo incluye `docker-compose.yml` para MongoDB. Puedes crear contenedores para la API y Streamlit si lo deseas.

Próximos pasos sugeridos
- Generar notebooks de ejemplo para: análisis de proteínas con Transformers, entrenamiento/inferencia con PyTorch, simulación con SimPy+Gym.
- Crear `Dockerfile` para backend y Streamlit si quieres despliegue contenedorizado completo.
- Añadir scripts de CI para ejecutar tests y linters.
