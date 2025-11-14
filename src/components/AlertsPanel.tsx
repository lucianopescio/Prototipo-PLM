import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { AlertTriangle, CheckCircle, Info, Bell, X, Mail } from 'lucide-react';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { toast } from 'sonner@2.0.3';

export function AlertsPanel() {
  const alerts = [
    {
      id: 1,
      type: 'error',
      title: 'Inconsistencia detectada en simulación',
      description: 'La simulación de cinética enzimática muestra resultados fuera del rango esperado. Se recomienda revisar parámetros de pH.',
      timestamp: '2025-11-06 14:32',
      experiment: 'Cinética enzimática - Kinase_mutant',
      severity: 'high'
    },
    {
      id: 2,
      type: 'warning',
      title: 'Precisión por debajo del umbral',
      description: 'El modelo ProtBERT ha generado predicciones con confianza del 78%, por debajo del umbral configurado (80%).',
      timestamp: '2025-11-06 11:15',
      experiment: 'Predicción BRCA1_variant',
      severity: 'medium'
    },
    {
      id: 3,
      type: 'info',
      title: 'Dataset requiere actualización',
      description: 'El dataset "Antibody_Sequences" no ha sido actualizado en 30 días. Se recomienda revisar y curar.',
      timestamp: '2025-11-06 09:00',
      experiment: 'Gestión de datos',
      severity: 'low'
    },
  ];

  const handleDismiss = (id: number) => {
    toast.success('Alerta marcada como resuelta');
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'info':
        return <Info className="h-5 w-5 text-blue-600" />;
      default:
        return <Bell className="h-5 w-5" />;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return <Badge variant="destructive">Alta</Badge>;
      case 'medium':
        return <Badge className="bg-yellow-600">Media</Badge>;
      case 'low':
        return <Badge variant="secondary">Baja</Badge>;
      default:
        return <Badge variant="outline">Info</Badge>;
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Centro de Alertas</h1>
        <p className="text-gray-600">Notificaciones automáticas y gestión de inconsistencias (HU-005)</p>
      </div>

      {/* Alert Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Alertas Activas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">3</div>
            <p className="text-xs text-gray-600 mt-1">Requieren atención</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Críticas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-red-600">1</div>
            <p className="text-xs text-gray-600 mt-1">Prioridad alta</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Resueltas Hoy</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-green-600">7</div>
            <p className="text-xs text-gray-600 mt-1">Gestión efectiva</p>
          </CardContent>
        </Card>
      </div>

      {/* Alerts List */}
      <Card>
        <CardHeader>
          <CardTitle>Alertas Recientes</CardTitle>
          <CardDescription>Notificaciones automáticas del sistema</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {alerts.map((alert) => (
            <div 
              key={alert.id} 
              className={`p-4 border rounded-lg ${
                alert.type === 'error' ? 'bg-red-50 border-red-200' :
                alert.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                'bg-blue-50 border-blue-200'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  {getAlertIcon(alert.type)}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <p>{alert.title}</p>
                      {getSeverityBadge(alert.severity)}
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{alert.description}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-600">
                      <span>{alert.timestamp}</span>
                      <span>•</span>
                      <span>{alert.experiment}</span>
                    </div>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => handleDismiss(alert.id)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              
              <div className="flex gap-2 mt-3">
                <Button size="sm" variant="outline">Ver Detalles</Button>
                <Button size="sm" variant="outline">Sugerencias</Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Configuración de Notificaciones</CardTitle>
          <CardDescription>Personaliza tus preferencias de alertas</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bell className="h-5 w-5 text-gray-600" />
              <div>
                <Label>Alertas visuales en el sistema</Label>
                <p className="text-sm text-gray-600">Mostrar notificaciones en tiempo real</p>
              </div>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail className="h-5 w-5 text-gray-600" />
              <div>
                <Label>Notificaciones por correo electrónico</Label>
                <p className="text-sm text-gray-600">Recibir alertas críticas por email</p>
              </div>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-gray-600" />
              <div>
                <Label>Solo alertas de alta prioridad</Label>
                <p className="text-sm text-gray-600">Filtrar notificaciones de baja severidad</p>
              </div>
            </div>
            <Switch />
          </div>

          <div className="pt-4 border-t">
            <h3 className="mb-3">Tipos de alertas a recibir:</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Switch defaultChecked />
                <Label>Inconsistencias en simulaciones</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch defaultChecked />
                <Label>Predicciones con baja confianza</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch defaultChecked />
                <Label>Errores de validación de datos</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch />
                <Label>Recordatorios de mantenimiento</Label>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
