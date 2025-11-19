import { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Dashboard } from './Dashboard';
import { SequenceUpload } from './SequenceUpload';
import { PLMExecution } from './PLMExecution';
import { VirtualLab } from './VirtualLab';
import { DatasetManagement } from './DatasetManagement';
import { DigitalTwin } from './DigitalTwin';
import { DigitalTwinTest } from './DigitalTwinTest';
import { QueryInterface } from './QueryInterface';
import { AlertsPanel } from './AlertsPanelSimple';

interface MainLayoutProps {
  onLogout: () => void;
  token: string | null;
  usuario: any;
}

export type ViewType = 'dashboard' | 'upload' | 'plm' | 'lab' | 'datasets' | 'twin' | 'query' | 'alerts';

export function MainLayout({ onLogout, token, usuario }: MainLayoutProps) {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');

  useEffect(() => {
    // Si el token deja de existir, forzar logout/redirect al Login
    if (!token) {
      onLogout();
    }
  }, [token, onLogout]);

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard token={token} />;
      case 'upload':
        return <SequenceUpload token={token} />;
      case 'plm':
        return <PLMExecution token={token} />;
      case 'lab':
        return <VirtualLab token={token} />;
      case 'datasets':
        return <DatasetManagement token={token} />;
      case 'twin':
        return <DigitalTwin token={token} />;
      case 'query':
        return <QueryInterface token={token} />;
      case 'alerts':
        return <AlertsPanel token={token} />;
      default:
        return <Dashboard token={token} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar 
        currentView={currentView} 
        onViewChange={setCurrentView}
        onLogout={onLogout}
        usuario={usuario}
      />
      <main className="flex-1 overflow-auto">
        {renderView()}
      </main>
    </div>
  );
}
