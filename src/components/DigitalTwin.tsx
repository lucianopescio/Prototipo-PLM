import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { Network, Play, Pause, RotateCcw, TrendingUp } from 'lucide-react';
import { Badge } from './ui/badge';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { toast } from 'sonner';
import axios from 'axios';

interface DigitalTwinProps {
  token: string | null;
}

export function DigitalTwin({ token }: DigitalTwinProps) {
  const [isRunning, setIsRunning] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [sequences, setSequences] = useState<any[]>([]);
  const [selectedSequenceIndex, setSelectedSequenceIndex] = useState<number>(0);
  const [isLoadingSequences, setIsLoadingSequences] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

  const performanceData = [
    { time: 0, biomasa: 0.5, producto: 0, viabilidad: 98 },
    { time: 6, biomasa: 2.1, producto: 0.3, viabilidad: 97 },
    { time: 12, biomasa: 4.8, producto: 1.2, viabilidad: 96 },
    { time: 18, biomasa: 8.2, producto: 2.8, viabilidad: 95 },
    { time: 24, biomasa: 12.5, producto: 5.1, viabilidad: 94 },
    { time: 30, biomasa: 15.8, producto: 8.2, viabilidad: 92 },
    { time: 36, biomasa: 17.2, producto: 11.5, viabilidad: 90 },
  ];

  const handleToggleSimulation = async () => {
    if (isRunning) {
      setIsRunning(false);
      toast.info('Simulación pausada');
      return;
    }

    if (sequences.length === 0) {
      toast.error('Por favor carga al menos una secuencia');
      return;
    }

    setIsRunning(true);
    
    try {
      const formData = new FormData();
      formData.append('idx_or_id', selectedSequenceIndex.toString());

      const response = await axios.post(`${API_URL}/simular_gemelo/`, formData);
      
      if (response.data) {
        toast.success('Simulación del gemelo digital iniciada', {
          description: 'Biorreactor en ejecución'
        });
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Error en la simulación';
      toast.error(message);
      console.error('Error:', error);
      setIsRunning(false);
    }
  };

  const handleReset = () => {
    setIsRunning(false);
    setCurrentTime(0);
    toast.info('Simulación reiniciada');
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Gemelo Digital de Biorreactor</h1>
        <p className="text-gray-600">Simulación integrada de condiciones de cultivo (HU-009)</p>
      </div>

      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Panel de Control</CardTitle>
          <CardDescription>Parámetros de cultivo y condiciones del biorreactor</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <Label htmlFor="protein-bioreactor">Proteína</Label>
              {isLoadingSequences ? (
                <p className="text-sm text-gray-500">Cargando secuencias...</p>
              ) : sequences.length === 0 ? (
                <p className="text-sm text-gray-500">No hay secuencias disponibles</p>
              ) : (
                <Select value={selectedSequenceIndex.toString()} onValueChange={(val) => setSelectedSequenceIndex(parseInt(val))}>
                  <SelectTrigger id="protein-bioreactor" disabled={isRunning}>
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
                <Label>Temperatura (°C)</Label>
                <span className="text-sm text-gray-600">37°C</span>
              </div>
              <Slider defaultValue={[37]} min={20} max={45} step={0.5} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>pH</Label>
                <span className="text-sm text-gray-600">7.2</span>
              </div>
              <Slider defaultValue={[7.2]} min={5} max={9} step={0.1} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Oxígeno Disuelto (%)</Label>
                <span className="text-sm text-gray-600">40%</span>
              </div>
              <Slider defaultValue={[40]} min={0} max={100} step={5} />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Agitación (RPM)</Label>
                <span className="text-sm text-gray-600">200</span>
              </div>
              <Slider defaultValue={[200]} min={0} max={500} step={10} />
            </div>

            <div>
              <Label htmlFor="glucose">Glucosa (g/L)</Label>
              <Input id="glucose" type="number" defaultValue="10.0" step="0.1" />
            </div>

            <div>
              <Label htmlFor="volume">Volumen (L)</Label>
              <Input id="volume" type="number" defaultValue="5.0" step="0.1" />
            </div>
          </div>

          <div className="flex items-center gap-3 mt-6">
            <Button onClick={handleToggleSimulation}>
              {isRunning ? (
                <>
                  <Pause className="mr-2 h-4 w-4" />
                  Pausar Simulación
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Iniciar Simulación
                </>
              )}
            </Button>
            <Button variant="outline" onClick={handleReset}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Reiniciar
            </Button>
            <div className="flex-1" />
            <Badge variant={isRunning ? 'default' : 'secondary'}>
              {isRunning ? 'En ejecución' : 'Detenido'}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Monitoring */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Crecimiento Celular y Producción</CardTitle>
            <CardDescription>Biomasa y producto en tiempo real</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" label={{ value: 'Tiempo (h)', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Concentración (g/L)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="biomasa" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="producto" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Viabilidad Celular</CardTitle>
            <CardDescription>Porcentaje de células viables durante el cultivo</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" label={{ value: 'Tiempo (h)', position: 'insideBottom', offset: -5 }} />
                <YAxis domain={[80, 100]} label={{ value: 'Viabilidad (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="viabilidad" stroke="#10b981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Biomasa Actual</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">17.2 g/L</div>
            <p className="text-xs text-gray-600 mt-1">+8.5% vs predicción</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Producto Acumulado</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">11.5 g/L</div>
            <p className="text-xs text-gray-600 mt-1">Rendimiento: 0.67</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Viabilidad</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-green-600">90%</div>
            <p className="text-xs text-gray-600 mt-1">Dentro del rango óptimo</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Tiempo de Cultivo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">36 h</div>
            <p className="text-xs text-gray-600 mt-1">de 72 h planificadas</p>
          </CardContent>
        </Card>
      </div>

      {/* Integration Info */}
      <Card>
        <CardHeader>
          <CardTitle>Integración con Predicciones PLM</CardTitle>
          <CardDescription>Validación cruzada de resultados</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <Network className="h-5 w-5 text-blue-600" />
                <p>Predicción ESM-2</p>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Estabilidad proteica:</span>
                  <span>Alta (0.89)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Expresión esperada:</span>
                  <span>12.3 g/L</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Concordancia:</span>
                  <span className="text-green-600">93.4%</span>
                </div>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-3 mb-3">
                <TrendingUp className="h-5 w-5 text-purple-600" />
                <p>Resultado Gemelo Digital</p>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Estabilidad observada:</span>
                  <span>Alta</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Producción actual:</span>
                  <span>11.5 g/L</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Estado:</span>
                  <Badge variant="default">Validado</Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
