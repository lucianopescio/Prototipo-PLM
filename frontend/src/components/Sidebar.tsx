import { 
  LayoutDashboard, 
  Upload, 
  Cpu, 
  FlaskConical, 
  Database, 
  Network,
  Search,
  Bell,
  LogOut
} from 'lucide-react';
import { Button } from './ui/button';
import { ViewType } from './MainLayout';
import { Badge } from './ui/badge';

interface SidebarProps {
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
  onLogout: () => void;
  usuario?: any;
}

export function Sidebar({ currentView, onViewChange, onLogout, usuario }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard' as ViewType, label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload' as ViewType, label: 'Cargar Secuencias', icon: Upload },
    { id: 'plm' as ViewType, label: 'Modelos PLM', icon: Cpu },
    { id: 'lab' as ViewType, label: 'Laboratorio Virtual', icon: FlaskConical },
    { id: 'datasets' as ViewType, label: 'Gestión de Datos', icon: Database },
    { id: 'twin' as ViewType, label: 'Gemelo Digital', icon: Network },
    { id: 'query' as ViewType, label: 'Consultas', icon: Search },
    { id: 'alerts' as ViewType, label: 'Alertas', icon: Bell, badge: 3 },
  ];

  return (
    <aside className="w-64 bg-gradient-to-b from-[#000033] to-[#1a1a4d] text-white p-4 flex flex-col">
      <div className="mb-8 p-4">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-3">
          <svg viewBox="0 0 24 24" className="w-8 h-8 text-white" fill="currentColor">
            <path d="M12 2L10 8L8 4L6 10L4 6L2 12L4 18L6 14L8 20L10 16L12 22L14 16L16 20L18 14L20 18L22 12L20 6L18 10L16 4L14 8L12 2Z" />
          </svg>
        </div>
        <h2>Protein Analysis</h2>
        <p className="text-blue-200 text-sm">Sistema PLM</p>
      </div>

      <nav className="flex-1 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? 'secondary' : 'ghost'}
              className={`w-full justify-start ${
                isActive 
                  ? 'bg-white/10 text-white hover:bg-white/20' 
                  : 'text-blue-100 hover:bg-white/5 hover:text-white'
              }`}
              onClick={() => onViewChange(item.id)}
            >
              <Icon className="mr-3 h-5 w-5" />
              <span className="flex-1 text-left">{item.label}</span>
              {item.badge && (
                <Badge variant="destructive" className="ml-2">
                  {item.badge}
                </Badge>
              )}
            </Button>
          );
        })}
      </nav>

      <div className="pt-4 border-t border-white/10">
        {usuario && (
          <div className="mb-4 p-3 bg-white/5 rounded-lg">
            <p className="text-xs text-gray-400">Usuario</p>
            <p className="text-sm font-medium truncate">{usuario.nombre}</p>
            <p className="text-xs text-gray-400">{usuario.rol}</p>
          </div>
        )}
        <Button
          variant="ghost"
          className="w-full justify-start text-blue-100 hover:bg-white/5 hover:text-white"
          onClick={onLogout}
        >
          <LogOut className="mr-3 h-5 w-5" />
          Cerrar Sesión
        </Button>
      </div>
    </aside>
  );
}
