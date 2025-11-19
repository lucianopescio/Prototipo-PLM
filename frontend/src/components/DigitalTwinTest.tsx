import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

interface DigitalTwinTestProps {
  token: string | null;
}

export function DigitalTwinTest({ token }: DigitalTwinTestProps) {
  console.log('DigitalTwinTest rendering with token:', token);
  
  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Gemelo Digital de Biorreactor - Test</h1>
        <p className="text-gray-600">Componente de prueba para depuración</p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Estado del Componente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p>Token: {token ? 'Disponible' : 'No disponible'}</p>
            <p>Hora actual: {new Date().toLocaleString()}</p>
            <p>Este es un componente de prueba funcional</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}