# database/models.py
from datetime import datetime
from typing import Optional, List

class Proteina:
    """Modelo de Proteína"""
    def __init__(self, nombre: str, secuencia: str, categoria: str, fuente: str = "Manual"):
        self.nombre = nombre
        self.secuencia = secuencia
        self.categoria = categoria
        self.fuente = fuente
        self.fecha_creacion = datetime.now().isoformat()
        self.longitud = len(secuencia)
    
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "secuencia": self.secuencia,
            "categoria": self.categoria,
            "fuente": self.fuente,
            "fecha_creacion": self.fecha_creacion,
            "longitud": self.longitud
        }

class Usuario:
    """Modelo de Usuario"""
    def __init__(self, nombre: str, rol: str, email: str = None, activo: bool = True):
        self.nombre = nombre
        self.rol = rol
        self.email = email
        self.activo = activo
        self.fecha_creacion = datetime.now().isoformat()
        
        # Validar rol
        roles_validos = ['admin', 'investigador', 'operador']
        if rol not in roles_validos:
            raise ValueError(f"Rol debe ser uno de: {roles_validos}")
    
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "rol": self.rol,
            "email": self.email,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion
        }

class Experimento:
    """Modelo de Experimento"""
    def __init__(self, usuario_id: str, proteina_id: str, protocolo: str, 
                 resultados: Optional[dict] = None, tipo: str = "general"):
        self.usuario_id = usuario_id
        self.proteina_id = proteina_id
        self.protocolo = protocolo
        self.resultados = resultados or {}
        self.tipo = tipo
        self.fecha = datetime.now().isoformat()
        self.estado = "en_progreso"
    
    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "proteina_id": self.proteina_id,
            "protocolo": self.protocolo,
            "resultados": self.resultados,
            "tipo": self.tipo,
            "fecha": self.fecha,
            "estado": self.estado
        }
    
    def completar(self, resultados: dict):
        """Marca el experimento como completado"""
        self.estado = "completado"
        self.resultados = resultados

class Alerta:
    """Modelo de Alerta"""
    def __init__(self, usuario_id: str, tipo_alerta: str, mensaje: str, severidad: str = "normal"):
        self.usuario_id = usuario_id
        self.tipo_alerta = tipo_alerta
        self.mensaje = mensaje
        self.severidad = severidad
        self.fecha = datetime.now().isoformat()
        self.resuelta = False
        
        # Validar severidad
        severidades_validas = ['baja', 'normal', 'alta', 'crítica']
        if severidad not in severidades_validas:
            raise ValueError(f"Severidad debe ser una de: {severidades_validas}")
    
    def to_dict(self):
        return {
            "usuario_id": self.usuario_id,
            "tipo_alerta": self.tipo_alerta,
            "mensaje": self.mensaje,
            "severidad": self.severidad,
            "fecha": self.fecha,
            "resuelta": self.resuelta
        }
    
    def resolver(self):
        """Marca la alerta como resuelta"""
        self.resuelta = True