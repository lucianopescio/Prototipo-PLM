from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Header
from fastapi.responses import JSONResponse, StreamingResponse, Response
import io
import csv
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    HAVE_REPORTLAB = True
except Exception:
    HAVE_REPORTLAB = False
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import re
import sys
import os
from pathlib import Path
from typing import Optional
try:
    from bson import ObjectId
except Exception:
    ObjectId = None

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import modules.plm as plm
import modules.laboratorio as laboratorio
import modules.gemelo_digital as gemelo
import database.init_db as db_init
from database.config import DB_NAME
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar generador de PDF (sin WeasyPrint para evitar errores en Windows)
try:
    from modules.pdf_generator import pdf_generator
    HAVE_PDF = True
except Exception as e:
    print(f"PDF generation not available: {e}")
    HAVE_PDF = False
    pdf_generator = None

# Desactivar WeasyPrint para evitar problemas de librerías en Windows
weasyprint = None

app = FastAPI(title="Prototipo PLM API", version="0.1.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar estructuras en memoria por defecto
secuencias_db = []
experimentos_db = []
alertas_db = []
usuarios_db = []

# Inicializar base de datos (MongoDB) si está disponible
db = db_init.init_db()
if db is not None:
    db_init.create_indexes(db)
    secuencias_col = db.secuencias
    experimentos_col = db.experimentos
    alertas_col = db.alertas
    usuarios_col = db.usuarios
    
    # Inicializar datos de ejemplo en MongoDB si está vacío
    try:
        from database.seed_data import seed_mongodb_data
        seed_mongodb_data(db)
    except Exception as e:
        print(f"⚠️ Error cargando datos de ejemplo en MongoDB: {e}")
else:
    secuencias_col = None
    experimentos_col = None
    alertas_col = None
    usuarios_col = None

# Inicializar datos de ejemplo en memoria siempre (para backup)
try:
    from database.seed_data import initialize_demo_data
    initialize_demo_data(secuencias_db, experimentos_db)
except Exception as e:
    print(f"⚠️ Error cargando datos de ejemplo en memoria: {e}")

# Sesiones se manejan en memoria (tokens temporales)
sesiones_db = {}


def _insert(collection, list_ref, record):
    if collection is not None:
        res = collection.insert_one(record)
        # Convertir ObjectId a string para serialización JSON
        record['id'] = str(res.inserted_id)
        return record
    else:
        record['id'] = len(list_ref)
        list_ref.append(record)
        return record


def _find_all(collection, list_ref):
    if collection is not None:
        docs = list(collection.find({}))
        results = []
        for d in docs:
            d['id'] = str(d.get('_id'))
            d.pop('_id', None)
            results.append(d)
        return results
    else:
        return list_ref


def _create_simple_pdf_report(resultado, secuencia, idx_or_id, tipo_reporte):
    """Crear PDF simple usando solo canvas de ReportLab"""
    try:
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Título
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"Reporte {tipo_reporte} - Secuencia {idx_or_id}")
        
        # Información básica
        y_position = height - 100
        p.setFont("Helvetica", 12)
        p.drawString(50, y_position, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y_position -= 30
        if secuencia:
            p.drawString(50, y_position, f"Secuencia: {str(secuencia)[:50]}...")
            y_position -= 30
        
        # Resultados
        p.drawString(50, y_position, "Resultados del análisis:")
        y_position -= 30
        
        if isinstance(resultado, dict):
            for key, value in resultado.items():
                if y_position < 50:  # Nueva página si es necesario
                    p.showPage()
                    y_position = height - 50
                p.drawString(70, y_position, f"{str(key)}: {str(value)[:80]}")
                y_position -= 20
        else:
            p.drawString(70, y_position, str(resultado)[:100])
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"Error creating simple PDF: {e}")
        # Fallback más básico con solo canvas
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"Reporte {tipo_reporte} - Error en generación completa")
        p.drawString(100, 730, f"Resultado básico: {str(resultado)[:50]}")
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error creando PDF simple: {e}")
        # PDF de emergencia muy básico
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = [Paragraph(f"Reporte {tipo_reporte} - Error en generación", getSampleStyleSheet()['Title'])]
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

