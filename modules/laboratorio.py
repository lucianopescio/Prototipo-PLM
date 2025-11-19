# modules/laboratorio.py

try:
    import simpy
except Exception:
    simpy = None


def _simulate_with_simpy(duracion, parametros):
    """Run a minimal SimPy simulation that waits `duracion` time units.

    The simulation is intentionally simple: it models a single process that
    takes `duracion` and then produces deterministic results. This keeps the
    external API stable while leveraging SimPy for timing/extension later.
    """
    env = simpy.Environment()
    results = {}

    def process(env):
        yield env.timeout(duracion)
        results.update({
            "muestras_procesadas": int(duracion * 5),
            "tasa_exito": 0.95,
            "tiempo_proceso": duracion,
            "observaciones": "SimPy: Simulación completada exitosamente"
        })

    env.process(process(env))
    env.run()
    return results


def _simular_con_simpy_avanzado(duracion, parametros, secuencia, resultado_plm):
    """
    Simulación avanzada con SimPy - modelo de eventos discretos
    """
    import random
    import math
    
    env = simpy.Environment()
    
    # Contenedores para datos de simulación
    datos_temporales = []
    eventos_sistema = []
    
    # Parámetros derivados de PLM
    if resultado_plm:
        confianza = resultado_plm.get('confianza', 0.90)
        modelo_usado = resultado_plm.get('modelo_usado', 'Generic')
        
        # Parámetros adaptativos según modelo PLM
        if modelo_usado == 'ESM-2':
            kcat = 100 * confianza  # Constante catalítica
            km = 0.5 / confianza   # Constante de Michaelis
            degradacion_rate = 0.01 * (2 - confianza)
        elif modelo_usado == 'ProtTrans':
            props = resultado_plm.get('propiedades_biofisicas', {})
            kcat = 80 + float(props.get('peso_molecular', 50000)) / 1000
            km = abs(float(props.get('carga_neta', 0))) * 0.1 + 0.3
            degradacion_rate = 0.005
        else:
            kcat = 75 * confianza
            km = 0.4
            degradacion_rate = 0.008
    else:
        kcat = 50
        km = 0.5
        degradacion_rate = 0.01
    
    # Recursos del sistema
    enzima = simpy.Container(env, capacity=1000, init=100)  # Concentración inicial
    sustrato = simpy.Container(env, capacity=10000, init=1000)
    producto = simpy.Container(env, capacity=10000, init=0)
    
    def reaccion_enzimatica(env, enzima, sustrato, producto):
        """Proceso de reacción enzimática con cinética de Michaelis-Menten"""
        while True:
            try:
                # Esperar un pequeño intervalo de tiempo
                yield env.timeout(0.1)
                
                current_time = env.now
                
                # Obtener niveles actuales
                E = enzima.level
                S = sustrato.level
                
                if S > 0 and E > 0:
                    # Cinética de Michaelis-Menten
                    v = (kcat * E * S) / (km + S)
                    delta_s = min(v * 0.1, S)  # No consumir más sustrato del disponible
                    
                    # Consumir sustrato y producir producto
                    if delta_s > 0:
                        yield sustrato.get(delta_s)
                        yield producto.put(delta_s)
                        eventos_sistema.append(f"t={current_time:.1f}: Reacción v={v:.2f}")
                
                # Registrar datos cada 0.5 unidades de tiempo
                if current_time % 0.5 < 0.1:
                    actividad = (v / kcat) * 100 if 'v' in locals() else 0
                    estabilidad = E / 100 * 100 * math.exp(-degradacion_rate * current_time)
                    
                    datos_temporales.append({
                        "tiempo": round(current_time, 1),
                        "actividad": round(max(0, actividad), 1),
                        "estabilidad": round(max(0, estabilidad), 1),
                        "producto": round(producto.level, 1),
                        "sustrato": round(sustrato.level, 1),
                        "enzima_activa": round(E, 1)
                    })
                    
            except simpy.Interrupt:
                eventos_sistema.append(f"t={env.now:.1f}: Proceso interrumpido")
                break
    
    def degradacion_enzimatica(env, enzima):
        """Proceso de degradación enzimática"""
        while True:
            yield env.timeout(1.0)  # Cada unidad de tiempo
            current_enzyme = enzima.level
            degradacion = current_enzyme * degradacion_rate
            if degradacion > 0:
                yield enzima.get(min(degradacion, current_enzyme))
                eventos_sistema.append(f"t={env.now:.1f}: Degradación enzimática -{degradacion:.2f}")
    
    # Iniciar procesos
    env.process(reaccion_enzimatica(env, enzima, sustrato, producto))
    env.process(degradacion_enzimatica(env, enzima))
    
    # Ejecutar simulación
    env.run(until=duracion)
    
    # Calcular métricas finales
    if datos_temporales:
        actividad_maxima = max(p["actividad"] for p in datos_temporales)
        producto_final = datos_temporales[-1]["producto"]
        estabilidad_final = datos_temporales[-1]["estabilidad"]
        eficiencia = (producto_final / 1000) * (actividad_maxima / 100) * 100
    else:
        actividad_maxima = 0
        producto_final = 0
        estabilidad_final = 0
        eficiencia = 0
    
    return {
        "tipo": "laboratorio_virtual_simpy",
        "estado": "completado",
        "duracion_simulacion": duracion,
        "motor_simulacion": "SimPy 4.0.1 - Eventos Discretos",
        "parametros_plm": {
            "modelo_plm": resultado_plm.get('modelo_usado', 'N/A') if resultado_plm else 'N/A',
            "confianza_plm": resultado_plm.get('confianza', 'N/A') if resultado_plm else 'N/A',
            "kcat_derivado": round(kcat, 2),
            "km_derivado": round(km, 3)
        },
        "secuencia_analizada": secuencia[:50] + "..." if secuencia and len(secuencia) > 50 else secuencia,
        "datos_temporales": datos_temporales,
        "eventos_sistema": eventos_sistema[-10:],  # Últimos 10 eventos
        "metricas_finales": {
            "actividad_maxima": round(actividad_maxima, 1),
            "estabilidad_final": round(estabilidad_final, 1),
            "rendimiento_producto": round(producto_final, 1),
            "eficiencia_cataltica": round(eficiencia, 1),
            "sustrato_consumido": round(1000 - (datos_temporales[-1]["sustrato"] if datos_temporales else 1000), 1)
        },
        "condiciones_experimentales": {
            "temperatura": parametros.get("temperatura", 37),
            "ph": parametros.get("ph", 7.4),
            "concentracion_sustrato_inicial": 1000,
            "concentracion_enzima_inicial": 100
        }
    }


