# tests/test_laboratorio.py
from modules.laboratorio import simular_experimento


def test_simular_experimento():
    # Llamamos con parámetros válidos y comprobamos la estructura devuelta
    resultado = simular_experimento({"duracion": 1})
    assert resultado is not None
    assert resultado.get("estado") == "completado"
    assert "datos_temporales" in resultado
    assert "metricas_finales" in resultado