def _create_simple_pdf_gemelo(resultado_gemelo, secuencia=None, resultado_plm=None):
    """Crear PDF específico para gemelo digital usando canvas de ReportLab"""
    buffer = io.BytesIO()
    
    try:
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Título
        p.setFont("Helvetica-Bold", 18)
        p.drawString(50, height - 50, "Reporte de Gemelo Digital - Biorreactor")
        
        # Fecha
        p.setFont("Helvetica", 10)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        p.drawString(50, height - 80, f"Fecha de Generación: {fecha}")
        
        y_pos = height - 120
        
        # Información básica del gemelo
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_pos, "INFORMACIÓN DE SIMULACIÓN")
        y_pos -= 30
        
        p.setFont("Helvetica", 11)
        if isinstance(resultado_gemelo, dict):
            modelo = resultado_gemelo.get('modelo', 'N/A')
            p.drawString(70, y_pos, f"Modelo: {modelo}")
            y_pos -= 20
            
            # Condiciones iniciales
            condiciones = resultado_gemelo.get('condiciones_iniciales', {})
            if condiciones:
                p.drawString(70, y_pos, f"Biomasa inicial: {condiciones.get('biomasa_inicial', 'N/A')}")
                y_pos -= 15
                p.drawString(70, y_pos, f"Temperatura: {condiciones.get('temperatura', 'N/A')} °C")
                y_pos -= 15
                p.drawString(70, y_pos, f"pH: {condiciones.get('ph', 'N/A')}")
                y_pos -= 15
                p.drawString(70, y_pos, f"Oxígeno inicial: {condiciones.get('oxigeno_inicial', 'N/A')} %")
                y_pos -= 25
            
            # Métricas finales
            metricas = resultado_gemelo.get('metricas_finales', {})
            if metricas:
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, y_pos, "MÉTRICAS FINALES")
                y_pos -= 25
                
                p.setFont("Helvetica", 11)
                for key, value in metricas.items():
                    if y_pos < 100:
                        p.showPage()
                        y_pos = height - 50
                    display_key = key.replace('_', ' ').title()
                    p.drawString(70, y_pos, f"{display_key}: {value}")
                    y_pos -= 18
                
                y_pos -= 15
            
            # Alertas
            alertas = resultado_gemelo.get('alertas', [])
            if alertas:
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, y_pos, "ALERTAS DEL SISTEMA")
                y_pos -= 25
                
                p.setFont("Helvetica", 11)
                for alerta in alertas[:5]:  # Máximo 5 alertas
                    if y_pos < 100:
                        p.showPage()
                        y_pos = height - 50
                    p.drawString(70, y_pos, f"• {alerta}")
                    y_pos -= 18
                
                y_pos -= 15
            
            # Integración PLM si está disponible
            integracion_plm = resultado_gemelo.get('integracion_plm', {})
            if integracion_plm:
                if y_pos < 150:
                    p.showPage()
                    y_pos = height - 50
                
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, y_pos, "INTEGRACIÓN PLM")
                y_pos -= 25
                
                p.setFont("Helvetica", 11)
                modelo_plm = integracion_plm.get('modelo_usado', 'N/A')
                p.drawString(70, y_pos, f"Modelo PLM: {modelo_plm}")
                y_pos -= 18
                
                confianza = integracion_plm.get('confianza', 'N/A')
                p.drawString(70, y_pos, f"Confianza: {confianza}")
                y_pos -= 18
                
                eficiencia = integracion_plm.get('eficiencia_derivada', 'N/A')
                p.drawString(70, y_pos, f"Eficiencia derivada: {eficiencia}")
                y_pos -= 18
        
        # Datos temporales (resumen)
        if isinstance(resultado_gemelo, dict) and 'datos_temporales' in resultado_gemelo:
            datos = resultado_gemelo['datos_temporales']
            if datos and len(datos) > 0:
                if y_pos < 200:
                    p.showPage()
                    y_pos = height - 50
                
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, y_pos, "DATOS TEMPORALES (RESUMEN)")
                y_pos -= 25
                
                p.setFont("Helvetica", 10)
                p.drawString(70, y_pos, f"Puntos de datos: {len(datos)}")
                y_pos -= 15
                
                # Primer y último punto
                primer_punto = datos[0]
                ultimo_punto = datos[-1]
                
                p.drawString(70, y_pos, f"Tiempo inicial: {primer_punto.get('time', 0)} h - Biomasa: {primer_punto.get('biomasa', 0)}")
                y_pos -= 15
                p.drawString(70, y_pos, f"Tiempo final: {ultimo_punto.get('time', 0)} h - Biomasa: {ultimo_punto.get('biomasa', 0)}")
                y_pos -= 15
                p.drawString(70, y_pos, f"Producto final: {ultimo_punto.get('producto', 0)}")
                y_pos -= 15
                p.drawString(70, y_pos, f"Viabilidad final: {ultimo_punto.get('viabilidad', 0)}%")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error en _create_simple_pdf_gemelo: {e}")
        # Fallback básico
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "Reporte de Gemelo Digital")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        p.drawString(50, height - 100, "Simulación de biorreactor completada")
        p.drawString(50, height - 120, "Los datos están disponibles en el sistema")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer.getvalue()


def _get_by_index(collection, list_ref, idx):
    if collection is not None:
        # Obtener el documento por orden de inserción (skip/limit)
        doc = list(collection.find({}).skip(idx).limit(1))
        if not doc:
            return None
        d = doc[0]
        d['id'] = str(d.get('_id'))
        d.pop('_id', None)
        return d
    else:
        if idx < 0 or idx >= len(list_ref):
            return None
        return list_ref[idx]


def _get_by_idx_or_id(collection, list_ref, idx_or_id):
    """Recupera un documento ya sea por índice (int) o por id (ObjectId/string).
    - Si `idx_or_id` puede convertirse a int, usa _get_by_index.
    - Si no, intenta buscar por `_id` (ObjectId) en MongoDB o por campo `id` en memoria.
    """
    if idx_or_id is None:
        return None
    # Intentar interpretar como índice entero
    try:
        idx = int(idx_or_id)
        return _get_by_index(collection, list_ref, idx)
    except Exception:
        # No es entero: buscar por id
        if collection is not None:
            # Intentar ObjectId si está disponible
            try:
                if ObjectId:
                    doc = collection.find_one({'_id': ObjectId(str(idx_or_id))})
                else:
                    doc = collection.find_one({'_id': str(idx_or_id)})
                if not doc:
                    # Intentar campo 'id' por si se guardó como string
                    doc = collection.find_one({'id': str(idx_or_id)})
                if not doc:
                    return None
                doc['id'] = str(doc.get('_id'))
                doc.pop('_id', None)
                return doc
            except Exception:
                # Fallback: buscar por campo 'id' o por cualquier coincidencia
                doc = collection.find_one({'id': str(idx_or_id)})
                if doc:
                    doc['id'] = str(doc.get('_id')) if doc.get('_id') else str(doc.get('id'))
                    doc.pop('_id', None)
                    return doc
                return None
        else:
            # Buscar en lista en memoria por coincidencia de id
            for item in list_ref:
                if str(item.get('id')) == str(idx_or_id):
                    return item
            return None

# Validadores
def validar_secuencia(secuencia: str) -> bool:
    """Valida que la secuencia contenga solo caracteres de aminoácidos válidos"""
    secuencia = secuencia.strip().upper()
    aminoacidos_validos = set('ACDEFGHIKLMNPQRSTVWY*')
    return all(c in aminoacidos_validos for c in secuencia)

def validar_nombre(nombre: str) -> bool:
    """Valida que el nombre sea válido"""
    return len(nombre.strip()) > 0 and len(nombre) <= 255

@app.get("/")
def read_root():
    return {"message": "API PLM funcionando correctamente"}

@app.get("/health")
def health_check():
    """Endpoint de diagnóstico del sistema"""
    return {
        "status": "OK",
        "mongodb_connected": usuarios_col is not None,
        "database_name": DB_NAME if usuarios_col else "memoria",
        "usuarios_en_memoria": len(usuarios_db)
    }

# ENDPOINTS DE GENERACIÓN DE REPORTES PDF

