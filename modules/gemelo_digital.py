# modules/gemelo_digital.py
import json

def simular_biorreactor(y0, t, params, secuencia=None, resultado_plm=None):
    """
    Simulación de gemelo digital de biorreactor con integración PLM
    
    Args:
        y0: Condición inicial
        t: Tiempo [t_inicio, t_fin]
        params: Parámetros del modelo (dict con clave 'k')
        secuencia: Secuencia de proteína para ajustar parámetros
        resultado_plm: Resultados del análisis PLM para parametrización
    
    Returns:
        Dict con resultados de simulación y datos temporales
    """
    import random
    import math
    
    try:
        if not isinstance(params, dict) or 'k' not in params:
            raise ValueError("Parámetros inválidos: se requiere dict con clave 'k'")
        
        if not isinstance(t, (list, tuple)) or len(t) != 2:
            raise ValueError("Tiempo debe ser [t_inicio, t_fin]")
        
        k = params.get('k', 0.1)
        temperatura = params.get('temperatura', 37)
        ph = params.get('ph', 7.2)
        oxigeno = params.get('oxigeno', 40)
        
        # Ajustar parámetros basados en PLM y secuencia
        k_ajustado = k
        viabilidad_base = 95
        capacidad_carga = 1000
        eficiencia_plm = 1.0
        
        if resultado_plm:
            # Usar resultados PLM para parametrización precisa
            confianza = resultado_plm.get('confianza', 0.90)
            modelo_usado = resultado_plm.get('modelo_usado', 'Generic')
            
            if modelo_usado == 'ESM-2' and 'estructura_secundaria' in resultado_plm:
                # Estructura secundaria influye en estabilidad y crecimiento
                helices = float(resultado_plm['estructura_secundaria'].get('helices_alfa', '30%').replace('%', '')) / 100
                laminas = float(resultado_plm['estructura_secundaria'].get('laminas_beta', '25%').replace('%', '')) / 100
                
                # Más estructura = mayor estabilidad y eficiencia
                factor_estructura = (helices + laminas) * 1.5
                k_ajustado = k * (0.7 + factor_estructura * confianza)
                viabilidad_base = 90 + (factor_estructura * confianza * 8)
                eficiencia_plm = 0.8 + factor_estructura * 0.4
                
            elif modelo_usado == 'ProtBERT' and 'similitud_funcional' in resultado_plm:
                # Similitud funcional determina eficiencia biológica
                prot_conocidas = resultado_plm['similitud_funcional'].get('proteinas_conocidas', [])
                if prot_conocidas:
                    max_similitud = max([p.get('similitud', 0) for p in prot_conocidas], default=0.5)
                    k_ajustado = k * (0.6 + max_similitud * 0.8 * confianza)
                    viabilidad_base = 85 + (max_similitud * confianza * 12)
                    eficiencia_plm = 0.7 + max_similitud * 0.5
                    
            elif modelo_usado == 'ProtTrans' and 'propiedades_biofisicas' in resultado_plm:
                # Propiedades bioquímicas afectan condiciones de cultivo
                props = resultado_plm['propiedades_biofisicas']
                peso_mol = float(str(props.get('peso_molecular', 50000)).replace(' Da', ''))
                punto_iso = float(props.get('punto_isoelectrico', 7.0))
                
                # Proteínas más grandes y estables crecen mejor
                factor_peso = min(1.8, peso_mol / 40000)  # Factor basado en peso
                factor_ph = 1.0 - abs(punto_iso - 7.2) * 0.03  # Cerca de pH óptimo
                
                k_ajustado = k * factor_peso * factor_ph * confianza
                viabilidad_base = 88 + (factor_peso * factor_ph * confianza * 10)
                eficiencia_plm = factor_peso * factor_ph * 0.9
                
            elif modelo_usado == 'AlphaFold' and 'estructura_3d' in resultado_plm:
                # Estructura 3D y plegamiento afectan viabilidad
                confianza_3d = float(resultado_plm['estructura_3d'].get('confianza_plegamiento', '80%').replace('%', '')) / 100
                dominios = resultado_plm['estructura_3d'].get('dominios_funcionales', 2)
                
                # Mejor plegamiento = mayor viabilidad
                k_ajustado = k * (0.5 + confianza_3d * confianza * 0.8)
                viabilidad_base = 82 + (confianza_3d * confianza * 15)
                eficiencia_plm = 0.6 + confianza_3d * 0.6
        
        elif secuencia:
            # Fallback: usar propiedades básicas de secuencia
            aromáticos = sum(1 for aa in secuencia if aa in 'FYW')
            básicos = sum(1 for aa in secuencia if aa in 'KRH')
            
            k_ajustado = k * (1 + aromáticos / len(secuencia) * 0.3)
            viabilidad_base = 98 - (básicos / len(secuencia) * 10)
        
        # Generar datos temporales (48 horas, punto cada 2 horas)
        datos_temporales = []
        tiempo_total = 48
        pasos = 24
        
        for i in range(pasos + 1):
            tiempo_actual = i * (tiempo_total / pasos)
            
            # Crecimiento de biomasa (logístico con limitación de nutrientes)
            biomasa_max = 20 * (1 + k_ajustado)
            biomasa = biomasa_max / (1 + math.exp(-k_ajustado * (tiempo_actual - 24)))
            biomasa = max(y0, biomasa + random.uniform(-0.5, 0.5))
            
            # Producción de proteína (sigmoidal)
            prod_max = 15 * k_ajustado
            producto = prod_max / (1 + math.exp(-0.15 * (tiempo_actual - 20)))
            producto = max(0, producto + random.uniform(-0.3, 0.3))
            
            # Viabilidad celular (decaimiento lento)
            viabilidad = viabilidad_base * math.exp(-tiempo_actual * 0.003)
            viabilidad = max(80, viabilidad + random.uniform(-2, 2))
            
            # Oxígeno disuelto (consumo dinámico)
            ox_consumo = biomasa * 0.5
            oxigeno_actual = max(10, oxigeno - ox_consumo + random.uniform(-3, 3))
            
            datos_temporales.append({
                "time": tiempo_actual,
                "biomasa": round(biomasa, 2),
                "producto": round(producto, 2),
                "viabilidad": round(viabilidad, 1),
                "oxigeno": round(oxigeno_actual, 1),
                "ph": round(ph + random.uniform(-0.2, 0.2), 2),
                "temperatura": round(temperatura + random.uniform(-1, 1), 1)
            })
        
        # Métricas finales
        ultimo_punto = datos_temporales[-1]
        
        resultado = {
            "modelo": "biorreactor_dinamico",
            "condiciones_iniciales": {
                "biomasa_inicial": y0,
                "temperatura": temperatura,
                "ph": ph,
                "oxigeno_inicial": oxigeno
            },
            "parametros": params,
            "secuencia_objetivo": secuencia[:50] + "..." if secuencia and len(secuencia) > 50 else secuencia,
            "datos_temporales": datos_temporales,
            "metricas_finales": {
                "biomasa_maxima": round(max(p["biomasa"] for p in datos_temporales), 2),
                "produccion_total": round(ultimo_punto["producto"], 2),
                "viabilidad_final": round(ultimo_punto["viabilidad"], 1),
                "eficiencia_proceso": round((ultimo_punto["producto"] / ultimo_punto["biomasa"]) * 100, 1)
            },
            "alertas": [
                f"Viabilidad: {'Óptima' if ultimo_punto['viabilidad'] > 90 else 'Revisar'}" ,
                f"Producción: {'Alta' if ultimo_punto['producto'] > 10 else 'Baja'}",
                f"pH: {'Estable' if abs(ultimo_punto['ph'] - ph) < 0.5 else 'Desviado'}"
            ]
        }
        # Agregar información PLM al resultado
        if resultado_plm:
            resultado["integracion_plm"] = {
                "modelo_usado": resultado_plm.get('modelo_usado', 'N/A'),
                "confianza": resultado_plm.get('confianza', 'N/A'),
                "eficiencia_derivada": round(eficiencia_plm, 3),
                "parametros_ajustados": {
                    "k_original": round(k, 4),
                    "k_ajustado": round(k_ajustado, 4),
                    "factor_mejora": round(k_ajustado / k, 2)
                }
            }
            
            # Interpretación específica por modelo PLM
            if resultado_plm.get('modelo_usado') == 'ESM-2':
                resultado["interpretacion_plm"] = "Estructura secundaria optimizada para estabilidad en biorreactor"
            elif resultado_plm.get('modelo_usado') == 'ProtBERT':
                resultado["interpretacion_plm"] = "Similitud funcional asegura actividad biológica sostenida"  
            elif resultado_plm.get('modelo_usado') == 'ProtTrans':
                resultado["interpretacion_plm"] = "Propiedades biofísicas adaptadas a condiciones de cultivo"
            elif resultado_plm.get('modelo_usado') == 'AlphaFold':
                resultado["interpretacion_plm"] = "Estructura 3D predice comportamiento en ambiente controlado"
        
        return resultado
        
    except Exception as e:
        return {"error": str(e), "estado": "fallo"}