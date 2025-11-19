# database/seed_data.py
"""
Script para inicializar datos de ejemplo en el sistema PLM
Estas secuencias y experimentos aparecerán en el dashboard, laboratorio virtual y gemelo digital
"""

from datetime import datetime
import json

def get_sample_sequences():
    """Retorna secuencias de proteínas de ejemplo para demostración"""
    return [
        {
            "id": 0,
            "nombre": "Proteína P53 (Tumor Suppressor)",
            "secuencia": "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD",
            "descripcion": "Proteína supresora de tumores P53 - crítica para control del ciclo celular",
            "organismo": "Homo sapiens",
            "fecha_carga": "2024-01-15T10:30:00Z",
            "longitud": 393,
            "peso_molecular": 43653.0,
            "punto_isoelectrico": 6.33,
            "tags": ["tumor_suppressor", "dna_binding", "transcription_factor"],
            "estructura_predicha": {
                "helices_alfa": "32%",
                "laminas_beta": "8%",
                "bucles": "60%"
            },
            "analisis_plm": {
                "modelo_usado": "ESM-2",
                "confianza": 0.94,
                "funcionalidad_predicha": "DNA binding, transcriptional regulation",  
                "estabilidad": "Alta",
                "dominios": ["DNA-binding domain", "Tetramerization domain"]
            }
        },
        {
            "id": 1,
            "nombre": "Insulina Humana",
            "secuencia": "MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN",
            "descripcion": "Hormona reguladora de glucosa en sangre",
            "organismo": "Homo sapiens", 
            "fecha_carga": "2024-01-15T11:15:00Z",
            "longitud": 110,
            "peso_molecular": 11500.0,
            "punto_isoelectrico": 5.4,
            "tags": ["hormone", "diabetes", "glucose_regulation"],
            "estructura_predicha": {
                "helices_alfa": "45%",
                "laminas_beta": "15%", 
                "bucles": "40%"
            },
            "analisis_plm": {
                "modelo_usado": "ProtBERT",
                "confianza": 0.96,
                "funcionalidad_predicha": "Hormone activity, glucose homeostasis",
                "estabilidad": "Media",
                "dominios": ["A chain", "B chain", "C-peptide"]
            }
        },
        {
            "id": 2,
            "nombre": "Hemoglobina Beta Chain", 
            "secuencia": "MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYH",
            "descripcion": "Cadena beta de hemoglobina - transporte de oxígeno",
            "organismo": "Homo sapiens",
            "fecha_carga": "2024-01-16T09:20:00Z", 
            "longitud": 147,
            "peso_molecular": 15867.0,
            "punto_isoelectrico": 6.8,
            "tags": ["oxygen_transport", "blood", "anemia"],
            "estructura_predicha": {
                "helices_alfa": "78%",
                "laminas_beta": "2%",
                "bucles": "20%"
            },
            "analisis_plm": {
                "modelo_usado": "ESM-2",
                "confianza": 0.98,
                "funcionalidad_predicha": "Oxygen binding and transport",
                "estabilidad": "Alta", 
                "dominios": ["Globin domain", "Heme binding site"]
            }
        },
        {
            "id": 3,
            "nombre": "Green Fluorescent Protein (GFP)",
            "secuencia": "MSKGEELFTGVVPILVELDGDVNGHKFSVSGEGEGDATYGKLTLKFICTTGKLPVPWPTLVTTFSYGVQCFSRYPDHMKQHDFFKSAMPEGYVQERTIFFKDDGNYKTRAEVKFEGDTLVNRIELKGIDFKEDGNILGHKLEYNYNSHNVYIMADKQKNGIKVNFKIRHNIEDGSVQLADHYQQNTPIGDGPVLLPDNHYLSTQSALSKDPNEKRDHMVLLEFVTAAGITHGMDELYK",
            "descripcion": "Proteína fluorescente verde - marcador biológico",
            "organismo": "Aequorea victoria",
            "fecha_carga": "2024-01-16T14:45:00Z",
            "longitud": 238,
            "peso_molecular": 26900.0,
            "punto_isoelectrico": 5.9,
            "tags": ["fluorescent", "marker", "imaging"],
            "estructura_predicha": {
                "helices_alfa": "15%",
                "laminas_beta": "65%",
                "bucles": "20%"
            },
            "analisis_plm": {
                "modelo_usado": "ProtTrans",
                "confianza": 0.91,
                "funcionalidad_predicha": "Fluorescence emission, protein folding reporter",
                "estabilidad": "Alta",
                "dominios": ["Beta barrel", "Chromophore"]
            }
        }
    ]