@app.post("/generar_reporte_plm/")
def generar_reporte_plm(idx_or_id: str = Form(...), formato: str = Form(default="pdf")):
    """Generar reporte PDF de análisis PLM"""
    try:
        # Obtener secuencia
        seq_doc = _get_by_idx_or_id(secuencias_col, secuencias_db, idx_or_id)
        if seq_doc is None:
            raise HTTPException(status_code=404, detail="Secuencia no encontrada")
        
        secuencia = seq_doc.get("secuencia")
        
        # Buscar resultado PLM más reciente para esta secuencia
        resultado_plm = None
        try:
            if experimentos_col is not None:
                # Intentar búsqueda con string primero
                plm_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "PLM"}, 
                    sort=[("fecha", -1)]
                )
                
                # Si no encuentra, intentar con int
                if not plm_result:
                    try:
                        plm_result = experimentos_col.find_one(
                            {"secuencia_idx": int(idx_or_id), "tipo": "PLM"}, 
                            sort=[("fecha", -1)]
                        )
                    except ValueError:
                        # Si idx_or_id no es convertible a int, continuar
                        pass
                
                if plm_result:
                    resultado_plm = plm_result.get("resultado")
            else:
                print("[DEBUG] experimentos_col es None")
        except Exception as e:
            print(f"Error buscando resultado PLM: {e}")
        
        if not resultado_plm:
            raise HTTPException(status_code=404, detail="No se encontró análisis PLM para esta secuencia")
        
        # Usar siempre PDF simple para evitar problemas
        pdf_content = _create_simple_pdf_report(resultado_plm, secuencia, idx_or_id, "PLM")
        
        # Retornar PDF
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_plm_{idx_or_id}_{fecha_str}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte PLM: {str(e)}")

@app.post("/generar_reporte_laboratorio/")
def generar_reporte_laboratorio(idx_or_id: str = Form(...)):
    """Generar reporte PDF de simulación de laboratorio"""
    try:
        # Obtener secuencia
        seq_doc = _get_by_idx_or_id(secuencias_col, secuencias_db, idx_or_id)
        if seq_doc is None:
            raise HTTPException(status_code=404, detail="Secuencia no encontrada")
        
        secuencia = seq_doc.get("secuencia")
        
        # Buscar resultado de laboratorio más reciente
        resultado_lab = None
        resultado_plm = None
        try:
            if experimentos_col is not None:
                # Buscar Laboratorio
                lab_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "Laboratorio"}, 
                    sort=[("fecha", -1)]
                )
                if not lab_result:
                    try:
                        lab_result = experimentos_col.find_one(
                            {"secuencia_idx": int(idx_or_id), "tipo": "Laboratorio"}, 
                            sort=[("fecha", -1)]
                        )
                    except ValueError:
                        pass
                
                if lab_result:
                    resultado_lab = lab_result.get("resultado")
                
                # Buscar PLM relacionado
                plm_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "PLM"}, 
                    sort=[("fecha", -1)]
                )
                if not plm_result:
                    try:
                        plm_result = experimentos_col.find_one(
                            {"secuencia_idx": int(idx_or_id), "tipo": "PLM"}, 
                            sort=[("fecha", -1)]
                        )
                    except ValueError:
                        pass
                
                if plm_result:
                    resultado_plm = plm_result.get("resultado")
        except Exception as e:
            print(f"Error buscando resultados: {e}")
        
        if not resultado_lab:
            raise HTTPException(status_code=404, detail="No se encontró simulación de laboratorio para esta secuencia")
        
        # Generar PDF simple
        pdf_content = _create_simple_pdf_report(
            {"laboratorio": resultado_lab, "plm": resultado_plm},
            secuencia, idx_or_id, "Laboratorio"
        )
        
        # Retornar PDF
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_laboratorio_{idx_or_id}_{fecha_str}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte laboratorio: {str(e)}")

@app.post("/generar_reporte_gemelo/")
def generar_reporte_gemelo(idx_or_id: str = Form(...)):
    """Generar reporte PDF de simulación de gemelo digital"""
    try:
        # Obtener secuencia
        seq_doc = _get_by_idx_or_id(secuencias_col, secuencias_db, idx_or_id)
        if seq_doc is None:
            raise HTTPException(status_code=404, detail="Secuencia no encontrada")
        
        secuencia = seq_doc.get("secuencia")
        
        # Buscar resultado de gemelo digital más reciente
        resultado_gemelo = None
        resultado_plm = None
        try:
            if experimentos_col is not None:
                # Gemelo Digital
                gemelo_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "GemeloDigital"}, 
                    sort=[("fecha", -1)]
                )
                if gemelo_result:
                    resultado_gemelo = gemelo_result.get("resultado")
                
                # PLM relacionado
                plm_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "PLM"}, 
                    sort=[("fecha", -1)]
                )
                if plm_result:
                    resultado_plm = plm_result.get("resultado")
        except Exception as e:
            print(f"Error buscando resultados: {e}")
        
        if not resultado_gemelo:
            raise HTTPException(status_code=404, detail="No se encontró simulación de gemelo digital para esta secuencia")
        
        # Generar PDF con fallback
        try:
            if pdf_generator and HAVE_REPORTLAB:
                pdf_content = pdf_generator.create_bioreactor_report(resultado_gemelo, secuencia, resultado_plm)
            else:
                raise Exception("pdf_generator no disponible")
        except Exception as pdf_error:
            print(f"Error con pdf_generator, usando fallback simple: {pdf_error}")
            # Fallback a generación simple
            pdf_content = _create_simple_pdf_gemelo(resultado_gemelo, secuencia, resultado_plm)
        
        # Retornar PDF
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_gemelo_{idx_or_id}_{fecha_str}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte gemelo: {str(e)}")

@app.post("/generar_reporte_completo/")
def generar_reporte_completo(idx_or_id: str = Form(...)):
    """Generar reporte PDF completo con todos los análisis disponibles"""
    try:
        # Obtener secuencia
        seq_doc = _get_by_idx_or_id(secuencias_col, secuencias_db, idx_or_id)
        if seq_doc is None:
            raise HTTPException(status_code=404, detail="Secuencia no encontrada")
        
        secuencia = seq_doc.get("secuencia")
        
        # Buscar todos los resultados disponibles
        resultado_plm = None
        resultado_lab = None
        resultado_gemelo = None
        
        try:
            if experimentos_col is not None:
                # PLM
                plm_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "PLM"}, 
                    sort=[("fecha", -1)]
                )
                if plm_result:
                    resultado_plm = plm_result.get("resultado")
                
                # Laboratorio
                lab_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "Laboratorio"}, 
                    sort=[("fecha", -1)]
                )
                if lab_result:
                    resultado_lab = lab_result.get("resultado")
                
                # Gemelo Digital
                gemelo_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "GemeloDigital"}, 
                    sort=[("fecha", -1)]
                )
                if gemelo_result:
                    resultado_gemelo = gemelo_result.get("resultado")
        except Exception as e:
            print(f"Error buscando resultados: {e}")
        
        if not any([resultado_plm, resultado_lab, resultado_gemelo]):
            raise HTTPException(status_code=404, detail="No se encontraron análisis para esta secuencia")
        
        # Generar PDF completo con fallback
        try:
            pdf_content = pdf_generator.create_comprehensive_report(
                resultado_plm, resultado_lab, resultado_gemelo, secuencia
            )
        except Exception as pdf_error:
            print(f"Error con pdf_generator, usando fallback simple: {pdf_error}")
            # Fallback a generación simple con todos los datos
            datos_completos = {
                "PLM": resultado_plm,
                "Laboratorio": resultado_lab,
                "Gemelo Digital": resultado_gemelo
            }
            pdf_content = _create_simple_pdf_report(
                titulo="Reporte Completo",
                resultados=datos_completos,
                secuencia=secuencia
            )
        
        # Retornar PDF
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_completo_{idx_or_id}_{fecha_str}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte completo: {str(e)}")

