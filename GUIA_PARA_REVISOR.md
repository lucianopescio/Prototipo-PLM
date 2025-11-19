#  GUÍA COMPLETA PARA REVISOR DEL PROYECTO - Sistema PLM

##  ARCHIVOS 

###  **RAÍZ DEL PROYECTO** (Prototipo PLM/)
```
 iniciar.bat                    # INICIADOR PRINCIPAL - ATENCION ESPECIAL
 README.md                      # Documentación completa
 requirements.txt               # Dependencias Python
 .gitignore                     # Exclusiones Git
 .env.example                   # Plantilla configuración
 iniciar_sistema.bat            # Iniciador Windows avanzado
 iniciar_sistema.ps1            # Iniciador PowerShell
 iniciar_sistema.py             # Iniciador multiplataforma
 iniciar_sistema.js             # Iniciador Node.js
 crear_acceso_directo.ps1       # Creador acceso directo
 README_INICIADORES.md          # Documentación iniciadores
 check_env.py                   # Verificador entorno
```

###  **backend/** 
```
 main.py                       # Servidor principal FastAPI
 Todos los archivos .py        # Código del servidor
 Todas las carpetas            # Rutas, modelos, etc.
```

###  **frontend/** 
```
 package.json                  # Dependencias React/Node.js
 .gitignore                    # Exclusiones específicas frontend
 tsconfig.json                 # Configuración TypeScript
 vite.config.ts                # Configuración Vite
 index.html                    # Página principal
 src/                          # TODO el código React
 public/                       # Archivos estáticos
```

###  **database/** 
```
 config.py                     # Configuración base de datos
 models.py                     # Modelos de datos
 init_db.py                    # Inicializador BD
```

###  **modules/** 
```
 plm.py                       # Análisis PLM
 laboratorio.py               # Laboratorio virtual
 gemelo_digital.py            # Gemelo digital
```

###  **tests/** 
```
 Todos los archivos test_*.py  # Pruebas automatizadas
```

###  **docs/** 
```
 manual_usuario.md            # Manual de usuario
 INSTALL.md                   # Guía instalación
```

---


##  **INSTRUCCIONES PARA USO DEL SISTEMA **

### **PASO 1: DESCARGAR**

#### Opción A: Clonar con Git
```bash
git clone [URL_DEL_REPOSITORIO]
cd prototipo-plm
```

#### Opción B: Descargar ZIP
```bash
# 1. Descargar ZIP desde GitHub
# 2. Descomprimir en una carpeta
# 3. Abrir carpeta del proyecto en terminal
```

### **PASO 2: PRERREQUISITOS**
 tener instalado:
- **Python 3.8+** → https://www.python.org/downloads/
- **Node.js 16+** → https://nodejs.org/
- **Git** → https://git-scm.com/

### **PASO 3: INSTALACIÓN Y ARRANQUE**

#### **Opción A: INSTALACIÓN AUTOMÁTICA (SENCILLO)**
```bash
# Doble clic en:
iniciar.bat

# O desde terminal:
.\iniciar.bat
```

**¿Qué hace automáticamente?**
1.  Crea el entorno virtual Python (.venv)
2.  Instala todas las dependencias Python
3.  Instala dependencias del frontend (npm)
4.  Inicia backend y frontend
5.  Abre el navegador automáticamente

**¡SISTEMA LISTO!** Se abre automáticamente en el navegador.

#### **Opción B: INSTALACIÓN MANUAL (Si falla la automática)**
```bash
# 1. Crear entorno virtual Python
python -m venv .venv

# 2. Activar entorno virtual
.venv\Scripts\activate

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Instalar dependencias Frontend (Nueva terminal)
cd frontend
npm install
cd ..

# 5. Iniciar Backend (Terminal 1)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# 6. Iniciar Frontend (Terminal 2)
cd frontend
npm run dev
```

### **PASO 4: ACCEDER AL SISTEMA**
- **Interfaz Principal:** http://localhost:3000
- **API Backend:** http://127.0.0.1:8000
- **Documentación API:** http://127.0.0.1:8000/docs

### **PASO 5: CREDENCIALES DE ACCESO**
**Usuario:**
- **Email:** `demo@plm.com`
- **Contraseña:** `plm123`

**Otras opciones disponibles:**
- **Administrador:** `admin@plm.com` / `admin123`
- **Test básico:** `test@test.com` / `123`
- **Evaluador:** `evaluador@plm.com` / `eval2024`

---

##  **GUÍA DE USO**

### 1. Gestión de Secuencias
- Ir a "Gestión de Datos" en la barra lateral
- Cargar secuencias proteicas (formato FASTA o texto)
- Ejemplo de secuencia para probar:
```
MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN
```

### 2. Análisis PLM
- Ir a "Análisis PLM"
- Seleccionar una secuencia cargada
- Hacer clic en "Ejecutar Análisis"
- Ver predicciones de estructura y función

### 3. Laboratorio Virtual
- Acceder a "Laboratorio Virtual"
- Configurar experimentos (temperatura, pH, nutrientes)
- Ejecutar simulación
- Analizar resultados

### 4. Gemelo Digital
- Ir a "Gemelo Digital"
- Configurar parámetros del biorreactor
- Iniciar simulación
- Observar métricas en tiempo real

### 5. Generar Reportes
- En cualquier módulo, hacer clic en "Descargar Reporte"
- Se genera automáticamente un PDF científico

---

##  CONFIGURACIÓN (Opcional)

Si quiere usar MongoDB local:
```bash
# Crear archivo .env en la raíz:
MONGO_URI=mongodb://localhost:27017
DB_NAME=plm_database
API_HOST=127.0.0.1
API_PORT=8000
VITE_API_URL=http://localhost:8000
```

---

## SOLUCIÓN DE PROBLEMAS

### Error: Puerto ocupado
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID [PID] /F
```

### Error: Módulo no encontrado
```bash
# Reinstalar dependencias
pip install -r requirements.txt
cd frontend && npm install
```

### Error: No se conecta a la base de datos
- El sistema usa MongoDB Atlas (cloud) por defecto
- No es necesario instalar MongoDB localmente

---

## PARA SOPORTE

Frente a problemas:
1. Verificar que tiene Python 3.8+ y Node.js 16+
2. Revisar que no hay otros servicios en puertos 3000 y 8000
3. Intentar primero con `iniciar.bat`
4. Si persisten problemas, usar instalación manual

---



## PARA TENER EN CUENTA EL REVISOR ##

**Tiempo estimado de instalación: 2-5 minutos aproximadamente**

**Para uso rápido y sencillo recomiendo que descargue el repositorio y lo descomprima localmente, luego identifique el Iniciador automático recomendado: `iniciar.bat`**,**ya esta configurado para que crear el entorno y arranque automaticamente**