def get_sample_experiments():
    """Retorna experimentos de ejemplo para mostrar en el dashboard"""
    return [
        {
            "id": 0,
            "nombre": "Estabilidad térmica P53",
            "secuencia_idx": 0,
            "tipo": "laboratorio_virtual",
            "parametros": {
                "temperatura": 65.0,
                "ph": 7.4,
                "tiempo": 120,
                "concentracion": 0.5
            },
            "resultados": {
                "viabilidad": 87.3,
                "actividad_enzimatica": 92.1,
                "estabilidad": "Alta",
                "tiempo_vida_media": 145.8
            },
            "fecha": "2024-01-15T12:00:00Z",
            "estado": "completado"
        },
        {
            "id": 1,
            "nombre": "Simulación biorreactor - Insulina",
            "secuencia_idx": 1,
            "tipo": "gemelo_digital",
            "parametros": {
                "temperatura": 37.0,
                "ph": 7.2,
                "oxigeno": 40.0,
                "tiempo_simulacion": 48
            },
            "resultados": {
                "rendimiento": 94.2,
                "pureza": 98.7,
                "concentracion_final": 2.3,
                "eficiencia_proceso": 91.5
            },
            "fecha": "2024-01-16T08:30:00Z",
            "estado": "completado"
        },
        {
            "id": 2,
            "nombre": "Análisis plegamiento - Hemoglobina",
            "secuencia_idx": 2,
            "tipo": "plm_execution",
            "parametros": {
                "modelo": "ESM-2",
                "temperatura": 25.0,
                "fuerza_ionica": 0.15
            },
            "resultados": {
                "confianza_estructura": 0.98,
                "energia_libre": -127.3,
                "rmsd": 0.8,
                "score_calidad": 95.2
            },
            "fecha": "2024-01-16T15:20:00Z",
            "estado": "completado"
        }
    ]

def initialize_demo_data(secuencias_db, experimentos_db):
    """
    Inicializa datos de demostración en las listas en memoria
    Llama esta función al inicio del backend para tener datos de ejemplo
    """
    # Limpiar datos existentes
    secuencias_db.clear()
    experimentos_db.clear()
    
    # Agregar secuencias de ejemplo
    sample_sequences = get_sample_sequences()
    secuencias_db.extend(sample_sequences)
    
    # Agregar experimentos de ejemplo
    sample_experiments = get_sample_experiments()
    experimentos_db.extend(sample_experiments)
    
    print(f"✅ Datos de demostración inicializados:")
    print(f"   - {len(sample_sequences)} secuencias de ejemplo")
    print(f"   - {len(sample_experiments)} experimentos de ejemplo")
    
    return len(sample_sequences), len(sample_experiments)

def seed_mongodb_data(db):
    """
    Inicializa datos de ejemplo en MongoDB si está disponible
    """
    if db is None:
        return False
        
    try:
        # Insertar secuencias de ejemplo
        sequences = get_sample_sequences()
        if db.secuencias.count_documents({}) == 0:
            db.secuencias.insert_many(sequences)
            print(f"✅ {len(sequences)} secuencias insertadas en MongoDB")
        
        # Insertar experimentos de ejemplo  
        experiments = get_sample_experiments()
        if db.experimentos.count_documents({}) == 0:
            db.experimentos.insert_many(experiments)
            print(f"✅ {len(experiments)} experimentos insertados en MongoDB")
            
        return True
        
    except Exception as e:
        print(f"⚠️ Error inicializando datos en MongoDB: {e}")
        return False