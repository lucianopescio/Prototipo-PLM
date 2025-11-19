import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card } from './ui/card';
import { useState } from 'react';
import { toast } from 'sonner';
import axios from 'axios';

interface LoginScreenProps {
  onLogin: (token: string, usuario: any) => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  const [isCreatingAccount, setIsCreatingAccount] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('Por favor completa todos los campos');
      return;
    }

    if (isCreatingAccount && password !== confirmPassword) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Intentando login con:', { email, API_URL });
      const formData = new FormData();
      formData.append('email', email);
      formData.append('password', password);

      console.log('Enviando petición a:', `${API_URL}/login/`);
      const response = await axios.post(`${API_URL}/login/`, formData);
      
      console.log('Respuesta del servidor:', response.data);
      if (response.data.token) {
        toast.success(`Bienvenido, ${response.data.usuario.nombre}!`);
        // Guardar token en sessionStorage (se cierra al cerrar navegador)
        sessionStorage.setItem('authToken', response.data.token);
        sessionStorage.setItem('usuario', JSON.stringify(response.data.usuario));
        console.log('Llamando onLogin...');
        onLogin(response.data.token, response.data.usuario);
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Error al iniciar sesión';
      toast.error(message);
      console.error('Error de login:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#000033] to-[#1a1a4d] flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 bg-white/95 backdrop-blur">
        <div className="flex flex-col items-center mb-8">
          <div className="w-20 h-20 mb-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <svg viewBox="0 0 24 24" className="w-12 h-12 text-white" fill="currentColor">
              <path d="M12 2L10 8L8 4L6 10L4 6L2 12L4 18L6 14L8 20L10 16L12 22L14 16L16 20L18 14L20 18L22 12L20 6L18 10L16 4L14 8L12 2Z" />
            </svg>
          </div>
          <h1 className="text-center mb-2">Protein Analysis Platform</h1>
          <p className="text-center text-gray-600">Sistema de análisis de proteínas y simulación de biorreactores</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Email</Label>
            <Input 
              id="email" 
              type="email" 
              placeholder="investigador@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          
          <div>
            <Label htmlFor="password">Contraseña</Label>
            <Input 
              id="password" 
              type="password"
              placeholder="Tu contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          {isCreatingAccount && (
            <div>
              <Label htmlFor="confirmPassword">Confirmar Contraseña</Label>
              <Input 
                id="confirmPassword" 
                type="password"
                placeholder="Confirma tu contraseña"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
          )}

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? 'Cargando...' : (isCreatingAccount ? 'Crear Cuenta' : 'Iniciar Sesión')}
          </Button>

          <Button 
            type="button"
            variant="outline"
            className="w-full"
            onClick={() => setIsCreatingAccount(!isCreatingAccount)}
            disabled={isLoading}
          >
            {isCreatingAccount ? 'Ya tengo cuenta' : 'Crear una Cuenta'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
