import { Download, FileText, FileDown, Printer } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Separator } from './ui/separator';

interface ReportDownloaderProps {
  sequenceId: string;
  hasPlm?: boolean;
  hasLaboratory?: boolean;
  hasDigitalTwin?: boolean;
}

export default function ReportDownloader({ 
  sequenceId, 
  hasPlm = false, 
  hasLaboratory = false, 
  hasDigitalTwin = false 
}: ReportDownloaderProps) {
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const downloadReport = async (endpoint: string, filename: string, type: string) => {
    setDownloading(type);
    setError(null);
    
    try {
      console.log(`Iniciando descarga de ${type} para secuencia ${sequenceId}`);
      console.log(`URL: ${API_URL}${endpoint}`);
      
      const formData = new FormData();
      formData.append('idx_or_id', sequenceId);
      
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      console.log(`Respuesta: ${response.status} ${response.statusText}`);
      console.log(`Content-Type: ${response.headers.get('content-type')}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      // Verificar que es un PDF
      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/pdf')) {
        console.warn(`Tipo de contenido inesperado: ${contentType}`);
      }

      // Crear blob y descargar
      const blob = await response.blob();
      console.log(`Blob creado: ${blob.size} bytes`);
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log(`Descarga completada: ${filename}`);
    } catch (err) {
      console.error('Error downloading report:', err);
      setError(`Error descargando reporte ${type}: ${err instanceof Error ? err.message : 'Error desconocido'}`);
    } finally {
      setDownloading(null);
    }
  };

  const downloadDocumentation = async () => {
    setDownloading('documentation');
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/documentacion/?formato=pdf`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `documentacion_sistema_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading documentation:', err);
      setError(`Error descargando documentación: ${err instanceof Error ? err.message : 'Error desconocido'}`);
    } finally {
      setDownloading(null);
    }
  };

  const reports = [
    {
      id: 'plm',
      title: 'Reporte PLM',
      description: 'Análisis detallado de Protein Language Models',
      endpoint: '/generar_reporte_plm/',
      available: hasPlm,
      icon: <FileText className="h-4 w-4" />,
      color: 'bg-blue-50 border-blue-200 text-blue-800'
    },
    {
      id: 'laboratory',
      title: 'Reporte Laboratorio Virtual',
      description: 'Simulación y análisis de experimentos in silico',
      endpoint: '/generar_reporte_laboratorio/',
      available: hasLaboratory,
      icon: <FileDown className="h-4 w-4" />,
      color: 'bg-green-50 border-green-200 text-green-800'
    },
    {
      id: 'digital-twin',
      title: 'Reporte Gemelo Digital',
      description: 'Simulación de biorreactor y análisis temporal',
      endpoint: '/generar_reporte_gemelo/',
      available: hasDigitalTwin,
      icon: <Printer className="h-4 w-4" />,
      color: 'bg-purple-50 border-purple-200 text-purple-800'
    },
    {
      id: 'comprehensive',
      title: 'Reporte Completo',
      description: 'Todos los análisis disponibles en un documento',
      endpoint: '/generar_reporte_completo/',
      available: hasPlm || hasLaboratory || hasDigitalTwin,
      icon: <Download className="h-4 w-4" />,
      color: 'bg-orange-50 border-orange-200 text-orange-800'
    }
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Generación de Reportes
          </CardTitle>
          <CardDescription>
            Descarga reportes detallados en formato PDF de los análisis realizados
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="grid gap-4 md:grid-cols-2">
            {reports.map((report) => (
              <Card key={report.id} className={`${report.available ? 'opacity-100' : 'opacity-50'}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      {report.icon}
                      {report.title}
                    </CardTitle>
                    <Badge 
                      variant={report.available ? "default" : "secondary"}
                      className={report.available ? report.color : ''}
                    >
                      {report.available ? "Disponible" : "No disponible"}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs">
                    {report.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <Button
                    onClick={() => downloadReport(
                      report.endpoint,
                      `${report.id}_${sequenceId}_${new Date().toISOString().slice(0, 10)}.pdf`,
                      report.title
                    )}
                    disabled={!report.available || downloading === report.title}
                    className="w-full"
                    size="sm"
                  >
                    {downloading === report.title ? (
                      <>
                        <div className="animate-spin h-4 w-4 mr-2 border-2 border-current border-t-transparent rounded-full" />
                        Generando...
                      </>
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-2" />
                        Descargar PDF
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <Separator className="my-6" />
          
          {/* Documentación del Sistema */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Documentación del Sistema
              </CardTitle>
              <CardDescription className="text-xs">
                Manual de usuario, guías de instalación y documentación técnica
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
              <Button
                onClick={downloadDocumentation}
                disabled={downloading === 'documentation'}
                className="w-full"
                variant="outline"
                size="sm"
              >
                {downloading === 'documentation' ? (
                  <>
                    <div className="animate-spin h-4 w-4 mr-2 border-2 border-current border-t-transparent rounded-full" />
                    Generando...
                  </>
                ) : (
                  <>
                    <FileDown className="h-4 w-4 mr-2" />
                    Descargar Documentación
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
      
      {/* Información adicional */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Información de Reportes</CardTitle>
        </CardHeader>
        <CardContent className="text-xs space-y-2">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-blue-50 text-blue-700">PLM</Badge>
            <span>Incluye análisis de estructura, función y propiedades predichas</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-green-50 text-green-700">Lab Virtual</Badge>
            <span>Contiene simulaciones SimPy con cinética enzimática y métricas temporales</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-purple-50 text-purple-700">Gemelo Digital</Badge>
            <span>Simulación de biorreactor con parámetros integrados de PLM</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-orange-50 text-orange-700">Completo</Badge>
            <span>Reporte integral con todos los análisis disponibles y gráficos</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}