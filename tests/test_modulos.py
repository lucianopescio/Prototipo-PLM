# tests/test_modulos.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from modules import plm, laboratorio, gemelo_digital

class TestModulosPLM:
    """Tests para el módulo PLM"""
    
    def test_analizar_proteina_valida(self):
        """Test: analiza una proteína válida"""
        secuencia = "MKTIIALSYIFCLVFADYKD"
        resultado = plm.analizar_proteina(secuencia)
        
        assert resultado is not None
        assert "modelo_usado" in resultado
        assert "confianza" in resultado
        assert "secuencia" in resultado
        assert resultado["secuencia"] == secuencia
    
    def test_analizar_proteina_corta(self):
        """Test: analiza una proteína muy corta"""
        secuencia = "MKT"
        resultado = plm.analizar_proteina(secuencia)
        
        assert resultado is not None
        assert len(resultado["secuencia"]) == 3

class TestModuloLaboratorio:
    """Tests para el módulo de laboratorio virtual"""
    
    def test_simular_experimento_valido(self):
        """Test: simula un experimento válido"""
        parametros = {"duracion": 10}
        resultado = laboratorio.simular_experimento(parametros)
        
        assert resultado is not None
        assert resultado["estado"] == "completado"
        assert "datos_temporales" in resultado
        assert "metricas_finales" in resultado
    
    def test_simular_experimento_duracion_cero(self):
        """Test: rechaza duración cero o negativa"""
        parametros = {"duracion": -5}
        resultado = laboratorio.simular_experimento(parametros)
        
        assert "error" in resultado or resultado["estado"] == "fallo"
    
    def test_simular_experimento_parametros_invalidos(self):
        """Test: rechaza parámetros inválidos"""
        parametros = "esto no es un diccionario"
        resultado = laboratorio.simular_experimento(parametros)
        
        assert "error" in resultado or resultado["estado"] == "fallo"

class TestModuloGemeloDigital:
    """Tests para el módulo de gemelo digital"""
    
    def test_simular_biorreactor_valido(self):
        """Test: simula un biorreactor válido"""
        resultado = gemelo_digital.simular_biorreactor(1, [0, 10], {"k": 0.1})
        
        assert resultado is not None
        assert "modelo" in resultado
        assert "datos_temporales" in resultado
        assert "metricas_finales" in resultado
    
    def test_simular_biorreactor_tiempo_invalido(self):
        """Test: rechaza tiempo inválido"""
        resultado = gemelo_digital.simular_biorreactor(1, "tiempo_invalido", {"k": 0.1})
        
        assert "error" in resultado or resultado.get("estado") == "fallo"
    
    def test_simular_biorreactor_sin_parametro_k(self):
        """Test: rechaza parámetros sin 'k'"""
        resultado = gemelo_digital.simular_biorreactor(1, [0, 10], {"otra_clave": 0.5})
        
        assert "error" in resultado or resultado.get("estado") == "fallo"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
