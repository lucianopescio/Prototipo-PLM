import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { FlaskConical, Play, AlertTriangle, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Slider } from './ui/slider';
import { Progress } from './ui/progress';
import axios from 'axios';

interface VirtualLabProps {
  token: string | null;
}

export function VirtualLab({ token }: VirtualLabProps) {
  const [isSimulating, setIsSimulating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [sequences, setSequences] = useState<any[]>([]);
  const [selectedSequenceIndex, setSelectedSequenceIndex] = useState<number>(0);
  const [experiments, setExperiments] = useState<any[]>([]);
  const [isLoadingSequences, setIsLoadingSequences] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    cargarSecuencias();
    cargarExperimentos();
  }, [token]);

  const cargarExperimentos = async () => {
    try {
      const headers: any = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const response = await axios.get(`${API_URL}/experimentos/`, { headers });
      if (response.data.experimentos) {
        setExperiments(response.data.experimentos);
      }
    } catch (error) {
      console.error('Error cargando experimentos:', error);
    }
  };

  const cargarSecuencias = async () => {
    setIsLoadingSequences(true);
    try {
      const response = await axios.get(`${API_URL}/secuencias/`);
      if (response.data.secuencias) {
        setSequences(response.data.secuencias);
        if (response.data.secuencias.length > 0) {
          setSelectedSequenceIndex(0);
        }
      }
    } catch (error) {
      console.error('Error cargando secuencias:', error);
      toast.error('Error al cargar secuencias');
    } finally {
      setIsLoadingSequences(false);
    }
  };

  const handleRunSimulation = async () => {
    if (sequences.length === 0) {
      toast.error('Por favor carga al menos una secuencia');
      return;
    }

    setIsSimulating(true);
    setProgress(0);
    
    try {
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            return prev;
          }
          return prev + Math.random() * 15;
        });
      }, 400);

      const formData = new FormData();
      formData.append('idx_or_id', selectedSequenceIndex.toString());

      const response = await axios.post(`${API_URL}/simular_laboratorio/`, formData);
      
      clearInterval(interval);
      setProgress(100);

      if (response.data) {
        // refrescar desde backend para obtener ID y datos reales
        await cargarExperimentos();
        toast.success('Simulación de laboratorio completada', {
          description: 'Resultados disponibles para análisis'
        });
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Error en la simulación';
      toast.error(message);
      console.error('Error:', error);
    } finally {
      setIsSimulating(false);
      setProgress(0);
    }
  };

  const handleDownloadExperiment = async (exp: any, format: string = 'txt') => {
    try {
      toast.info('Preparando descarga del informe...');
      const headers: any = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      const url = `${API_URL}/experimentos/${encodeURIComponent(exp.id)}/download?format=${encodeURIComponent(format)}`;
      const resp = await axios.get(url, { responseType: 'blob', headers });
      const blob = new Blob([resp.data], { type: resp.headers['content-type'] || (format === 'pdf' ? 'application/pdf' : 'text/plain') });
      const filename = resp.headers['content-disposition']?.split('filename=')[1]?.replace(/"/g, '') || `experimento_${exp.id}.${format}`;
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(link.href);
      toast.success(`Descarga iniciada: ${filename}`);
    } catch (error) {
      console.error('Error descargando informe:', error);
      const message = (error as any).response?.data?.detail || 'Error al descargar informe';
      toast.error(message);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Laboratorio Virtual</h1>
        <p className="text-gray-600">Simula experimentos para validar predicciones (HU-004)</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configuración de Experimento</CardTitle>
              <CardDescription>Define los parámetros experimentales para la simulación</CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="thermal">
                <TabsList className="grid grid-cols-3 w-full">
                  <TabsTrigger value="thermal">Estabilidad Térmica</TabsTrigger>
                  <TabsTrigger value="ph">Prueba de pH</TabsTrigger>
                  <TabsTrigger value="kinetic">Cinética</TabsTrigger>
                </TabsList>

                <TabsContent value="thermal" className="space-y-4 mt-4">
                  <div>
                    <Label htmlFor="protein-thermal">Proteína</Label>
                    {isLoadingSequences ? (
                      <p className="text-sm text-gray-500">Cargando secuencias...</p>
                    ) : sequences.length === 0 ? (
                      <p className="text-sm text-gray-500">No hay secuencias disponibles</p>
                    ) : (
                      <Select value={selectedSequenceIndex.toString()} onValueChange={(val) => setSelectedSequenceIndex(parseInt(val))}>
                        <SelectTrigger id="protein-thermal" disabled={isSimulating}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {sequences.map((seq, idx) => (
                            <SelectItem key={idx} value={idx.toString()}>
                              {seq.nombre}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label>Temperatura Inicial (°C)</Label>
                      <span className="text-sm text-gray-600">25°C</span>
                    </div>
                    <Slider defaultValue={[25]} min={0} max={100} step={5} disabled={isSimulating} />
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label>Temperatura Final (°C)</Label>
                      <span className="text-sm text-gray-600">95°C</span>
                    </div>
                    <Slider defaultValue={[95]} min={0} max={100} step={5} />
                  </div>

                  <div>
                    <Label htmlFor="time-thermal">Duración (minutos)</Label>
                    <Input id="time-thermal" type="number" defaultValue="60" />
                  </div>
                </TabsContent>

                <TabsContent value="ph" className="space-y-4 mt-4">
                  <div>
                    <Label htmlFor="protein-ph">Proteína</Label>
                    <Select defaultValue="p53">
                      <SelectTrigger id="protein-ph">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="p53">P53_HUMAN</SelectItem>
                        <SelectItem value="brca1">BRCA1_variant</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label>pH Mínimo</Label>
                      <span className="text-sm text-gray-600">4.0</span>
                    </div>
                    <Slider defaultValue={[4]} min={1} max={14} step={0.5} />
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label>pH Máximo</Label>
                      <span className="text-sm text-gray-600">10.0</span>
                    </div>
                    <Slider defaultValue={[10]} min={1} max={14} step={0.5} />
                  </div>

                  <div>
                    <Label htmlFor="buffer">Buffer</Label>
                    <Select defaultValue="pbs">
                      <SelectTrigger id="buffer">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pbs">PBS</SelectItem>
                        <SelectItem value="tris">Tris-HCl</SelectItem>
                        <SelectItem value="acetate">Acetato</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>

                <TabsContent value="kinetic" className="space-y-4 mt-4">
                  <div>
                    <Label htmlFor="enzyme">Enzima</Label>
                    <Select defaultValue="kinase">
                      <SelectTrigger id="enzyme">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="kinase">Kinase_mutant</SelectItem>
                        <SelectItem value="protease">Protease_A</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="substrate">Concentración Sustrato (mM)</Label>
                    <Input id="substrate" type="number" defaultValue="1.0" step="0.1" />
                  </div>

                  <div>
                    <Label htmlFor="enzyme-conc">Concentración Enzima (µM)</Label>
                    <Input id="enzyme-conc" type="number" defaultValue="0.5" step="0.1" />
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label>Temperatura (°C)</Label>
                      <span className="text-sm text-gray-600">37°C</span>
                    </div>
                    <Slider defaultValue={[37]} min={0} max={60} step={1} />
                  </div>
                </TabsContent>
              </Tabs>

              <Button 
                onClick={handleRunSimulation} 
                disabled={isSimulating || sequences.length === 0}
                className="w-full mt-6"
              >
                <Play className="mr-2 h-4 w-4" />
                {isSimulating ? `Simulando... ${Math.round(progress)}%` : 'Iniciar Simulación'}
              </Button>

              {isSimulating && (
                <div className="space-y-2 mt-4">
                  <div className="flex justify-between text-sm">
                    <span>Procesando simulación...</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <Progress value={progress} />
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Experimentos Realizados ({experiments.length})</CardTitle>
              <CardDescription>Historial de simulaciones en laboratorio virtual</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {experiments.length === 0 ? (
                  <p className="text-sm text-gray-500">No hay experimentos aún</p>
                ) : (
                experiments.map((exp) => (
                  <div key={exp.id} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FlaskConical className="h-5 w-5 text-purple-600" />
                        <div>
                          <p className="font-medium">{exp.tipo} - ID {exp.id}</p>
                          <p className="text-sm text-gray-600">{exp.fecha}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge variant={exp.estado === 'completado' ? 'default' : 'secondary'}>
                          {exp.estado}
                        </Badge>
                      </div>
                    </div>
                    <div className="mt-3 text-sm text-gray-700">
                      <details>
                        <summary className="cursor-pointer">Ver resultado / acciones</summary>
                        <pre className="mt-2 whitespace-pre-wrap text-xs bg-gray-50 p-3 rounded">{JSON.stringify(exp.resultado, null, 2)}</pre>
                        <div className="flex gap-2 mt-3">
                          <Button size="sm" onClick={() => handleDownloadExperiment(exp, 'txt')}>Descargar TXT</Button>
                          <Button size="sm" onClick={() => handleDownloadExperiment(exp, 'pdf')}>Descargar PDF</Button>
                          <Button size="sm" onClick={() => navigator.clipboard.writeText(JSON.stringify(exp.resultado))}>Copiar JSON</Button>
                        </div>
                      </details>
                    </div>
                  </div>
                ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Validación de Predicciones</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-sm">Predicciones PLM</p>
                    <p className="text-xs text-gray-600 mt-1">Se validarán contra resultados experimentales</p>
                  </div>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Predicción ESM-2:</span>
                  <span>0.87</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Resultado Lab Virtual:</span>
                  <span className="text-green-600">Pendiente</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Alertas de Calidad</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                  <div>
                    <p className="text-sm">Inconsistencia Detectada</p>
                    <p className="text-xs text-gray-600 mt-1">Experimento: Cinética enzimática</p>
                    <p className="text-xs text-gray-600">Revisar parámetros de pH</p>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="text-sm">Validación Exitosa</p>
                    <p className="text-xs text-gray-600 mt-1">Estabilidad térmica P53</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
