import { useState, useEffect } from "react";
import { LoginScreen } from "./components/LoginScreen";
import { MainLayout } from "./components/MainLayout";
import { Toaster } from "./components/ui/sonner";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [usuario, setUsuario] = useState<any>(null);
  const [checkingAuth, setCheckingAuth] = useState<boolean>(true);

  // Verificar si hay sesión guardada al cargar (solo durante la sesión del navegador)
  useEffect(() => {
    const savedToken = sessionStorage.getItem('authToken');
    const savedUsuario = sessionStorage.getItem('usuario');
    const validate = async () => {
      if (!savedToken || !savedUsuario) {
        setCheckingAuth(false);
        return;
      }
      try {
        const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/session/validate`, {
          headers: {
            'Authorization': `Bearer ${savedToken}`
          }
        });
        if (res.ok) {
          setToken(savedToken);
          setUsuario(JSON.parse(savedUsuario));
          setIsAuthenticated(true);
        } else {
          // token inválido -> limpiar
          sessionStorage.removeItem('authToken');
          sessionStorage.removeItem('usuario');
          setToken(null);
          setUsuario(null);
          setIsAuthenticated(false);
        }
      } catch (err) {
        console.error('Error validating token:', err);
        sessionStorage.removeItem('authToken');
        sessionStorage.removeItem('usuario');
        setToken(null);
        setUsuario(null);
        setIsAuthenticated(false);
      } finally {
        setCheckingAuth(false);
      }
    };
    validate();
  }, []);

  const handleLogin = (newToken: string, newUsuario: any) => {
    console.log('handleLogin llamado con:', { newToken, newUsuario });
    setToken(newToken);
    setUsuario(newUsuario);
    setIsAuthenticated(true);
    // Guardar sesión solo durante la sesión del navegador (se borra al cerrar)
    try {
      sessionStorage.setItem('authToken', newToken);
      sessionStorage.setItem('usuario', JSON.stringify(newUsuario));
      console.log('Usuario autenticado correctamente');
    } catch (e) {
      console.warn('Unable to save session', e);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem('usuario');
    setToken(null);
    setUsuario(null);
    setIsAuthenticated(false);
  };

  if (checkingAuth) {
    return (
      <>
        <div className="flex items-center justify-center h-screen">Cargando sesión...</div>
        <Toaster />
      </>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        <LoginScreen onLogin={handleLogin} />
        <Toaster />
      </>
    );
  }

  return (
    <>
      <MainLayout onLogout={handleLogout} token={token} usuario={usuario} />
      <Toaster />
    </>
  );
}