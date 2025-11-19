import { Download, FileText, FileDown, Database } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner';

interface InformeDownloaderProps {
  className?: string;
}

export function InformeDownloader({ className }: InformeDownloaderProps) {
  const [downloading, setDownloading] = useState<string | null>(null);
  const [formato, setFormato] = useState<string>('json');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const downloadInforme = async (tipo: string, nombreArchivo: string) => {
    setDownloading(tipo);
    
    try {
      const response = await fetch(`${API_URL}/informes/${tipo}/?formato=${formato}`);
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${nombreArchivo}.${formato}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success(`Informe ${tipo} descargado exitosamente`);
    } catch (error) {
      console.error('Error downloading report:', error);
      toast.error(`Error descargando informe: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setDownloading(null);
    }
  };

  const informes = [
    {
      id: 'sistema',
      title: 'Informe del Sistema',
      description: 'Estado general y estadísticas del sistema PLM',
      icon: <Database className="h-5 w-5" />,
      color: 'bg-blue-50 border-blue-200'
    },
    {
      id: 'alertas',
      title: 'Informe de Alertas',
      description: 'Todas las alertas activas y resueltas del sistema',
      icon: <FileText className="h-5 w-5" />,
      color: 'bg-orange-50 border-orange-200'
    }
  ];

  const formatos = [
    { value: 'json', label: 'JSON', icon: '{}' },
    { value: 'csv', label: 'CSV', icon: '📊' },
    { value: 'html', label: 'HTML', icon: '🌐' }
  ];

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Download className="h-5 w-5" />
          Generación de Informes
        </CardTitle>
        <CardDescription>
          Descarga informes del sistema en diferentes formatos
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Selector de formato */}
        <div>
          <label className="text-sm font-medium mb-2 block">Formato de salida</label>
          <Select value={formato} onValueChange={setFormato}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {formatos.map((fmt) => (
                <SelectItem key={fmt.value} value={fmt.value}>
                  <span className="flex items-center gap-2">
                    <span>{fmt.icon}</span>
                    {fmt.label}
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Lista de informes */}
        <div className="space-y-3">
          {informes.map((informe) => (
            <div
              key={informe.id}
              className={`p-4 rounded-lg border-2 ${informe.color}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-white">
                    {informe.icon}
                  </div>
                  <div>
                    <h3 className="font-medium text-sm">{informe.title}</h3>
                    <p className="text-xs text-gray-600 mt-1">
                      {informe.description}
                    </p>
                  </div>
                </div>
                <Button
                  onClick={() => downloadInforme(informe.id, `informe_${informe.id}_${new Date().toISOString().slice(0, 10)}`)}
                  disabled={downloading === informe.id}
                  size="sm"
                  className="flex items-center gap-2"
                >
                  {downloading === informe.id ? (
                    <>
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                      Descargando...
                    </>
                  ) : (
                    <>
                      <FileDown className="h-3 w-3" />
                      Descargar
                    </>
                  )}
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Información adicional */}
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-600">
            Los informes incluyen datos actualizados al momento de la descarga. 
            Formatos disponibles: JSON (datos estructurados), CSV (hoja de cálculo), HTML (visualización web).
          </p>
        </div>
      </CardContent>
    </Card>
  );
}