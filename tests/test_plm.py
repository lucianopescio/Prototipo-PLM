# tests/test_plm.py
from modules.plm import analizar_proteina

def test_analizar_proteina():
    resultado = analizar_proteina("MVLSPADKTNVKAA")
    assert "modelo_usado" in resultado
    assert "confianza" in resultado
    assert "secuencia" in resultado
    assert resultado["secuencia"] == "MVLSPADKTNVKAA"