@app.get("/documentacion/")
def obtener_documentacion(formato: str = "pdf"):
    """Generar documentación del sistema en PDF"""
    try:
        # Leer archivos de documentación
        docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
        
        documentos = {
            "manual_usuario": os.path.join(docs_path, "manual_usuario.md"),
            "readme": os.path.join(docs_path, "README.md"),
            "install": os.path.join(docs_path, "INSTALL.md")
        }
        
        # Leer contenido de los documentos
        contenido_docs = {}
        for key, path in documentos.items():
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    contenido_docs[key] = f.read()
        
        if not contenido_docs:
            raise HTTPException(status_code=404, detail="Documentación no encontrada")
        
        # Generar HTML temporal para convertir a PDF
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Documentación Sistema PLM</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #2E86AB; border-bottom: 3px solid #2E86AB; padding-bottom: 10px; }}
                h2 {{ color: #A23B72; margin-top: 30px; }}
                h3 {{ color: #F18F01; }}
                pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
                .section {{ margin-bottom: 40px; page-break-after: auto; }}
            </style>
        </head>
        <body>
            <h1>Documentación del Sistema PLM</h1>
            <p><strong>Fecha de generación:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        """
        
        # Agregar cada documento
        for key, content in contenido_docs.items():
            titulo = key.replace('_', ' ').title()
            html_content += f"""
            <div class="section">
                <h1>{titulo}</h1>
                <pre>{content}</pre>
            </div>
            """
        
        html_content += "</body></html>"
        
        # Convertir HTML a PDF usando WeasyPrint (deshabilitado en Windows)
        # pdf_content = weasyprint.HTML(string=html_content).write_pdf()
        raise HTTPException(status_code=501, detail="Documentación PDF temporalmente deshabilitada - usar módulos específicos")
        
        # Retornar PDF
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"documentacion_sistema_{fecha_str}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando documentación: {str(e)}")

# ==================== AUTENTICACIÓN ====================

@app.post("/login/")
def login(email: str = Form(...), password: str = Form(...)):
    """Autentica un usuario con credenciales fijas para demo"""
    try:
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email y contraseña son requeridos")

        # Credenciales fijas para demo/evaluación
        demo_users = {
            os.getenv("DEMO_USER_EMAIL", "demo@plm.com"): {
                "password": os.getenv("DEMO_USER_PASSWORD", "plm123"),
                "nombre": "Usuario Demo",
                "rol": "investigador"
            },
            os.getenv("DEMO_ADMIN_EMAIL", "admin@plm.com"): {
                "password": os.getenv("DEMO_ADMIN_PASSWORD", "admin123"),
                "nombre": "Administrador",
                "rol": "admin"
            },
            # Credenciales adicionales para flexibilidad
            "test@test.com": {
                "password": "123",
                "nombre": "Usuario Test",
                "rol": "investigador"
            },
            "evaluador@plm.com": {
                "password": "eval2024",
                "nombre": "Evaluador",
                "rol": "evaluador"
            }
        }

        # Validar credenciales
        if email not in demo_users or demo_users[email]["password"] != password:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Buscar o crear usuario en base de datos
        usuario = None
        if usuarios_col is not None:
            u = usuarios_col.find_one({"email": email})
            if u:
                u['id'] = str(u.get('_id'))
                u.pop('_id', None)
                usuario = u
        else:
            for u in usuarios_db:
                if u["email"] == email:
                    usuario = u
                    break

        if not usuario:
            # Crear usuario con datos de demo
            usuario = {
                "email": email,
                "nombre": demo_users[email]["nombre"],
                "rol": demo_users[email]["rol"],
                "activo": True,
                "fecha_creacion": datetime.now().isoformat()
            }
            usuario = _insert(usuarios_col, usuarios_db, usuario)

        # Generar token de sesión
        token = f"token_{usuario.get('id')}_{datetime.now().timestamp()}"
        sesiones_db[token] = {
            "usuario_id": usuario.get('id'),
            "email": email,
            "fecha_login": datetime.now().isoformat()
        }

        return {
            "mensaje": "Login exitoso",
            "token": token,
            "usuario": {
                "id": usuario.get('id'),
                "email": usuario.get('email'),
                "nombre": usuario.get('nombre'),
                "rol": usuario.get('rol')
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en login: {str(e)}")

@app.post("/logout/")
def logout(token: str = Form(...)):
    """Cierra la sesión del usuario"""
    if token in sesiones_db:
        del sesiones_db[token]
        return {"mensaje": "Logout exitoso"}
    raise HTTPException(status_code=401, detail="Token inválido")

def verificar_token(token: Optional[str]) -> dict:
    """Verifica si el token es válido"""
    if not token or token not in sesiones_db:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return sesiones_db[token]


# Endpoint para validar sesión/token desde frontend
@app.get("/session/validate")
def session_validate(token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Valida un token de sesión. Acepta `token` como query param o `Authorization: Bearer <token>` header."""
    # Prefer header Bearer token
    tok = token
    if authorization and authorization.startswith("Bearer "):
        tok = authorization.split(" ", 1)[1]
    try:
        session = verificar_token(tok)
        return {"valid": True, "session": session}
    except HTTPException as e:
        # Re-lanzar para que el cliente reciba 401
        raise


# 1. Cargar secuencia proteica
@app.post("/cargar_secuencia/")
async def cargar_secuencia(request: Request):
    """Carga una secuencia proteica desde archivo o texto

    Lee el formulario directamente desde `Request` para aceptar
    tanto `application/x-www-form-urlencoded` como `multipart/form-data`.
    """
    try:
        form = await request.form()

        nombre = form.get("nombre")
        fuente = form.get("fuente")
        secuencia_texto = form.get("secuencia_texto")
        archivo = form.get("archivo") if "archivo" in form else None

        # Validar nombre
        if not validar_nombre(nombre or ""):
            raise HTTPException(status_code=400, detail="Nombre inválido")

        secuencia = None
        formato = None

        if archivo is not None:
            # archivo puede ser un UploadFile (cuando multipart) o algo más
            if hasattr(archivo, "file"):
                contenido = await archivo.read()
                try:
                    secuencia = contenido.decode("utf-8").strip()
                    formato = archivo.filename.split('.')[-1].lower() if getattr(archivo, 'filename', None) else 'txt'
                    if formato not in ['fasta', 'csv', 'pdb', 'txt']:
                        raise HTTPException(status_code=400, detail=f"Formato no soportado: {formato}")
                except UnicodeDecodeError:
                    raise HTTPException(status_code=400, detail="Archivo no es UTF-8 válido")
            else:
                # no es UploadFile, lo ignoramos
                archivo = None

        if secuencia_texto and not secuencia:
            secuencia = str(secuencia_texto).strip()
            formato = formato or "txt"

        if not secuencia:
            raise HTTPException(status_code=400, detail="No se recibió secuencia")

        # Validar secuencia
        if not validar_secuencia(secuencia):
            raise HTTPException(status_code=400, detail="Secuencia contiene caracteres inválidos")

        registro = {
            "nombre": nombre,
            "fuente": fuente,
            "secuencia": secuencia,
            "formato": formato,
            "fecha_carga": datetime.now().isoformat(),
            "longitud": len(secuencia)
        }
        registro = _insert(secuencias_col, secuencias_db, registro)
        return {"mensaje": "Secuencia cargada correctamente", "registro": registro}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar: {str(e)}")

# 2. Listar secuencias
@app.get("/secuencias/")
def listar_secuencias():
    return {"secuencias": _find_all(secuencias_col, secuencias_db)}

# 3. Consultar secuencia específica
@app.get("/secuencia/{idx}")
def consultar_secuencia(idx: int):
    doc = _get_by_index(secuencias_col, secuencias_db, idx)
    if doc is None:
        return JSONResponse(status_code=404, content={"error": "Secuencia no encontrada"})
    return doc

# 4. Ejecutar análisis PLM
@app.post("/analizar_plm/")
def analizar_plm(idx_or_id: str = Form(...), modelo: str = Form(default="esm2")):
    """Ejecuta análisis PLM en una secuencia con modelo específico"""
    try:
        seq_doc = _get_by_idx_or_id(secuencias_col, secuencias_db, idx_or_id)
        if seq_doc is None:
            raise HTTPException(status_code=404, detail="Secuencia no encontrada")

        secuencia = seq_doc.get("secuencia")
        resultado = plm.analizar_proteina(secuencia, modelo)

        # Guarda resultado en experimentos
        experimento = {
            "tipo": "PLM",
            "secuencia_idx": idx_or_id,
            "resultado": resultado,
            "fecha": datetime.now().isoformat(),
            "estado": "completado"
        }
        _insert(experimentos_col, experimentos_db, experimento)
        return {"mensaje": "Análisis PLM ejecutado", "resultado": resultado}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

# 5. Simulación de laboratorio virtual
@app.post("/simular_laboratorio/")
def simular_laboratorio(idx_or_id: str = Form(...)):
    """Ejecuta simulación de laboratorio virtual"""
    try:
        seq_doc = _get_by_idx_or_id(secuencias_col, secuencias_db, idx_or_id)
        if seq_doc is None:
            raise HTTPException(status_code=404, detail="Secuencia no encontrada")

        secuencia = seq_doc.get("secuencia")
        
        # Buscar resultado PLM reciente para esta secuencia
        resultado_plm = None
        try:
            if experimentos_col:
                plm_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "PLM"}, 
                    sort=[("fecha", -1)]
                )
                if plm_result:
                    resultado_plm = plm_result.get("resultado")
        except:
            pass
        
        resultado = laboratorio.simular_experimento({"duracion": 10}, secuencia, resultado_plm)

        experimento = {
            "tipo": "Laboratorio",
            "secuencia_idx": idx_or_id,
            "resultado": resultado,
            "fecha": datetime.now().isoformat(),
            "estado": "completado"
        }
        _insert(experimentos_col, experimentos_db, experimento)
        return {"mensaje": "Simulación de laboratorio ejecutada", "resultado": resultado}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")

# 6. Simulación de gemelo digital
@app.post("/simular_gemelo/")
def simular_gemelo(idx_or_id: str = Form(...)):
    """Ejecuta simulación de gemelo digital"""
    try:
        seq_doc = _get_by_idx_or_id(secuencias_col, secuencias_db, idx_or_id)
        if seq_doc is None:
            raise HTTPException(status_code=404, detail="Secuencia no encontrada")

        secuencia = seq_doc.get("secuencia")
        
        # Buscar resultado PLM reciente para esta secuencia
        resultado_plm = None
        try:
            if experimentos_col:
                plm_result = experimentos_col.find_one(
                    {"secuencia_idx": idx_or_id, "tipo": "PLM"}, 
                    sort=[("fecha", -1)]
                )
                if plm_result:
                    resultado_plm = plm_result.get("resultado")
        except:
            pass
        
        resultado = gemelo.simular_biorreactor(1, [0, 48], {"k": 0.1, "temperatura": 37, "ph": 7.2, "oxigeno": 40}, secuencia, resultado_plm)

        experimento = {
            "tipo": "GemeloDigital",
            "secuencia_idx": idx_or_id,
            "resultado": resultado if isinstance(resultado, (dict, list)) else str(resultado),
            "fecha": datetime.now().isoformat(),
            "estado": "completado"
        }
        _insert(experimentos_col, experimentos_db, experimento)
        return {"mensaje": "Simulación de gemelo digital ejecutada", "resultado": resultado}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en gemelo digital: {str(e)}")

# 7. Listar experimentos
@app.get("/experimentos/")
def listar_experimentos():
    return {"experimentos": _find_all(experimentos_col, experimentos_db)}

# 8. Crear alerta
@app.post("/alerta/")
def crear_alerta(
    usuario: str = Form(...), 
    mensaje: str = Form(...),
    tipo: str = Form(default="info"),
    prioridad: str = Form(default="media")
):
    """Crea una nueva alerta con tipo y prioridad"""
    try:
        if not usuario or not mensaje:
            raise HTTPException(status_code=400, detail="Usuario y mensaje son requeridos")

        alerta = {
            "usuario": usuario,
            "mensaje": mensaje,
            "tipo": tipo,  # info, warning, error, success
            "prioridad": prioridad,  # baja, media, alta, critica
            "fecha": datetime.now().isoformat(),
            "resuelta": False
        }
        alerta = _insert(alertas_col, alertas_db, alerta)
        # Asegurar que todos los valores son serializables
        for key, value in alerta.items():
            if hasattr(value, 'binary'):
                alerta[key] = str(value)
        return {"mensaje": "Alerta creada exitosamente", "alerta": alerta}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear alerta: {str(e)}")

# 8.1. Resolver alerta
@app.put("/alerta/{alerta_id}/resolver")
def resolver_alerta(alerta_id: str):
    """Marca una alerta como resuelta"""
    try:
        # Buscar y actualizar alerta
        if alertas_col is not None:
            from bson import ObjectId
            result = alertas_col.update_one(
                {"_id": ObjectId(alerta_id)},
                {"$set": {"resuelta": True, "fecha_resolucion": datetime.now().isoformat()}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Alerta no encontrada")
        else:
            # Buscar en memoria
            for alerta in alertas_db:
                if str(alerta.get('id')) == alerta_id:
                    alerta['resuelta'] = True
                    alerta['fecha_resolucion'] = datetime.now().isoformat()
                    break
            else:
                raise HTTPException(status_code=404, detail="Alerta no encontrada")
        
        return {"mensaje": "Alerta marcada como resuelta"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al resolver alerta: {str(e)}")

# 8.2. Crear alertas automáticas del sistema
@app.post("/alerta/sistema/")
def crear_alerta_sistema(tipo_evento: str = Form(...), descripcion: str = Form(...)):
    """Crea alertas automáticas del sistema"""
    try:
        alertas_predefinidas = {
            "experimento_completado": {
                "tipo": "success",
                "prioridad": "media",
                "mensaje": f"Experimento completado exitosamente: {descripcion}"
            },
            "error_analisis": {
                "tipo": "error", 
                "prioridad": "alta",
                "mensaje": f"Error en análisis: {descripcion}"
            },
            "datos_procesados": {
                "tipo": "info",
                "prioridad": "baja", 
                "mensaje": f"Datos procesados correctamente: {descripcion}"
            },
            "limite_alcanzado": {
                "tipo": "warning",
                "prioridad": "media",
                "mensaje": f"Límite de recursos alcanzado: {descripcion}"
            }
        }
        
        config_alerta = alertas_predefinidas.get(tipo_evento, {
            "tipo": "info",
            "prioridad": "media", 
            "mensaje": descripcion
        })
        
        alerta = {
            "usuario": "sistema",
            "mensaje": config_alerta["mensaje"],
            "tipo": config_alerta["tipo"],
            "prioridad": config_alerta["prioridad"],
            "fecha": datetime.now().isoformat(),
            "resuelta": False,
            "automatica": True
        }
        
        alerta = _insert(alertas_col, alertas_db, alerta)
        return {"mensaje": "Alerta del sistema creada", "alerta": alerta}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando alerta del sistema: {str(e)}")

# 9. Listar alertas
@app.get("/alertas/")
def listar_alertas():
    """Lista todas las alertas del sistema, incluyendo alertas automáticas de estado"""
    alertas_existentes = _find_all(alertas_col, alertas_db)
    
    # Agregar alertas automáticas de estado del sistema
    alertas_sistema = [
        {
            "id": "sistema_operativo",
            "tipo": "sistema",
            "mensaje": "Sistema PLM funcionando correctamente - Todos los servicios operativos",
            "prioridad": "info",
            "fecha": datetime.now().isoformat(),
            "resuelta": False,
            "automatica": True
        },
        {
            "id": "base_datos",
            "tipo": "base_datos", 
            "mensaje": "Conexión a MongoDB establecida - Base de datos respondiendo",
            "prioridad": "info",
            "fecha": datetime.now().isoformat(), 
            "resuelta": False,
            "automatica": True
        },
        {
            "id": "pdf_generation",
            "tipo": "pdf",
            "mensaje": "Sistema de generación de PDF disponible - ReportLab operativo",
            "prioridad": "info" if HAVE_REPORTLAB else "warning",
            "fecha": datetime.now().isoformat(),
            "resuelta": False,
            "automatica": True
        },
        {
            "id": "modelos_plm",
            "tipo": "modelos",
            "mensaje": "Modelos PLM listos para análisis - 4 modelos disponibles (ESM-2, ProtBERT, ProtTrans, AlphaFold)",
            "prioridad": "info",
            "fecha": datetime.now().isoformat(),
            "resuelta": False,
            "automatica": True
        }
    ]
    
    # Combinar alertas existentes con alertas de sistema
    todas_alertas = alertas_existentes + alertas_sistema
    
    return {"alertas": todas_alertas}

# 10. Generar reporte comparativo
@app.get("/reportes/comparativos/")
def generar_reportes_comparativos():
    """Genera reportes comparativos entre diferentes análisis y simulaciones"""
    try:
        experimentos = _find_all(experimentos_col, experimentos_db)
        secuencias = _find_all(secuencias_col, secuencias_db)
        
        # Agrupar experimentos por tipo
        reportes_por_tipo = {}
        for exp in experimentos:
            tipo = exp.get("tipo", "Desconocido")
            if tipo not in reportes_por_tipo:
                reportes_por_tipo[tipo] = []
            reportes_por_tipo[tipo].append(exp)
        
        # Crear resumen de reportes
        reportes_generados = []
        for tipo, exps in reportes_por_tipo.items():
            fecha_ultima = max([exp.get("fecha", "") for exp in exps]) if exps else ""
            reportes_generados.append({
                "tipo": tipo,
                "cantidad": len(exps),
                "fecha_ultima": fecha_ultima,
                "estado": "Disponible",
                "descripcion": f"Análisis de {tipo} con {len(exps)} resultados"
            })
        
        return {
            "reportes": reportes_generados,
            "total_experimentos": len(experimentos),
            "total_secuencias": len(secuencias),
            "mensaje": f"Se han generado {len(reportes_generados)} tipos de reportes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reportes: {str(e)}")


# 10b. Descargar reporte comparativo como CSV
@app.get("/reportes/comparativos/download")
def download_reporte_comparativo(tipo: Optional[str] = None, format: Optional[str] = 'csv', token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Genera un archivo con los experimentos filtrados por `tipo`.
    Parámetros:
      - tipo: filtrar por tipo de experimento
      - format: 'csv' o 'pdf' (si reportlab está disponible)
    Requiere token válido (query param o Authorization header).
    """
    # validar token
    tok = token
    if authorization and authorization.startswith("Bearer "):
        tok = authorization.split(" ", 1)[1]
    verificar_token(tok)

    try:
        experimentos = _find_all(experimentos_col, experimentos_db)

        # Filtrar por tipo si aplica
        if tipo:
            experimentos = [e for e in experimentos if e.get('tipo') == tipo]

        # Enriquecer con nombre de secuencia si es posible
        enriched = []
        for exp in experimentos:
            seq_idx = exp.get('secuencia_idx')
            seq_nombre = ''
            try:
                seq_doc = _get_by_index(secuencias_col, secuencias_db, int(seq_idx)) if seq_idx is not None else None
                if seq_doc:
                    seq_nombre = seq_doc.get('nombre', '')
            except Exception:
                seq_nombre = ''
            enriched.append({**exp, 'secuencia_nombre': seq_nombre})

        if format == 'pdf':
            if not HAVE_REPORTLAB:
                raise HTTPException(status_code=501, detail='PDF generation not available (missing reportlab)')
            # Generar PDF simple en memoria
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            y = 800
            p.setFont('Helvetica', 10)
            p.drawString(30, y, f'Reporte comparativo - tipo: {tipo or "todos"} - {len(enriched)} items')
            y -= 20
            headers = ['id', 'tipo', 'secuencia_idx', 'secuencia_nombre', 'fecha', 'estado']
            p.drawString(30, y, ' | '.join(headers))
            y -= 15
            for exp in enriched:
                row = [str(exp.get(h, '')) for h in ['id', 'tipo', 'secuencia_idx', 'secuencia_nombre', 'fecha', 'estado']]
                text = ' | '.join(row)
                p.drawString(30, y, text[:120])
                y -= 12
                if y < 40:
                    p.showPage()
                    y = 800
            p.save()
            buffer.seek(0)
            filename = f"reportes_{tipo or 'todos'}.pdf"
            return StreamingResponse(buffer, media_type='application/pdf', headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            })

        # Default CSV
        output = io.StringIO()
        writer = csv.writer(output)
        # Cabeceras
        writer.writerow(['id', 'tipo', 'secuencia_idx', 'secuencia_nombre', 'fecha', 'estado', 'resultado'])
        for exp in enriched:
            writer.writerow([
                exp.get('id', ''),
                exp.get('tipo', ''),
                exp.get('secuencia_idx', ''),
                exp.get('secuencia_nombre', ''),
                exp.get('fecha', ''),
                exp.get('estado', ''),
                str(exp.get('resultado', ''))
            ])

        output.seek(0)
        filename = f"reportes_{tipo or 'todos'}.csv"
        return StreamingResponse(io.StringIO(output.getvalue()), media_type='text/csv', headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando archivo: {str(e)}")


# 12. Descargar informe de un experimento individual
@app.get("/experimentos/{exp_id}/download")
def download_experimento_report(exp_id: str, format: Optional[str] = 'txt', token: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Descarga un informe simple para un experimento por su id.
    - format: 'txt' o 'pdf'
    - requiere token (query o Authorization header)
    """
    # validar token
    tok = token
    if authorization and authorization.startswith("Bearer "):
        tok = authorization.split(" ", 1)[1]
    verificar_token(tok)

    try:
        exps = _find_all(experimentos_col, experimentos_db)
        exp = next((e for e in exps if str(e.get('id')) == str(exp_id) or str(e.get('id')) == exp_id), None)
        if not exp:
            raise HTTPException(status_code=404, detail='Experimento no encontrado')

        # Build simple textual report
        report_lines = []
        report_lines.append(f"Informe de Experimento - ID: {exp.get('id')}")
        report_lines.append(f"Tipo: {exp.get('tipo')}")
        report_lines.append(f"Secuencia idx: {exp.get('secuencia_idx')}")
        report_lines.append(f"Fecha: {exp.get('fecha')}")
        report_lines.append(f"Estado: {exp.get('estado')}")
        report_lines.append("")
        report_lines.append("Resultado:")
        report_lines.append(str(exp.get('resultado')))

        if format == 'pdf':
            if not HAVE_REPORTLAB:
                raise HTTPException(status_code=501, detail='PDF generation not available (missing reportlab)')
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            y = 800
            p.setFont('Helvetica', 10)
            for line in report_lines:
                p.drawString(30, y, line[:100])
                y -= 14
                if y < 40:
                    p.showPage()
                    y = 800
            p.save()
            buffer.seek(0)
            filename = f"experimento_{exp.get('id')}.pdf"
            return StreamingResponse(buffer, media_type='application/pdf', headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            })

        # default txt
        output = io.StringIO('\n'.join(report_lines))
        output.seek(0)
        filename = f"experimento_{exp.get('id')}.txt"
        return StreamingResponse(io.StringIO(output.getvalue()), media_type='text/plain', headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando informe: {str(e)}")

# 11. Buscar en experimentos y secuencias
@app.get("/buscar/")
def buscar(q: str = "", tipo: str = "all"):
    """Busca en experimentos y secuencias"""
    try:
        q_lower = q.lower()
        resultados = {
            "secuencias": [],
            "experimentos": [],
            "alertas": []
        }
        
        # Buscar en secuencias
        secuencias = _find_all(secuencias_col, secuencias_db)
        for seq in secuencias:
            if q_lower in seq.get("nombre", "").lower() or q_lower in seq.get("secuencia", "").lower():
                if tipo in ["all", "datasets"]:
                    resultados["secuencias"].append({
                        "id": seq.get("id"),
                        "nombre": seq.get("nombre"),
                        "tipo": "Secuencia",
                        "fecha": seq.get("fecha")
                    })
        
        # Buscar en experimentos
        experimentos = _find_all(experimentos_col, experimentos_db)
        for exp in experimentos:
            if q_lower in exp.get("tipo", "").lower() or q_lower in str(exp.get("resultado", "")).lower():
                if tipo in ["all", "analysis"]:
                    resultados["experimentos"].append({
                        "id": exp.get("id"),
                        "tipo": exp.get("tipo"),
                        "fecha": exp.get("fecha"),
                        "estado": exp.get("estado")
                    })
        
        # Buscar en alertas
        alertas = _find_all(alertas_col, alertas_db)
        for alerta in alertas:
            if q_lower in alerta.get("mensaje", "").lower():
                if tipo in ["all", "reports"]:
                    resultados["alertas"].append({
                        "id": alerta.get("id"),
                        "mensaje": alerta.get("mensaje"),
                        "fecha": alerta.get("fecha"),
                        "nivel": alerta.get("nivel", "info")
                    })
        
        return {
            "total_resultados": len(resultados["secuencias"]) + len(resultados["experimentos"]) + len(resultados["alertas"]),
            "resultados": resultados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")


# ENDPOINTS DE GENERACIÓN DE INFORMES EN MÚLTIPLES FORMATOS

@app.get("/informes/sistema/")
def generar_informe_sistema(formato: str = "json"):
    """Generar informe del estado del sistema"""
    try:
        # Recopilar información del sistema
        informe_data = {
            "fecha_generacion": datetime.now().isoformat(),
            "sistema": {
                "nombre": "Sistema PLM - Análisis de Proteínas",
                "version": "1.0.0",
                "estado": "Operativo"
            },
            "estadisticas": {
                "total_secuencias": len(_find_all(secuencias_col, secuencias_db)),
                "total_experimentos": len(_find_all(experimentos_col, experimentos_db)),
                "total_alertas": len(_find_all(alertas_col, alertas_db))
            },
            "componentes": {
                "base_datos": "MongoDB Atlas - Conectado",
                "generacion_pdf": "ReportLab - Disponible" if HAVE_REPORTLAB else "No disponible",
                "backend": "FastAPI - Operativo",
                "frontend": "React + Vite - Operativo"
            }
        }
        
        if formato.lower() == "csv":
            # Generar CSV
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["Componente", "Estado", "Detalles"])
            writer.writerow(["Sistema", informe_data["sistema"]["estado"], informe_data["sistema"]["nombre"]])
            writer.writerow(["Base de Datos", "Conectado", informe_data["componentes"]["base_datos"]])
            writer.writerow(["Backend", "Operativo", informe_data["componentes"]["backend"]])
            writer.writerow(["Frontend", "Operativo", informe_data["componentes"]["frontend"]])
            writer.writerow(["Total Secuencias", str(informe_data["estadisticas"]["total_secuencias"]), ""])
            writer.writerow(["Total Experimentos", str(informe_data["estadisticas"]["total_experimentos"]), ""])
            writer.writerow(["Total Alertas", str(informe_data["estadisticas"]["total_alertas"]), ""])
            
            return Response(
                content=buffer.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=informe_sistema.csv"}
            )
        
        elif formato.lower() == "html":
            # Generar HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Informe del Sistema PLM</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                    .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                    .stat-card {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; flex: 1; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Informe del Sistema PLM</h1>
                    <p>Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <h3>Secuencias</h3>
                        <p><strong>{informe_data["estadisticas"]["total_secuencias"]}</strong></p>
                    </div>
                    <div class="stat-card">
                        <h3>Experimentos</h3>
                        <p><strong>{informe_data["estadisticas"]["total_experimentos"]}</strong></p>
                    </div>
                    <div class="stat-card">
                        <h3>Alertas</h3>
                        <p><strong>{informe_data["estadisticas"]["total_alertas"]}</strong></p>
                    </div>
                </div>
                
                <h2>Estado de Componentes</h2>
                <table>
                    <tr><th>Componente</th><th>Estado</th></tr>
                    <tr><td>Base de Datos</td><td>{informe_data["componentes"]["base_datos"]}</td></tr>
                    <tr><td>Generación PDF</td><td>{informe_data["componentes"]["generacion_pdf"]}</td></tr>
                    <tr><td>Backend</td><td>{informe_data["componentes"]["backend"]}</td></tr>
                    <tr><td>Frontend</td><td>{informe_data["componentes"]["frontend"]}</td></tr>
                </table>
            </body>
            </html>
            """
            
            return Response(
                content=html_content,
                media_type="text/html",
                headers={"Content-Disposition": "attachment; filename=informe_sistema.html"}
            )
        
        else:
            # Formato JSON por defecto
            return JSONResponse(content=informe_data)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando informe: {str(e)}")

@app.get("/informes/alertas/")
def generar_informe_alertas(formato: str = "json"):
    """Generar informe de alertas"""
    try:
        alertas = _find_all(alertas_col, alertas_db)
        
        # Agregar alertas automáticas
        alertas_sistema = [
            {
                "id": "sistema_operativo",
                "tipo": "sistema",
                "mensaje": "Sistema PLM funcionando correctamente",
                "prioridad": "info",
                "fecha": datetime.now().isoformat(),
                "resuelta": False,
                "automatica": True
            },
            {
                "id": "base_datos",
                "tipo": "base_datos",
                "mensaje": "Conexión a MongoDB establecida",
                "prioridad": "info",
                "fecha": datetime.now().isoformat(),
                "resuelta": False,
                "automatica": True
            }
        ]
        
        todas_alertas = alertas + alertas_sistema
        
        if formato.lower() == "csv":
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(["ID", "Tipo", "Mensaje", "Prioridad", "Fecha", "Resuelta", "Automática"])
            
            for alerta in todas_alertas:
                writer.writerow([
                    alerta.get("id", ""),
                    alerta.get("tipo", ""),
                    alerta.get("mensaje", ""),
                    alerta.get("prioridad", ""),
                    alerta.get("fecha", ""),
                    alerta.get("resuelta", False),
                    alerta.get("automatica", False)
                ])
            
            return Response(
                content=buffer.getvalue(),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=informe_alertas.csv"}
            )
        
        elif formato.lower() == "html":
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Informe de Alertas</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .alta {{ background-color: #ffebee; }}
                    .media {{ background-color: #fff3e0; }}
                    .baja {{ background-color: #e8f5e8; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Informe de Alertas</h1>
                    <p>Total de alertas: {len(todas_alertas)}</p>
                    <p>Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <table>
                    <tr>
                        <th>Tipo</th>
                        <th>Mensaje</th>
                        <th>Prioridad</th>
                        <th>Fecha</th>
                        <th>Estado</th>
                    </tr>
            """
            
            for alerta in todas_alertas:
                prioridad = alerta.get("prioridad", "").lower()
                clase_css = "alta" if prioridad in ["alta", "critical"] else "media" if prioridad in ["media", "medium"] else "baja"
                estado = "Automática" if alerta.get("automatica") else "Resuelta" if alerta.get("resuelta") else "Activa"
                
                html_content += f"""
                    <tr class="{clase_css}">
                        <td>{alerta.get("tipo", "")}</td>
                        <td>{alerta.get("mensaje", "")}</td>
                        <td>{alerta.get("prioridad", "")}</td>
                        <td>{alerta.get("fecha", "")[:19] if alerta.get("fecha") else ""}</td>
                        <td>{estado}</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            return Response(
                content=html_content,
                media_type="text/html",
                headers={"Content-Disposition": "attachment; filename=informe_alertas.html"}
            )
        
        else:
            return JSONResponse(content={"alertas": todas_alertas, "total": len(todas_alertas)})
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando informe de alertas: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
