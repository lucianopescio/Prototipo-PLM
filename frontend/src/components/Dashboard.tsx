import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Activity, TrendingUp, Database, CheckCircle } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { InformeDownloader } from './InformeDownloader';

interface DashboardProps {
  token: string | null;
}

export function Dashboard({ token }: DashboardProps) {
  const [stats, setStats] = useState({
    totalAnalisis: 0,
    prediccionesActivas: 0,
    datasets: 0,
    precisionPromedio: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    cargarDatos();
  }, [token]);

  const cargarDatos = async () => {
    setIsLoading(true);
    try {
      const [secResponse, expResponse] = await Promise.all([
        axios.get(`${API_URL}/secuencias/`),
        axios.get(`${API_URL}/experimentos/`)
      ]);

      const secuencias = secResponse.data.secuencias || [];
      const experimentos = expResponse.data.experimentos || [];

      setStats({
        totalAnalisis: experimentos.length,
        prediccionesActivas: secuencias.length,
        datasets: secuencias.length,
        precisionPromedio: 92.4
      });
    } catch (error) {
      console.error('Error cargando datos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const analysisData = [
    { name: 'Ene', predicciones: 45, simulaciones: 30 },
    { name: 'Feb', predicciones: 52, simulaciones: 38 },
    { name: 'Mar', predicciones: 61, simulaciones: 42 },
    { name: 'Abr', predicciones: 58, simulaciones: 45 },
    { name: 'May', predicciones: 72, simulaciones: 51 },
    { name: 'Jun', predicciones: 68, simulaciones: 48 },
  ];

  const modelData = [
    { name: 'ESM-2', value: 35, color: '#3b82f6' },
    { name: 'ProtBERT', value: 25, color: '#8b5cf6' },
    { name: 'ProtTrans', value: 20, color: '#06b6d4' },
    { name: 'Otros', value: 20, color: '#6366f1' },
  ];

  const recentAnalysis = [
    { id: 1, name: 'Análisis de estabilidad P53', model: 'ESM-2', status: 'Completado', date: '2025-11-12', accuracy: '94%' },
    { id: 2, name: 'Predicción de plegamiento', model: 'ProtBERT', status: 'En proceso', date: '2025-11-12', accuracy: '-' },
    { id: 3, name: 'Simulación de mutaciones', model: 'ProtTrans', status: 'Completado', date: '2025-11-11', accuracy: '89%' },
    { id: 4, name: 'Optimización de secuencia', model: 'ESM-2', status: 'Completado', date: '2025-11-11', accuracy: '91%' },
  ];

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Dashboard de Análisis</h1>
        <p className="text-gray-600">Resumen de actividades y resultados del sistema</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Análisis Totales</CardTitle>
            <Activity className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.totalAnalisis}</div>
            <p className="text-xs text-gray-600 mt-1">+12% vs mes anterior</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Predicciones Activas</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.prediccionesActivas}</div>
            <p className="text-xs text-gray-600 mt-1">15 completadas hoy</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Datasets</CardTitle>
            <Database className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.datasets}</div>
            <p className="text-xs text-gray-600 mt-1">{stats.datasets * 0.2} GB almacenados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm">Precisión Promedio</CardTitle>
            <CheckCircle className="h-4 w-4 text-cyan-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{stats.precisionPromedio.toFixed(1)}%</div>
            <p className="text-xs text-gray-600 mt-1">Últimos 30 días</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Tendencia de Análisis</CardTitle>
            <CardDescription>Predicciones y simulaciones por mes</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analysisData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="predicciones" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="simulaciones" stroke="#8b5cf6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Uso de Modelos PLM</CardTitle>
            <CardDescription>Distribución de modelos utilizados</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={modelData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {modelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Report Downloader */}
      <InformeDownloader className="lg:col-span-2" />

      {/* Recent Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>Análisis Recientes</CardTitle>
          <CardDescription>Últimas predicciones y simulaciones realizadas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentAnalysis.map((analysis) => (
              <div key={analysis.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <p>{analysis.name}</p>
                    <Badge variant="outline">{analysis.model}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{analysis.date}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Precisión</p>
                    <p>{analysis.accuracy}</p>
                  </div>
                  <Badge variant={analysis.status === 'Completado' ? 'default' : 'secondary'}>
                    {analysis.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
