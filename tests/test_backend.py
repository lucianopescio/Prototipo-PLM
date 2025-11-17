# tests/test_backend.py
import pytest
import json

class TestBackendBasico:
    """Tests básicos del backend"""
    
    def test_root_endpoint(self, client):
        """Test: verifica que la API esté corriendo"""
        r = client.get("/")
        assert r.status_code == 200
        assert "message" in r.json()
    
    def test_cargar_secuencia_texto(self, client):
        """Test: carga una secuencia de texto"""
        data = {
            "nombre": "Proteína Test",
            "fuente": "Manual",
            "secuencia_texto": "MKTIIALSYIFCLVFADYKD"
        }
        r = client.post("/cargar_secuencia/", data=data)
        assert r.status_code == 200
        assert "registro" in r.json()
    
    def test_cargar_secuencia_invalida(self, client):
        """Test: rechaza secuencia con caracteres inválidos"""
        data = {
            "nombre": "Proteína Inválida",
            "fuente": "Manual",
            "secuencia_texto": "MKTIII123XYZ"
        }
        r = client.post("/cargar_secuencia/", data=data)
        assert r.status_code == 400
    
    def test_listar_secuencias(self, client):
        """Test: lista todas las secuencias cargadas"""
        r = client.get("/secuencias/")
        assert r.status_code == 200
        assert "secuencias" in r.json()
    
    def test_consultar_secuencia_no_existe(self, client):
        """Test: retorna 404 para secuencia inexistente"""
        r = client.get("/secuencia/99999")
        assert r.status_code == 404
    
    def test_listar_experimentos(self, client):
        """Test: lista todos los experimentos"""
        r = client.get("/experimentos/")
        assert r.status_code == 200
        assert "experimentos" in r.json()
    
    def test_listar_alertas(self, client):
        """Test: lista todas las alertas"""
        r = client.get("/alertas/")
        assert r.status_code == 200
        assert "alertas" in r.json()
    
    def test_crear_alerta(self, client):
        """Test: crea una nueva alerta"""
        data = {
            "usuario": "admin",
            "mensaje": "Alerta de prueba"
        }
        r = client.post("/alerta/", data=data)
        assert r.status_code == 200
        assert "alerta" in r.json()

class TestValidaciones:
    """Tests de validación de datos"""
    
    def test_nombre_vacio(self, client):
        """Test: rechaza nombre vacío"""
        data = {
            "nombre": "",
            "fuente": "Manual",
            "secuencia_texto": "MKTIIALSYIFCLVFADYKD"
        }
        r = client.post("/cargar_secuencia/", data=data)
        assert r.status_code == 400
    
    def test_secuencia_vacia(self, client):
        """Test: rechaza secuencia vacía"""
        data = {
            "nombre": "Proteína",
            "fuente": "Manual",
            "secuencia_texto": ""
        }
        r = client.post("/cargar_secuencia/", data=data)
        assert r.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__, "-v"])