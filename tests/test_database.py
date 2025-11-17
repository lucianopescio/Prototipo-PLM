# tests/test_database.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Proteina, Usuario, Experimento, Alerta

class TestModeloProteina:
    """Tests para el modelo Proteína"""
    
    def test_crear_proteina(self):
        """Test: crea una proteína correctamente"""
        proteina = Proteina("P53", "MKTIIALSYIFCLVFADYKD", "tumor_suppressor")
        
        assert proteina.nombre == "P53"
        assert proteina.longitud == 20
        assert proteina.to_dict()["categoria"] == "tumor_suppressor"
    
    def test_proteina_a_dict(self):
        """Test: convierte proteína a diccionario"""
        proteina = Proteina("Test", "MKTIII", "test")
        diccionario = proteina.to_dict()
        
        assert "nombre" in diccionario
        assert "secuencia" in diccionario
        assert "fecha_creacion" in diccionario

class TestModeloUsuario:
    """Tests para el modelo Usuario"""
    
    def test_crear_usuario_valido(self):
        """Test: crea un usuario con rol válido"""
        usuario = Usuario("Juan", "investigador", "juan@example.com")
        
        assert usuario.nombre == "Juan"
        assert usuario.rol == "investigador"
        assert usuario.activo == True
    
    def test_crear_usuario_rol_invalido(self):
        """Test: rechaza rol inválido"""
        try:
            usuario = Usuario("Juan", "super_admin", "juan@example.com")
            assert False, "Debería haber lanzado excepción"
        except ValueError as e:
            assert "Rol debe ser uno de" in str(e)

class TestModeloExperimento:
    """Tests para el modelo Experimento"""
    
    def test_crear_experimento(self):
        """Test: crea un experimento correctamente"""
        experimento = Experimento("usuario1", "proteina1", "protocolo_test")
        
        assert experimento.usuario_id == "usuario1"
        assert experimento.estado == "en_progreso"
    
    def test_completar_experimento(self):
        """Test: marca experimento como completado"""
        experimento = Experimento("usuario1", "proteina1", "protocolo_test")
        resultados = {"precision": 0.95}
        
        experimento.completar(resultados)
        
        assert experimento.estado == "completado"
        assert experimento.resultados["precision"] == 0.95

class TestModeloAlerta:
    """Tests para el modelo Alerta"""
    
    def test_crear_alerta(self):
        """Test: crea una alerta correctamente"""
        alerta = Alerta("usuario1", "error", "Error en simulación")
        
        assert alerta.usuario_id == "usuario1"
        assert alerta.resuelta == False
    
    def test_crear_alerta_severidad_invalida(self):
        """Test: rechaza severidad inválida"""
        try:
            alerta = Alerta("usuario1", "error", "Mensaje", "extrema")
            assert False, "Debería haber lanzado excepción"
        except ValueError as e:
            assert "Severidad debe ser una de" in str(e)
    
    def test_resolver_alerta(self):
        """Test: marca alerta como resuelta"""
        alerta = Alerta("usuario1", "warning", "Advertencia")
        alerta.resolver()
        
        assert alerta.resuelta == True
