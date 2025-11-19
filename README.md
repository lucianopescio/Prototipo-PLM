# Sistema PLM - Prototipo de Análisis de Proteínas

Sistema integral de análisis de proteínas que combina modelos de lenguaje de proteínas (PLM), laboratorio virtual y gemelo digital para investigación biotecnológica avanzada.

##  INICIO RÁPIDO

###  **Instalación Automática (RECOMENDADA)**
```cmd
# 1. Extraer ZIP y abrir CMD en la carpeta del proyecto
# 2. Ejecutar diagnóstico (instala todo automáticamente):
diagnostico.bat

# 3. Iniciar sistema:
iniciar.bat

# 4. Abrir navegador: http://localhost:3000
```

###  **Credenciales de Acceso**
- **Usuario Demo:** `demo@plm.com` / `plm123`
- **Administrador:** `admin@plm.com` / `admin123`
- **Usuario Test:** `test@test.com` / `123`

###  **Prerrequisitos**
- Python 3.8+ ( **Con "Add to PATH" marcado**)
- Node.js LTS
- Windows 10/11

## Características Principales

- **Análisis PLM:** Procesamiento con ESM-2, ProtBERT, ProtTrans, AlphaFold
- **Laboratorio Virtual:** Simulaciones SimPy de experimentos bioquímicos
- **Gemelo Digital:** Modelado dinámico de biorreactores industriales
- **Dashboard Interactivo:** Visualización tiempo real con Recharts
- **Reportes Multi-formato:** PDF, CSV, JSON, HTML automáticos
- **Gestión Completa:** CRUD de secuencias, datasets y experimentos

## Instalación Manual

### Instalación rápida

#### Opción 1 Desde ZIP (evaluación)
```cmd
# Extraer ZIP a carpeta local
# Abrir CMD en la carpeta del proyecto
diagnostico.bat    # Configura todo automáticamente
iniciar.bat        # Inicia el sistema
```

#### Opción 2: Desde archivo ZIP descargado
```bash
# 1. Descomprimir el archivo ZIP
# 2. Abrir carpeta del proyecto
# 3. Ejecutar:
iniciar.bat
```

**Nota:** El iniciador crea automáticamente el entorno virtual e instala todas las dependencias.

El sistema se abre automáticamente en http://localhost:3000

### Instalación manual

1. Crear entorno virtual Python:
```bash
python -m venv .venv
```

2. Activar entorno virtual:
```bash
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Instalar dependencias del frontend:
```bash
cd frontend
npm install
cd ..
```

5. Iniciar servicios:
```bash
# Terminal 1 - Backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## URLs del Sistema

- Interfaz Web: http://localhost:3000
- API Backend: http://127.0.0.1:8000
- Documentación API: http://127.0.0.1:8000/docs
- API Interactiva: http://127.0.0.1:8000/redoc

## Uso del Sistema

### Gestión de Secuencias
- Navegar a "Gestión de Datos" en la barra lateral
- Cargar secuencias proteícas en formato FASTA o texto plano
- Visualizar y administrar biblioteca de secuencias

### Análisis PLM
- Entrar a "Análisis PLM"
- Seleccionar una secuencia cargada
- Ejecutar análisis con modelos ESM-2
- Visualizar predicciones de estructura y función

### Laboratorio Virtual
- Ingresar a "Laboratorio Virtual"
- Configurar experimentos de cultivo celular
- Ajustar parámetros: temperatura, pH, nutrientes 
- Ejecutar simulaciones y analizar resultados

### Gemelo Digital
- Ir a "Gemelo Digital"
- Modelar procesos de biorreactor
- Optimizar condiciones de cultivo
- Visualizar métricas en tiempo real

### Reportes PDF
- Hacer clic en "Descargar Reporte" en cualquier módulo
- Se genera automáticamente un PDF científico
- Incluye gráficos, datos y análisis completos

## Arquitectura del Sistema

```
Sistema PLM/
├── backend/          # API FastAPI
├── frontend/         # Interfaz React
├── database/         # Configuración de BD
├── modules/          # Módulos de análisis
├── docs/             # Documentación
└── tests/            # Pruebas automatizadas
```

## Configuración

Crear archivo `.env` en la raíz:

```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=plm_database
API_HOST=127.0.0.1
API_PORT=8000
VITE_API_URL=http://localhost:8000
```

##  Funcionalidades Técnicas

### Análisis PLM
- **Modelo**: ESM-2 (Evolutionary Scale Modeling)
- **Capacidades**: 
  - Predicción de estructura secundaria
  - Análisis de sitios activos
  - Predicción de función proteica
  - Cálculo de métricas de estabilidad

### Laboratorio Virtual
- **Simulaciones**:
  - Cinética de crecimiento microbiano
  - Producción de metabolitos
  - Optimización de medios de cultivo
  - Análisis de viabilidad celular

### Gemelo Digital
- **Modelado**:
  - Biorreactores de tanque agitado
  - Control de procesos automatizado
  - Optimización en tiempo real
  - Predicción de rendimientos

## Ejemplos de Uso

### Secuencia de ejemplo
```
MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN
```

### API Endpoints principales
```bash
GET /secuencias/
POST /analizar_plm/
POST /generar_reporte_plm/
```

## Desarrollo

1. Fork el proyecto
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Solución de Problemas

### Error: Puerto en uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: Entorno virtual no encontrado
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Error: Base de datos no conecta
- El sistema usa MongoDB Atlas por defecto
- Para usar MongoDB local, actualizar `MONGO_URI` en `.env`

### Logs
- Backend: Terminal donde se ejecuta uvicorn
- Frontend: Consola del navegador (F12)

## Soporte

- Issues: GitHub Issues del repositorio
- Documentación: Ver `README_INICIADORES.md`

## Licencia

Licencia MIT - ver archivo LICENSE

## Tecnologías utilizadas

- ESM-2: Meta AI Research
- FastAPI: Framework web Python
- React: Biblioteca de interfaz de usuario
- MongoDB: Base de datos NoSQL
- ReportLab: Generación de PDFs

## Estado del Proyecto

- Backend API: Integramente funcional
- Frontend React: Interfaz completa
- Análisis PLM: Implementado y probado
- Laboratorio Virtual: Operativo
- Gemelo Digital: Funcional
- Generación PDF: Implementado
- Base de Datos: MongoDB integrado
- Iniciadores Automáticos: Funcionan Ok

Versión: 1.0.0
Última actualización: Noviembre 2025