// frontend/src/services/api.ts
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejo de errores
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Error del servidor
      console.error('Error de servidor:', error.response.status, error.response.data);
    } else if (error.request) {
      // Error de red
      console.error('Error de red:', error.request);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Servicio de Secuencias
export const secuenciasService = {
  cargarSecuencia: async (nombre: string, fuente: string, secuencia_texto?: string, archivo?: File) => {
    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('fuente', fuente);
    
    if (archivo) {
      formData.append('archivo', archivo);
    } else if (secuencia_texto) {
      formData.append('secuencia_texto', secuencia_texto);
    }

    return apiClient.post('/cargar_secuencia/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  listarSecuencias: () => apiClient.get('/secuencias/'),

  consultarSecuencia: (idx: number) => apiClient.get(`/secuencia/${idx}`),
};

// Servicio de Análisis
export const analisisService = {
  analizarPLM: (idx: number | string, modelo: string = 'esm2') => {
    const formData = new FormData();
    formData.append('idx_or_id', (idx ?? '').toString());
    formData.append('modelo', modelo);
    return apiClient.post('/analizar_plm/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  simularLaboratorio: (idx: number | string) => {
    const formData = new FormData();
    formData.append('idx_or_id', (idx ?? '').toString());
    return apiClient.post('/simular_laboratorio/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  simularGemelo: (idx: number | string) => {
    const formData = new FormData();
    formData.append('idx_or_id', (idx ?? '').toString());
    return apiClient.post('/simular_gemelo/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

// Servicio de Experimentos
export const experimentosService = {
  listarExperimentos: () => apiClient.get('/experimentos/'),
};

// Servicio de Alertas
export const alertasService = {
  crearAlerta: (usuario: string, mensaje: string) => {
    const formData = new FormData();
    formData.append('usuario', usuario);
    formData.append('mensaje', mensaje);
    return apiClient.post('/alerta/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  listarAlertas: () => apiClient.get('/alertas/'),
};

export default apiClient;
