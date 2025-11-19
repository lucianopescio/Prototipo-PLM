import { useState, useEffect } from 'react';

interface Alert {
  id: string;
  tipo: string;
  mensaje: string;
  prioridad: string;
  fecha: string;
  resuelta: boolean;
  automatica?: boolean;
}

interface AlertsPanelProps {
  token: string | null;
}

export function AlertsPanel({ token }: AlertsPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_URL}/alertas/`);
      const data = await response.json();
      setAlerts(data.alertas || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      toast.error('Error cargando alertas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleDismiss = async (alertaId: string) => {
    try {
      const response = await fetch(`${API_URL}/alerta/${alertaId}/resolver`, {
        method: 'PUT',
      });
      if (response.ok) {
        toast.success('Alerta marcada como resuelta');
        fetchAlerts(); // Refresh alerts
      } else {
        toast.error('Error resolviendo alerta');
      }
    } catch (error) {
      console.error('Error dismissing alert:', error);
      toast.error('Error resolviendo alerta');
    }
  };

  const createAlert = async (tipo: string, mensaje: string, prioridad: string) => {
    try {
      const response = await fetch(`${API_URL}/alerta/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          tipo,
          mensaje,
          prioridad,
        }),
      });
      if (response.ok) {
        toast.success('Nueva alerta creada');
        fetchAlerts(); // Refresh alerts
      } else {
        toast.error('Error creando alerta');
      }
    } catch (error) {
      console.error('Error creating alert:', error);
      toast.error('Error creando alerta');
    }
  };

  const generateReport = async () => {
    try {
      const response = await fetch(`${API_URL}/reportes/comparativos/`);
      const data = await response.json();
      
      // Show report data in toast
      toast.success(`Reporte generado: ${data.total_experimentos} experimentos, ${data.total_secuencias} secuencias`);
      
      // You could also trigger a PDF download here if needed
      console.log('Report data:', data);
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Error generando reporte');
    }
  };

  const getAlertIcon = (tipo: string) => {
    switch (tipo?.toLowerCase()) {
      case 'error':
      case 'critica':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'warning':
      case 'advertencia':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'info':
      case 'informacion':
        return <Info className="h-5 w-5 text-blue-600" />;
      default:
        return <Bell className="h-5 w-5" />;
    }
  };

  const getSeverityBadge = (prioridad: string) => {
    switch (prioridad?.toLowerCase()) {
      case 'alta':
      case 'high':
        return <Badge variant="destructive">Alta</Badge>;
      case 'media':
      case 'medium':
        return <Badge className="bg-yellow-600">Media</Badge>;
      case 'baja':
      case 'low':
        return <Badge variant="secondary">Baja</Badge>;
      default:
        return <Badge variant="outline">Info</Badge>;
    }
  };

  // Get alert counts
  const activeAlerts = alerts.filter(alert => !alert.resuelta);
  const criticalAlerts = activeAlerts.filter(alert => alert.prioridad?.toLowerCase() === 'alta');
  const resolvedAlerts = alerts.filter(alert => alert.resuelta);

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Centro de Alertas</h1>
        <p className="text-gray-600">Notificaciones automáticas y gestión de inconsistencias (HU-005)</p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <Button onClick={generateReport} className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Generar Reporte de Alertas
        </Button>
        <Button 
          variant="outline" 
          onClick={() => createAlert('info', 'Alerta de prueba creada desde la interfaz', 'media')}
          className="flex items-center gap-2"
        >
          <Bell className="h-4 w-4" />
          Crear Alerta de Prueba
        </Button>
      </div>

      {/* Alert Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Alertas Activas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">{activeAlerts.length}</div>
            <p className="text-xs text-gray-600 mt-1">Requieren atención</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Críticas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-red-600">{criticalAlerts.length}</div>
            <p className="text-xs text-gray-600 mt-1">Prioridad alta</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Resueltas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-green-600">{resolvedAlerts.length}</div>
            <p className="text-xs text-gray-600 mt-1">Procesadas exitosamente</p>
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
          {loading ? (
            <div className="text-center py-4">Cargando alertas...</div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-4 text-gray-500">
              <Bell className="h-8 w-8 mx-auto mb-2 opacity-50" />
              No hay alertas en el sistema
            </div>
          ) : (
            alerts.map((alert) => (
              <div 
                key={alert.id} 
                className={`p-4 border rounded-lg ${
                  alert.resuelta ? 'opacity-60 bg-gray-50' : 
                  alert.tipo === 'error' ? 'bg-red-50 border-red-200' :
                  alert.tipo === 'warning' ? 'bg-yellow-50 border-yellow-200' :
                  'bg-blue-50 border-blue-200'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1">
                    {getAlertIcon(alert.tipo)}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <p className="font-medium">
                          {alert.tipo.charAt(0).toUpperCase() + alert.tipo.slice(1)}
                          {alert.resuelta && <CheckCircle className="h-4 w-4 text-green-600 ml-2 inline" />}
                        </p>
                        {getSeverityBadge(alert.prioridad)}
                        {alert.automatica && (
                          <Badge variant="outline" className="text-xs">Auto</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{alert.mensaje}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-600">
                        <span>{new Date(alert.fecha).toLocaleString()}</span>
                        <span>•</span>
                        <span>Estado: {alert.resuelta ? 'Resuelta' : 'Activa'}</span>
                      </div>
                    </div>
                  </div>
                  {!alert.resuelta && (
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => handleDismiss(alert.id)}
                      title="Marcar como resuelta"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                
                <div className="flex gap-2 mt-3">
                  <Button size="sm" variant="outline" disabled={loading}>
                    Ver Detalles
                  </Button>
                  {!alert.resuelta && (
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleDismiss(alert.id)}
                    >
                      Resolver
                    </Button>
                  )}
                </div>
              </div>
            ))
          )}
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