def simular_experimento(parametros, secuencia=None, resultado_plm=None):
    """
    Simulación de laboratorio virtual avanzada con SimPy y integración PLM

    Args:
        parametros: Dict con parámetros de simulación (duracion, condiciones, etc)
        secuencia: Secuencia de proteína para ajustar simulación
        resultado_plm: Resultados del análisis PLM para parametrización precisa

    Returns:
        Dict con resultados de la simulación y datos de gráficos
    """
    import random
    import math
    
    try:
        if not isinstance(parametros, dict):
            raise ValueError("Parámetros debe ser un diccionario")

        duracion = parametros.get("duracion", 10)
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise ValueError("Duración debe ser un número positivo")

        # Usar SimPy si está disponible para simulación avanzada
        if simpy is not None:
            return _simular_con_simpy_avanzado(duracion, parametros, secuencia, resultado_plm)
        
        # Propiedades adaptativas basadas en PLM
        seq_factor = 1.0
        estabilidad_base = 0.85
        precision_plm = 0.90
        
        if resultado_plm:
            # Integrar resultados PLM para parámetros precisos
            confianza = resultado_plm.get('confianza', 0.90)
            precision_plm = confianza
            
            if 'estructura_secundaria' in resultado_plm:
                # ESM-2 results
                helices = float(resultado_plm['estructura_secundaria'].get('helices_alfa', '30%').replace('%', '')) / 100
                seq_factor = 0.7 + helices * 0.6  # Más hélices = mayor estabilidad
                
            elif 'propiedades_biofisicas' in resultado_plm:
                # ProtTrans results
                hidrofobicidad = resultado_plm['propiedades_biofisicas'].get('hidrofobicidad', 0)
                seq_factor = 0.8 + max(0, hidrofobicidad) * 0.1
                
            elif 'estructura_3d' in resultado_plm:
                # AlphaFold results
                confianza_3d = float(resultado_plm['estructura_3d'].get('confianza_plegamiento', '80%').replace('%', '')) / 100
                seq_factor = 0.6 + confianza_3d * 0.5
                
        elif secuencia:
            # Fallback: propiedades básicas de secuencia
            hidrofobicos = sum(1 for aa in secuencia if aa in 'AILMFWYV')
            polares = sum(1 for aa in secuencia if aa in 'STNQ')
            cargados = sum(1 for aa in secuencia if aa in 'KRHDE')
            
            seq_factor = 0.8 + (hidrofobicos / len(secuencia)) * 0.4
            estabilidad_base = 0.7 + (polares / len(secuencia)) * 0.3
            
        # Generar serie temporal de datos experimentales
        puntos_tiempo = []
        tiempo_total = int(duracion * 6)  # 6 puntos por unidad de tiempo
        
        for i in range(tiempo_total + 1):
            t = i * (duracion / tiempo_total)
            
            # Actividad enzimática (curva sigmoidal)
            actividad_max = 100 * seq_factor
            actividad = actividad_max / (1 + math.exp(-0.5 * (t - duracion/2)))
            actividad += random.uniform(-5, 5)  # ruido
            
            # Estabilidad (decaimiento exponencial)
            estabilidad = estabilidad_base * math.exp(-t * 0.02) * 100
            estabilidad += random.uniform(-3, 3)
            
            # Concentración de producto (crecimiento logístico)
            producto_max = 80 * seq_factor
            producto = producto_max / (1 + math.exp(-0.3 * (t - duracion/3)))
            producto += random.uniform(-4, 4)
            
            puntos_tiempo.append({
                "tiempo": round(t, 1),
                "actividad": max(0, round(actividad, 1)),
                "estabilidad": max(0, min(100, round(estabilidad, 1))),
                "producto": max(0, round(producto, 1))
            })

        # Métricas finales
        actividad_final = puntos_tiempo[-1]["actividad"]
        estabilidad_final = puntos_tiempo[-1]["estabilidad"]
        producto_final = puntos_tiempo[-1]["producto"]
        
        resultado = {
            "tipo": "laboratorio_virtual",
            "estado": "completado",
            "duracion_simulacion": duracion,
            "parametros_entrada": parametros,
            "secuencia_analizada": secuencia[:50] + "..." if secuencia and len(secuencia) > 50 else secuencia,
            "datos_temporales": puntos_tiempo,
            "metricas_finales": {
                "actividad_maxima": round(max(p["actividad"] for p in puntos_tiempo), 1),
                "estabilidad_final": round(estabilidad_final, 1),
                "rendimiento_producto": round(producto_final, 1),
                "eficiencia_cataltica": round(actividad_final / 100 * estabilidad_final / 100 * 100, 1)
            },
            "condiciones_experimentales": {
                "temperatura": parametros.get("temperatura", 37),
                "ph": parametros.get("ph", 7.4),
                "concentracion_sustrato": parametros.get("sustrato", 1.0)
            }
        }
        return resultado

    except Exception as e:
        return {"error": str(e), "estado": "fallo"}