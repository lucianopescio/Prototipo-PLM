"""
Generador de reportes PDF para el sistema PLM
Incluye reportes de análisis PLM, laboratorio virtual y gemelo digital
"""

import os
import io
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from jinja2 import Template
# Disable WeasyPrint to avoid Windows library issues
HAVE_WEASYPRINT = False
weasyprint = None

# Configurar estilo de matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class PDFReportGenerator:
    """Generador de reportes PDF para análisis PLM y simulaciones"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Configurar estilos personalizados para los reportes"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#A23B72')
        ))
        
        # Texto de métricas
        self.styles.add(ParagraphStyle(
            name='MetricStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=20
        ))

    def create_plm_report(self, resultado_plm: Dict[Any, Any], secuencia: str, 
                         experimento_id: str = None) -> bytes:
        """
        Generar reporte PDF de análisis PLM
        
        Args:
            resultado_plm: Resultado del análisis PLM
            secuencia: Secuencia de proteína analizada
            experimento_id: ID del experimento (opcional)
            
        Returns:
            bytes: Contenido del PDF
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Contenido del reporte
        story = []
        
        # Título
        story.append(Paragraph("Reporte de Análisis PLM", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Información general
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_data = [
            ['Fecha de Análisis:', fecha],
            ['Modelo PLM Usado:', resultado_plm.get('modelo_usado', 'N/A')],
            ['Confianza:', f"{resultado_plm.get('confianza', 0) * 100:.1f}%"],
            ['ID Experimento:', experimento_id or 'N/A'],
            ['Longitud Secuencia:', str(len(secuencia)) + ' aminoácidos']
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4FD')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Secuencia analizada
        story.append(Paragraph("Secuencia Analizada", self.styles['CustomSubtitle']))
        secuencia_truncada = secuencia[:100] + "..." if len(secuencia) > 100 else secuencia
        story.append(Paragraph(f"<font name='Courier'>{secuencia_truncada}</font>", 
                              self.styles['Normal']))
        story.append(Spacer(1, 15))
        
        # Resultados específicos por modelo
        self._add_model_specific_results(story, resultado_plm)
        
        # Generar gráfico de confianza
        if 'confianza' in resultado_plm:
            chart_buffer = self._create_confidence_chart(resultado_plm)
            if chart_buffer:
                story.append(PageBreak())
                story.append(Paragraph("Análisis de Confianza", self.styles['CustomSubtitle']))
                story.append(Image(chart_buffer, width=5*inch, height=3*inch))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def create_laboratory_report(self, resultado_lab: Dict[Any, Any], secuencia: str = None,
                               resultado_plm: Dict[Any, Any] = None) -> bytes:
        """
        Generar reporte PDF de simulación de laboratorio virtual
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Título
        story.append(Paragraph("Reporte de Laboratorio Virtual", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Información de la simulación
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        motor = resultado_lab.get('motor_simulacion', 'N/A')
        duracion = resultado_lab.get('duracion_simulacion', 'N/A')
        
        sim_data = [
            ['Fecha de Simulación:', fecha],
            ['Motor de Simulación:', motor],
            ['Duración:', f"{duracion} unidades de tiempo"],
            ['Tipo:', resultado_lab.get('tipo', 'N/A')],
            ['Estado:', resultado_lab.get('estado', 'N/A')]
        ]
        
        sim_table = Table(sim_data, colWidths=[2*inch, 3*inch])
        sim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(sim_table)
        story.append(Spacer(1, 20))
        
        # Parámetros PLM si están disponibles
        if 'parametros_plm' in resultado_lab:
            story.append(Paragraph("Integración PLM", self.styles['CustomSubtitle']))
            plm_params = resultado_lab['parametros_plm']
            
            plm_data = [
                ['Modelo PLM:', plm_params.get('modelo_plm', 'N/A')],
                ['Confianza PLM:', str(plm_params.get('confianza_plm', 'N/A'))],
                ['Kcat Derivado:', str(plm_params.get('kcat_derivado', 'N/A'))],
                ['Km Derivado:', str(plm_params.get('km_derivado', 'N/A'))]
            ]
            
            plm_table = Table(plm_data, colWidths=[2*inch, 3*inch])
            plm_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFF8DC')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(plm_table)
            story.append(Spacer(1, 20))
        
        # Métricas finales
        if 'metricas_finales' in resultado_lab:
            story.append(Paragraph("Métricas Finales", self.styles['CustomSubtitle']))
            metricas = resultado_lab['metricas_finales']
            
            metricas_data = []
            for key, value in metricas.items():
                metricas_data.append([key.replace('_', ' ').title() + ':', str(value)])
            
            metricas_table = Table(metricas_data, colWidths=[2.5*inch, 2.5*inch])
            metricas_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4FD')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metricas_table)
            story.append(Spacer(1, 20))
        
        # Gráfico de datos temporales
        if 'datos_temporales' in resultado_lab and resultado_lab['datos_temporales']:
            chart_buffer = self._create_temporal_chart(resultado_lab['datos_temporales'], 'Laboratorio')
            if chart_buffer:
                story.append(PageBreak())
                story.append(Paragraph("Evolución Temporal", self.styles['CustomSubtitle']))
                story.append(Image(chart_buffer, width=6*inch, height=4*inch))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def create_bioreactor_report(self, resultado_gemelo: Dict[Any, Any], secuencia: str = None,
                               resultado_plm: Dict[Any, Any] = None) -> bytes:
        """
        Generar reporte PDF de simulación de gemelo digital (biorreactor)
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Título
        story.append(Paragraph("Reporte de Gemelo Digital - Biorreactor", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Información del biorreactor
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipo = resultado_gemelo.get('tipo', 'N/A')
        estado = resultado_gemelo.get('estado', 'N/A')
        tiempo_sim = resultado_gemelo.get('tiempo_simulacion', 'N/A')
        
        bio_data = [
            ['Fecha de Simulación:', fecha],
            ['Tipo de Simulación:', tipo],
            ['Estado:', estado],
            ['Tiempo de Simulación:', f"{tiempo_sim} horas"],
            ['Motor:', resultado_gemelo.get('motor_simulacion', 'Modelo Logístico')]
        ]
        
        bio_table = Table(bio_data, colWidths=[2*inch, 3*inch])
        bio_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFE8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(bio_table)
        story.append(Spacer(1, 20))
        
        # Integración PLM si disponible
        if 'integracion_plm' in resultado_gemelo:
            story.append(Paragraph("Integración PLM", self.styles['CustomSubtitle']))
            plm_info = resultado_gemelo['integracion_plm']
            
            plm_data = [
                ['Modelo PLM Usado:', plm_info.get('modelo_usado', 'N/A')],
                ['Confianza:', str(plm_info.get('confianza', 'N/A'))],
                ['Eficiencia Derivada:', str(plm_info.get('eficiencia_derivada', 'N/A'))],
                ['Factor de Mejora:', str(plm_info.get('parametros_ajustados', {}).get('factor_mejora', 'N/A'))]
            ]
            
            plm_table = Table(plm_data, colWidths=[2*inch, 3*inch])
            plm_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFF0E6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(plm_table)
            story.append(Spacer(1, 20))
        
        # Parámetros del modelo
        if 'parametros_modelo' in resultado_gemelo:
            story.append(Paragraph("Parámetros del Modelo", self.styles['CustomSubtitle']))
            params = resultado_gemelo['parametros_modelo']
            
            params_data = []
            for key, value in params.items():
                params_data.append([key.replace('_', ' ').title() + ':', str(value)])
            
            params_table = Table(params_data, colWidths=[2.5*inch, 2.5*inch])
            params_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(params_table)
            story.append(Spacer(1, 20))
        
        # Métricas finales
        if 'metricas_finales' in resultado_gemelo:
            story.append(Paragraph("Métricas Finales", self.styles['CustomSubtitle']))
            metricas = resultado_gemelo['metricas_finales']
            
            metricas_data = []
            for key, value in metricas.items():
                metricas_data.append([key.replace('_', ' ').title() + ':', str(value)])
            
            metricas_table = Table(metricas_data, colWidths=[2.5*inch, 2.5*inch])
            metricas_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F8E8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metricas_table)
            story.append(Spacer(1, 20))
        
        # Interpretación PLM
        if 'interpretacion_plm' in resultado_gemelo:
            story.append(Paragraph("Interpretación PLM", self.styles['CustomSubtitle']))
            interpretacion = resultado_gemelo['interpretacion_plm']
            story.append(Paragraph(interpretacion, self.styles['Normal']))
            story.append(Spacer(1, 15))
        
        # Gráfico de datos temporales
        if 'datos_temporales' in resultado_gemelo and resultado_gemelo['datos_temporales']:
            chart_buffer = self._create_temporal_chart(resultado_gemelo['datos_temporales'], 'Biorreactor')
            if chart_buffer:
                story.append(PageBreak())
                story.append(Paragraph("Evolución del Biorreactor", self.styles['CustomSubtitle']))
                story.append(Image(chart_buffer, width=6*inch, height=4*inch))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_model_specific_results(self, story: List, resultado_plm: Dict[Any, Any]):
        """Agregar resultados específicos según el modelo PLM usado"""
        modelo = resultado_plm.get('modelo_usado', '')
        
        if modelo == 'ESM-2' and 'estructura_secundaria' in resultado_plm:
            story.append(Paragraph("Estructura Secundaria (ESM-2)", self.styles['CustomSubtitle']))
            estructura = resultado_plm['estructura_secundaria']
            
            est_data = [
                ['Hélices Alfa:', estructura.get('helices_alfa', 'N/A')],
                ['Láminas Beta:', estructura.get('laminas_beta', 'N/A')],
                ['Bucles:', estructura.get('bucles', 'N/A')],
                ['Regiones Desordenadas:', estructura.get('regiones_desordenadas', 'N/A')]
            ]
            
        elif modelo == 'ProtBERT' and 'similitud_funcional' in resultado_plm:
            story.append(Paragraph("Similitud Funcional (ProtBERT)", self.styles['CustomSubtitle']))
            similitud = resultado_plm['similitud_funcional']
            
            est_data = [
                ['Función Predicha:', similitud.get('funcion_predicha', 'N/A')],
                ['Categoría GO:', similitud.get('categoria_go', 'N/A')]
            ]
            
            # Agregar proteínas conocidas
            if 'proteinas_conocidas' in similitud:
                story.append(Paragraph("Proteínas Similares:", self.styles['Normal']))
                for i, prot in enumerate(similitud['proteinas_conocidas'][:3], 1):
                    story.append(Paragraph(f"{i}. {prot.get('nombre', 'N/A')} - Similitud: {prot.get('similitud', 'N/A')}", 
                                         self.styles['MetricStyle']))
                story.append(Spacer(1, 10))
                return
            
        elif modelo == 'ProtTrans' and 'propiedades_biofisicas' in resultado_plm:
            story.append(Paragraph("Propiedades Biofísicas (ProtTrans)", self.styles['CustomSubtitle']))
            props = resultado_plm['propiedades_biofisicas']
            
            est_data = [
                ['Peso Molecular:', str(props.get('peso_molecular', 'N/A'))],
                ['Punto Isoeléctrico:', str(props.get('punto_isoelectrico', 'N/A'))],
                ['Carga Neta:', str(props.get('carga_neta', 'N/A'))],
                ['Hidrofobicidad:', str(props.get('hidrofobicidad', 'N/A'))]
            ]
            
        elif modelo == 'AlphaFold' and 'estructura_3d' in resultado_plm:
            story.append(Paragraph("Estructura 3D (AlphaFold)", self.styles['CustomSubtitle']))
            estructura_3d = resultado_plm['estructura_3d']
            
            est_data = [
                ['Confianza Plegamiento:', estructura_3d.get('confianza_plegamiento', 'N/A')],
                ['Dominios Funcionales:', str(estructura_3d.get('dominios_funcionales', 'N/A'))],
                ['Sitios Activos:', str(estructura_3d.get('sitios_activos', 'N/A'))],
                ['Cavidades:', str(estructura_3d.get('cavidades', 'N/A'))]
            ]
        else:
            return
        
        # Crear tabla con los datos específicos
        if 'est_data' in locals():
            est_table = Table(est_data, colWidths=[2*inch, 3*inch])
            est_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5DC')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(est_table)
            story.append(Spacer(1, 20))

    def _create_confidence_chart(self, resultado_plm: Dict[Any, Any]) -> Optional[io.BytesIO]:
        """Crear gráfico de barras de confianza del modelo PLM"""
        try:
            fig, ax = plt.subplots(figsize=(8, 5))
            
            modelo = resultado_plm.get('modelo_usado', 'N/A')
            confianza = resultado_plm.get('confianza', 0) * 100
            
            # Datos para el gráfico
            categorias = ['Confianza del Modelo', 'Precisión Esperada', 'Fiabilidad']
            valores = [confianza, confianza * 0.9, confianza * 0.85]
            colores = ['#2E86AB', '#A23B72', '#F18F01']
            
            bars = ax.bar(categorias, valores, color=colores, alpha=0.8)
            
            # Personalizar gráfico
            ax.set_title(f'Análisis de Confianza - {modelo}', fontsize=14, fontweight='bold')
            ax.set_ylabel('Porcentaje (%)', fontsize=12)
            ax.set_ylim(0, 100)
            
            # Agregar valores en las barras
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{valor:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Guardar en buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='PNG', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error creando gráfico de confianza: {e}")
            return None

    def _create_temporal_chart(self, datos_temporales: List[Dict], tipo: str) -> Optional[io.BytesIO]:
        """Crear gráfico de evolución temporal"""
        try:
            if not datos_temporales:
                return None
                
            df = pd.DataFrame(datos_temporales)
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle(f'Evolución Temporal - {tipo}', fontsize=16, fontweight='bold')
            
            # Gráfico 1: Actividad/Biomasa
            if 'actividad' in df.columns:
                axes[0, 0].plot(df['tiempo'], df['actividad'], marker='o', color='#2E86AB', linewidth=2)
                axes[0, 0].set_title('Actividad Enzimática')
                axes[0, 0].set_ylabel('Actividad (%)')
                axes[0, 0].grid(True, alpha=0.3)
            elif 'biomasa' in df.columns:
                axes[0, 0].plot(df['tiempo'], df['biomasa'], marker='o', color='#2E86AB', linewidth=2)
                axes[0, 0].set_title('Crecimiento de Biomasa')
                axes[0, 0].set_ylabel('Biomasa (g/L)')
                axes[0, 0].grid(True, alpha=0.3)
            
            # Gráfico 2: Estabilidad/Viabilidad
            if 'estabilidad' in df.columns:
                axes[0, 1].plot(df['tiempo'], df['estabilidad'], marker='s', color='#A23B72', linewidth=2)
                axes[0, 1].set_title('Estabilidad Enzimática')
                axes[0, 1].set_ylabel('Estabilidad (%)')
                axes[0, 1].grid(True, alpha=0.3)
            elif 'viabilidad' in df.columns:
                axes[0, 1].plot(df['tiempo'], df['viabilidad'], marker='s', color='#A23B72', linewidth=2)
                axes[0, 1].set_title('Viabilidad Celular')
                axes[0, 1].set_ylabel('Viabilidad (%)')
                axes[0, 1].grid(True, alpha=0.3)
            
            # Gráfico 3: Producto/Productividad
            if 'producto' in df.columns:
                axes[1, 0].plot(df['tiempo'], df['producto'], marker='^', color='#F18F01', linewidth=2)
                axes[1, 0].set_title('Producción')
                axes[1, 0].set_ylabel('Producto (mM)')
                axes[1, 0].set_xlabel('Tiempo')
                axes[1, 0].grid(True, alpha=0.3)
            elif 'productividad' in df.columns:
                axes[1, 0].plot(df['tiempo'], df['productividad'], marker='^', color='#F18F01', linewidth=2)
                axes[1, 0].set_title('Productividad')
                axes[1, 0].set_ylabel('Productividad (g/L/h)')
                axes[1, 0].set_xlabel('Tiempo')
                axes[1, 0].grid(True, alpha=0.3)
            
            # Gráfico 4: Sustrato/pH
            if 'sustrato' in df.columns:
                axes[1, 1].plot(df['tiempo'], df['sustrato'], marker='d', color='#C73E1D', linewidth=2)
                axes[1, 1].set_title('Consumo de Sustrato')
                axes[1, 1].set_ylabel('Sustrato (mM)')
                axes[1, 1].set_xlabel('Tiempo')
                axes[1, 1].grid(True, alpha=0.3)
            elif 'ph' in df.columns:
                axes[1, 1].plot(df['tiempo'], df['ph'], marker='d', color='#C73E1D', linewidth=2)
                axes[1, 1].set_title('pH del Medio')
                axes[1, 1].set_ylabel('pH')
                axes[1, 1].set_xlabel('Tiempo')
                axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Guardar en buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='PNG', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            print(f"Error creando gráfico temporal: {e}")
            return None

    def create_comprehensive_report(self, resultado_plm: Dict[Any, Any] = None,
                                  resultado_lab: Dict[Any, Any] = None, 
                                  resultado_gemelo: Dict[Any, Any] = None,
                                  secuencia: str = None) -> bytes:
        """
        Crear reporte comprehensivo que incluye todos los análisis disponibles
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Título principal
        story.append(Paragraph("Reporte Integral PLM - Análisis Completo", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información general
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        story.append(Paragraph(f"Fecha de Generación: {fecha}", self.styles['Normal']))
        story.append(Spacer(1, 10))
        
        if secuencia:
            story.append(Paragraph(f"Secuencia Analizada: {len(secuencia)} aminoácidos", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Índice de contenidos
        story.append(Paragraph("Contenido del Reporte", self.styles['CustomSubtitle']))
        contenido = []
        if resultado_plm:
            contenido.append("• Análisis PLM")
        if resultado_lab:
            contenido.append("• Simulación de Laboratorio Virtual")
        if resultado_gemelo:
            contenido.append("• Simulación de Gemelo Digital")
        
        for item in contenido:
            story.append(Paragraph(item, self.styles['Normal']))
        
        story.append(PageBreak())
        
        # Incluir cada sección si está disponible
        if resultado_plm:
            story.append(Paragraph("1. ANÁLISIS PLM", self.styles['CustomTitle']))
            # Agregar contenido resumido del PLM
            story.append(Paragraph(f"Modelo: {resultado_plm.get('modelo_usado', 'N/A')}", self.styles['Normal']))
            story.append(Paragraph(f"Confianza: {resultado_plm.get('confianza', 0) * 100:.1f}%", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        if resultado_lab:
            story.append(Paragraph("2. LABORATORIO VIRTUAL", self.styles['CustomTitle']))
            # Agregar contenido resumido del laboratorio
            motor = resultado_lab.get('motor_simulacion', 'N/A')
            story.append(Paragraph(f"Motor de Simulación: {motor}", self.styles['Normal']))
            if 'metricas_finales' in resultado_lab:
                story.append(Paragraph("Métricas destacadas:", self.styles['Normal']))
                metricas = resultado_lab['metricas_finales']
                for key, value in list(metricas.items())[:3]:
                    story.append(Paragraph(f"  • {key.replace('_', ' ').title()}: {value}", self.styles['MetricStyle']))
            story.append(Spacer(1, 20))
        
        if resultado_gemelo:
            story.append(Paragraph("3. GEMELO DIGITAL", self.styles['CustomTitle']))
            # Agregar contenido resumido del gemelo digital
            tipo = resultado_gemelo.get('tipo', 'N/A')
            story.append(Paragraph(f"Tipo: {tipo}", self.styles['Normal']))
            if 'metricas_finales' in resultado_gemelo:
                story.append(Paragraph("Métricas destacadas:", self.styles['Normal']))
                metricas = resultado_gemelo['metricas_finales']
                for key, value in list(metricas.items())[:3]:
                    story.append(Paragraph(f"  • {key.replace('_', ' ').title()}: {value}", self.styles['MetricStyle']))
            story.append(Spacer(1, 20))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


# Instancia global del generador
pdf_generator = PDFReportGenerator()