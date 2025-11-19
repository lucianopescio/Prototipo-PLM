import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Search, Filter, Download, FileText, BarChart3 } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import axios from 'axios';
import { toast } from 'sonner';

interface QueryInterfaceProps {
  token: string | null;
}

export function QueryInterface({ token }: QueryInterfaceProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [recentReports, setRecentReports] = useState<any[]>([]);
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isLoadingReports, setIsLoadingReports] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    cargarReportes();
  }, [token]);

  const cargarReportes = async () => {
    setIsLoadingReports(true);
    try {
      const headers: any = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const response = await axios.get(`${API_URL}/reportes/comparativos/`, { headers });
      if (response.data.reportes) {
        setRecentReports(response.data.reportes);
      }
    } catch (error) {
      console.error('Error cargando reportes:', error);
      toast.error('Error al cargar reportes');
    } finally {
      setIsLoadingReports(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Por favor ingresa un término de búsqueda');
      return;
    }

    setIsSearching(true);
    try {
      const response = await axios.get(`${API_URL}/buscar/`, {
        params: {
          q: searchQuery,
          tipo: filterType
        }
      });
      setSearchResults(response.data);
      if (response.data.total_resultados === 0) {
        toast.info('No se encontraron resultados');
      } else {
        toast.success(`Se encontraron ${response.data.total_resultados} resultados`);
      }
    } catch (error) {
      console.error('Error en búsqueda:', error);
      toast.error('Error al buscar');
    } finally {
      setIsSearching(false);
    }
  };

  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);

  const handleDownloadReport = async (report: any, format: string = 'csv') => {
    try {
      setIsDownloading(true);
      setDownloadProgress(0);
      toast.info(`Preparando descarga: ${report.tipo}`);
      const url = `${API_URL}/reportes/comparativos/download` + (report.tipo ? `?tipo=${encodeURIComponent(report.tipo)}` : '') + `&format=${encodeURIComponent(format)}`;
      const headers: any = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const resp = await axios.get(url, {
        responseType: 'blob',
        headers,
        onDownloadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setDownloadProgress(percent);
          }
        }
      });

      const blob = new Blob([resp.data], { type: resp.headers['content-type'] || 'text/csv' });
      const filename = resp.headers['content-disposition']?.split('filename=')[1]?.replace(/"/g, '') || `report_${report.tipo || 'all'}.${format}`;
      // Crear enlace y forzar descarga
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(link.href);
      toast.success(`Descarga iniciada: ${filename}`);
    } catch (error) {
      console.error('Error descargando reporte:', error);
      const message = (error as any).response?.data?.detail || 'Error descargando el reporte';
      toast.error(message);
    } finally {
      setIsDownloading(false);
      setDownloadProgress(0);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Interfaz de Consulta</h1>
        <p className="text-gray-600">Búsqueda de resultados, reportes y comparaciones (HU-010, HU-011)</p>
      </div>

      {/* Search Bar */}
      <Card>
        <CardHeader>
          <CardTitle>Búsqueda Avanzada</CardTitle>
          <CardDescription>Busca y filtra información del sistema</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input 
                placeholder="Buscar por nombre de proteína, análisis, dataset..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-10"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[180px]">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="analysis">Análisis</SelectItem>
                <SelectItem value="datasets">Datasets</SelectItem>
                <SelectItem value="reports">Reportes</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={handleSearch} disabled={isSearching}>
              <Search className="mr-2 h-4 w-4" />
              {isSearching ? 'Buscando...' : 'Buscar'}
            </Button>
          </div>

          <div className="flex gap-2 mt-4">
            <Badge variant="outline" className="cursor-pointer" onClick={() => setSearchQuery('último mes')}>Último mes</Badge>
            <Badge variant="outline" className="cursor-pointer" onClick={() => setSearchQuery('alta precisión')}>Alta precisión (&gt;90%)</Badge>
            <Badge variant="outline" className="cursor-pointer" onClick={() => setSearchQuery('validados')}>Validados</Badge>
            <Badge variant="outline" className="cursor-pointer" onClick={() => setSearchQuery('FAIR')}>FAIR compliant</Badge>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="reports">
        <TabsList>
          <TabsTrigger value="reports">Reportes Comparativos</TabsTrigger>
          <TabsTrigger value="queries">Resultados de Búsqueda</TabsTrigger>
          <TabsTrigger value="benchmarks">Análisis Comparativo</TabsTrigger>
        </TabsList>

        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Reportes y Resultados</CardTitle>
              <CardDescription>Comparativos y análisis generados automáticamente</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingReports ? (
                <p className="text-sm text-gray-500">Cargando reportes...</p>
              ) : recentReports.length === 0 ? (
                <p className="text-sm text-gray-500">No hay reportes disponibles. Realiza un análisis primero.</p>
              ) : (
                <div className="space-y-3">
                  {recentReports.map((report, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <FileText className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium">{report.tipo}</p>
                          <div className="flex items-center gap-3 mt-1">
                            <p className="text-sm text-gray-600">{report.descripcion}</p>
                            <span className="text-gray-400">•</span>
                            <p className="text-sm text-gray-600">{report.fecha_ultima}</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{report.cantidad} resultados</Badge>
                            <div className="flex items-center gap-2">
                              <Button variant="ghost" size="sm" onClick={() => handleDownloadReport(report, 'csv')}>
                                <Download className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="sm" onClick={() => handleDownloadReport(report, 'pdf')}>
                                <FileText className="h-4 w-4" />
                              </Button>
                            </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              
              <Button variant="outline" className="w-full mt-4" onClick={cargarReportes}>
                🔄 Actualizar reportes
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="queries" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Resultados de Búsqueda</CardTitle>
              <CardDescription>Resultados encontrados para: "{searchQuery}"</CardDescription>
            </CardHeader>
            <CardContent>
              {!searchResults ? (
                <p className="text-sm text-gray-500">Realiza una búsqueda para ver resultados aquí</p>
              ) : (
                <div className="space-y-6">
                  {searchResults.resultados.secuencias && searchResults.resultados.secuencias.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-3">Secuencias ({searchResults.resultados.secuencias.length})</h3>
                      <div className="space-y-2">
                        {searchResults.resultados.secuencias.map((seq: any, idx: number) => (
                          <div key={idx} className="p-3 border rounded-lg hover:bg-gray-50">
                            <p className="font-medium">{seq.nombre}</p>
                            <p className="text-sm text-gray-600">{seq.fecha}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {searchResults.resultados.experimentos && searchResults.resultados.experimentos.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-3">Experimentos ({searchResults.resultados.experimentos.length})</h3>
                      <div className="space-y-2">
                        {searchResults.resultados.experimentos.map((exp: any, idx: number) => (
                          <div key={idx} className="p-3 border rounded-lg hover:bg-gray-50">
                            <p className="font-medium">{exp.tipo}</p>
                            <div className="flex justify-between items-center mt-1">
                              <p className="text-sm text-gray-600">{exp.fecha}</p>
                              <Badge variant={exp.estado === 'completado' ? 'default' : 'secondary'}>
                                {exp.estado}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {searchResults.resultados.alertas && searchResults.resultados.alertas.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-3">Alertas ({searchResults.resultados.alertas.length})</h3>
                      <div className="space-y-2">
                        {searchResults.resultados.alertas.map((alerta: any, idx: number) => (
                          <div key={idx} className="p-3 border rounded-lg hover:bg-gray-50">
                            <p className="font-medium">{alerta.mensaje}</p>
                            <p className="text-sm text-gray-600">{alerta.fecha}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="benchmarks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Comparativos de Resultados</CardTitle>
              <CardDescription>Análisis comparativo entre diferentes tipos de análisis (HU-010)</CardDescription>
            </CardHeader>
            <CardContent>
              {recentReports.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-600 mb-4">No hay experimentos disponibles para comparar</p>
                  <Button onClick={cargarReportes}>Cargar reportes</Button>
                </div>
              ) : (
                <>
                  <div className="space-y-3">
                    {recentReports.map((report, idx) => (
                      <div key={idx} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-4">
                          <BarChart3 className="h-5 w-5 text-purple-600" />
                          <div>
                            <p className="font-medium">{report.tipo}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              Total: {report.cantidad} análisis • Última actualización: {report.fecha_ultima}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <p className="text-sm text-gray-600">Resultados</p>
                            <p className="text-lg font-semibold">{report.cantidad}</p>
                          </div>
                          <Badge variant="default">
                            {report.estado}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm">
                      <strong>Resumen:</strong> Se han procesado {recentReports.reduce((sum, r) => sum + r.cantidad, 0)} análisis en total. 
                      Todos los resultados están disponibles para descarga en formato CSV o PDF.
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
