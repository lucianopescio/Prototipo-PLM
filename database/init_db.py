# database/init_db.py
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from database.config import DB_URI, DB_NAME

def init_db():
    """
    Inicializa la conexión con MongoDB
    
    Returns:
        Base de datos MongoDB o None si falla
    """
    try:
        client = MongoClient(DB_URI, serverSelectionTimeoutMS=5000)
        # Verificar conexión
        client.admin.command('ping')
        
        db = client[DB_NAME]
        print(f"✅ Conectado a MongoDB: {DB_NAME}")
        return db
        
    except ServerSelectionTimeoutError:
        print("❌ No se pudo conectar a MongoDB. Asegúrate de que MongoDB está corriendo o que MONGO_URI es correcto.")
        print(f"   MONGO_URI: {DB_URI[:80]}...")
        return None
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {str(e)}")
        return None

def get_collections(db):
    """Obtiene todas las colecciones de la base de datos"""
    if db is None:
        return []
    return db.list_collection_names()

def create_indexes(db):
    """Crea índices en las colecciones principales"""
    if db is None:
        return
    
    try:
        # Índices para secuencias
        db.secuencias.create_index("nombre", unique=False)
        db.secuencias.create_index("fecha_carga")
        
        # Índices para experimentos
        db.experimentos.create_index("secuencia_idx")
        db.experimentos.create_index("fecha")
        
        # Índices para alertas
        db.alertas.create_index("usuario")
        db.alertas.create_index("fecha")
        
        print("✅ Índices creados correctamente")
    except Exception as e:
        print(f"⚠️ Error creando índices: {str(e)}")