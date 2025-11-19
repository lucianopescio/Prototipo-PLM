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
  // token puede ser usado en el futuro para autenticación
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchAlerts = async () => {
    try {
      console.log('Fetching alerts from:', `${API_URL}/alertas/`);
      const response = await fetch(`${API_URL}/alertas/`);
      const data = await response.json();
      console.log('Alerts data:', data);
      setAlerts(data.alertas || []);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  if (loading) {
    return (
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Centro de Alertas</h1>
        <p>Cargando alertas...</p>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-2">Centro de Alertas</h1>
        <p className="text-gray-600">Notificaciones automáticas y gestión de inconsistencias (HU-005)</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Alertas Activas ({alerts.length})</h2>
        
        {alerts.length === 0 ? (
          <p className="text-gray-500">No hay alertas disponibles</p>
        ) : (
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{alert.mensaje}</h3>
                    <p className="text-sm text-gray-500">
                      Tipo: {alert.tipo} | Prioridad: {alert.prioridad}
                    </p>
                    <p className="text-sm text-gray-400">
                      {new Date(alert.fecha).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {alert.automatica && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        Auto
                      </span>
                    )}
                    <span className={`text-xs px-2 py-1 rounded ${
                      alert.prioridad === 'info' ? 'bg-green-100 text-green-800' :
                      alert.prioridad === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {alert.prioridad}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}