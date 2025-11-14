import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import { Cpu, Play, Settings, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';
import { Progress } from './ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import axios from 'axios';

interface PLMExecutionProps {
  token: string | null;
}

export function PLMExecution({ token }: PLMExecutionProps) {
  const [selectedModel, setSelectedModel] = useState('esm2');
  const [selectedSequenceIndex, setSelectedSequenceIndex] = useState<number>(0);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [sequences, setSequences] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [isLoadingSequences, setIsLoadingSequences] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const models = [
    { id: 'esm2', name: 'ESM-2', description: 'Estado del arte en predicción de estructura', accuracy: '95%' },
    { id: 'protbert', name: 'ProtBERT', description: 'Modelo basado en BERT para proteínas', accuracy: '92%' },
    { id: 'prottrans', name: 'ProtTrans', description: 'Transformer optimizado para secuencias', accuracy: '90%' },
    { id: 'alphafold', name: 'AlphaFold', description: 'Predicción de plegamiento 3D', accuracy: '94%' },
  ];

  // Cargar secuencias al montar
  useEffect(() => {
    cargarSecuencias();
  }, [token]);

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

  const handleRunModel = async () => {
    if (sequences.length === 0) {
      toast.error('Por favor carga al menos una secuencia');
      return;
    }

    setIsRunning(true);
    setProgress(0);
    
    try {
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            return prev;
          }
          return prev + Math.random() * 20;
        });
      }, 300);

      const formData = new FormData();
      formData.append('idx_or_id', selectedSequenceIndex.toString());

      const response = await axios.post(`${API_URL}/analizar_plm/`, formData);
      
      clearInterval(interval);
      setProgress(100);

      if (response.data.resultado) {
        setResults([...results, {
          id: results.length + 1,
          sequence: sequences[selectedSequenceIndex]?.nombre || 'Desconocida',
          model: models.find(m => m.id === selectedModel)?.name || 'Modelo',
          result: response.data.resultado,
          date: new Date().toLocaleDateString(),
          timestamp: new Date().toISOString()
        }]);

        toast.success('Predicción completada', {
          description: 'Los resultados están disponibles abajo'
        });
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Error en el análisis PLM';
      toast.error(message);
      console.error('Error:', error);
    } finally {
      setIsRunning(false);
      setProgress(0);
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Ejecución de Modelos PLM</h1>
        <p className="text-gray-600">Ejecuta modelos de lenguaje proteico preentrenados (HU-003)</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model Configuration */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Selección de Modelo</CardTitle>
              <CardDescription>Elige el modelo PLM para tu análisis</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {models.map((model) => (
                  <Card 
                    key={model.id}
                    className={`cursor-pointer transition-all ${selectedModel === model.id ? 'ring-2 ring-blue-500' : ''}`}
                    onClick={() => setSelectedModel(model.id)}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-base">{model.name}</CardTitle>
                          <CardDescription className="text-xs mt-1">{model.description}</CardDescription>
                        </div>
                        <Badge variant="outline">{model.accuracy}</Badge>
                      </div>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Configuración de Parámetros</CardTitle>
              <CardDescription>Ajusta los parámetros del modelo (HU-007)</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="sequence-select">Secuencia a Analizar</Label>
                {isLoadingSequences ? (
                  <p className="text-sm text-gray-500">Cargando secuencias...</p>
                ) : sequences.length === 0 ? (
                  <p className="text-sm text-gray-500">No hay secuencias disponibles. Carga una secuencia primero.</p>
                ) : (
                  <Select value={selectedSequenceIndex.toString()} onValueChange={(val) => setSelectedSequenceIndex(parseInt(val))}>
                    <SelectTrigger id="sequence-select" disabled={isRunning}>
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
                <Label htmlFor="property">Propiedad a Predecir</Label>
                <Select defaultValue="stability">
                  <SelectTrigger id="property" disabled={isRunning}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="stability">Estabilidad</SelectItem>
                    <SelectItem value="function">Función</SelectItem>
                    <SelectItem value="structure">Estructura 3D</SelectItem>
                    <SelectItem value="interactions">Interacciones</SelectItem>
                    <SelectItem value="mutations">Efectos de Mutaciones</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Temperatura del Modelo</Label>
                  <span className="text-sm text-gray-600">0.7</span>
                </div>
                <Slider defaultValue={[0.7]} max={1} step={0.1} disabled={isRunning} />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Confianza Mínima</Label>
                  <span className="text-sm text-gray-600">80%</span>
                </div>
                <Slider defaultValue={[80]} max={100} step={5} disabled={isRunning} />
              </div>

              <Button 
                onClick={handleRunModel} 
                disabled={isRunning || sequences.length === 0}
                className="w-full"
              >
                <Play className="mr-2 h-4 w-4" />
                {isRunning ? `Ejecutando... ${progress}%` : 'Ejecutar Predicción'}
              </Button>

              {isRunning && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Procesando...</span>
                    <span>{Math.round(progress)}%</span>
                  </div>
                  <Progress value={progress} />
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Modelo Seleccionado</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Cpu className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <p>{models.find(m => m.id === selectedModel)?.name}</p>
                  <p className="text-sm text-gray-600">PLM Pre-entrenado</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Precisión:</span>
                  <span>{models.find(m => m.id === selectedModel)?.accuracy}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Parámetros:</span>
                  <span>650M</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tiempo Est.:</span>
                  <span>~2 min</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Predicciones Recientes ({results.length})</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {results.length === 0 ? (
                <p className="text-sm text-gray-500">No hay predicciones aún</p>
              ) : (
                results.map((result) => (
                  <div key={result.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium">{result.sequence}</p>
                      <Badge variant="outline" className="text-xs">{result.model}</Badge>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">Resultado: {JSON.stringify(result.result).substring(0, 50)}...</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">{result.date}</span>
                      <Badge>Completado</Badge>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
