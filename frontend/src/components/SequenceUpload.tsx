import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { Upload, FileText, Database as DatabaseIcon, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import axios from 'axios';

interface SequenceUploadProps {
  token: string | null;
}

interface Sequence {
  id: number;
  nombre: string;
  fuente: string;
  secuencia: string;
  formato: string;
  fecha_carga: string;
  longitud: number;
}

export function SequenceUpload({ token }: SequenceUploadProps) {
  const [uploadMethod, setUploadMethod] = useState<'file' | 'database' | 'manual'>('file');
  const [uploadedSequences, setUploadedSequences] = useState<Sequence[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    fuente: 'Manual',
    secuencia_texto: '',
    source: 'manual'
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Cargar secuencias al montar el componente
  useEffect(() => {
    cargarSecuencias();
  }, [token]);

  const cargarSecuencias = async () => {
    try {
      const response = await axios.get(`${API_URL}/secuencias/`);
      if (response.data.secuencias) {
        setUploadedSequences(response.data.secuencias);
      }
    } catch (error) {
      console.error('Error al cargar secuencias:', error);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const content = event.target?.result as string;
        await enviarSecuencia(formData.nombre || file.name, formData.fuente, content, file);
      };
      reader.readAsText(file);
    }
  };

  const handleManualSubmit = async () => {
    if (!formData.nombre || !formData.secuencia_texto) {
      toast.error('Por favor completa nombre y secuencia');
      return;
    }
    await enviarSecuencia(formData.nombre, formData.fuente, formData.secuencia_texto);
  };

  const enviarSecuencia = async (nombre: string, fuente: string, secuencia?: string, archivo?: File) => {
    setIsLoading(true);
    try {
      const data = new FormData();
      data.append('nombre', nombre);
      data.append('fuente', fuente);
      
      if (archivo) {
        data.append('archivo', archivo);
      } else if (secuencia) {
        data.append('secuencia_texto', secuencia);
      }

      const response = await axios.post(`${API_URL}/cargar_secuencia/`, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      if (response.data.registro) {
        toast.success(`Secuencia "${nombre}" cargada correctamente`);
        setUploadedSequences([...uploadedSequences, response.data.registro]);
        setFormData({ nombre: '', fuente: 'Manual', secuencia_texto: '', source: 'manual' });
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Error al cargar secuencia';
      toast.error(message);
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDatabaseImport = () => {
    toast.info('Importación desde bases de datos públicas', {
      description: 'Funcionalidad en desarrollo...'
    });
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1>Carga de Secuencias Proteicas</h1>
        <p className="text-gray-600">Importa secuencias desde diferentes fuentes para análisis (HU-001)</p>
      </div>

      {/* Upload Methods */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card 
          className={`cursor-pointer transition-all ${uploadMethod === 'file' ? 'ring-2 ring-blue-500' : ''}`}
          onClick={() => setUploadMethod('file')}
        >
          <CardHeader>
            <FileText className="h-8 w-8 text-blue-600 mb-2" />
            <CardTitle className="text-base">Cargar Archivo</CardTitle>
            <CardDescription>FASTA, CSV, PDB</CardDescription>
          </CardHeader>
        </Card>

        <Card 
          className={`cursor-pointer transition-all ${uploadMethod === 'database' ? 'ring-2 ring-blue-500' : ''}`}
          onClick={() => setUploadMethod('database')}
        >
          <CardHeader>
            <DatabaseIcon className="h-8 w-8 text-purple-600 mb-2" />
            <CardTitle className="text-base">Base de Datos</CardTitle>
            <CardDescription>UniProt, PDB, NCBI</CardDescription>
          </CardHeader>
        </Card>

        <Card 
          className={`cursor-pointer transition-all ${uploadMethod === 'manual' ? 'ring-2 ring-blue-500' : ''}`}
          onClick={() => setUploadMethod('manual')}
        >
          <CardHeader>
            <Upload className="h-8 w-8 text-green-600 mb-2" />
            <CardTitle className="text-base">Entrada Manual</CardTitle>
            <CardDescription>Pegar secuencia</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Upload Form */}
      <Card>
        <CardHeader>
          <CardTitle>
            {uploadMethod === 'file' && 'Cargar desde Archivo'}
            {uploadMethod === 'database' && 'Importar desde Base de Datos'}
            {uploadMethod === 'manual' && 'Entrada Manual de Secuencia'}
          </CardTitle>
          <CardDescription>
            {uploadMethod === 'file' && 'Soporta formatos: .fasta, .csv, .pdb, .txt'}
            {uploadMethod === 'database' && 'Conecta con bases de datos públicas de proteínas'}
            {uploadMethod === 'manual' && 'Ingresa la secuencia en formato FASTA'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {uploadMethod === 'file' && (
            <>
              <div>
                <Label htmlFor="file-name">Nombre de la Carga</Label>
                <Input 
                  id="file-name" 
                  placeholder="Nombre descriptivo"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  disabled={isLoading}
                />
              </div>
              <div>
                <Label htmlFor="file-upload">Seleccionar Archivo</Label>
                <Input 
                  id="file-upload" 
                  type="file" 
                  accept=".fasta,.csv,.pdb,.txt"
                  onChange={handleFileUpload}
                  className="mt-1"
                  disabled={isLoading}
                />
              </div>
              <div>
                <Label htmlFor="source">Fuente de Origen</Label>
                <Select value={formData.fuente} onValueChange={(val) => setFormData({ ...formData, fuente: val })}>
                  <SelectTrigger id="source" disabled={isLoading}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Manual">Carga Manual</SelectItem>
                    <SelectItem value="UniProt">UniProt</SelectItem>
                    <SelectItem value="PDB">Protein Data Bank</SelectItem>
                    <SelectItem value="NCBI">NCBI</SelectItem>
                    <SelectItem value="Otra">Otra</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </>
          )}

          {uploadMethod === 'database' && (
            <>
              <div>
                <Label htmlFor="database-source">Base de Datos</Label>
                <Select defaultValue="uniprot">
                  <SelectTrigger id="database-source" disabled={isLoading}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="uniprot">UniProt</SelectItem>
                    <SelectItem value="pdb">Protein Data Bank (PDB)</SelectItem>
                    <SelectItem value="ncbi">NCBI Protein</SelectItem>
                    <SelectItem value="pfam">Pfam</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="protein-id">ID de Proteína</Label>
                <Input 
                  id="protein-id" 
                  placeholder="Ej: P04637 (P53_HUMAN)"
                  disabled={isLoading}
                />
              </div>
              <Button onClick={handleDatabaseImport} disabled={isLoading}>
                <DatabaseIcon className="mr-2 h-4 w-4" />
                Importar Secuencia
              </Button>
            </>
          )}

          {uploadMethod === 'manual' && (
            <>
              <div>
                <Label htmlFor="sequence-name">Nombre de la Secuencia</Label>
                <Input 
                  id="sequence-name" 
                  placeholder="Ej: Protein_P53_mutant"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  disabled={isLoading}
                />
              </div>
              <div>
                <Label htmlFor="source-manual">Fuente</Label>
                <Select value={formData.fuente} onValueChange={(val) => setFormData({ ...formData, fuente: val })}>
                  <SelectTrigger id="source-manual" disabled={isLoading}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Manual">Manual</SelectItem>
                    <SelectItem value="UniProt">UniProt</SelectItem>
                    <SelectItem value="PDB">PDB</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="sequence-text">Secuencia (Formato FASTA)</Label>
                <Textarea 
                  id="sequence-text" 
                  placeholder=">sp|P04637|P53_HUMAN&#10;MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDD&#10;IEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSV..."
                  rows={8}
                  value={formData.secuencia_texto}
                  onChange={(e) => setFormData({ ...formData, secuencia_texto: e.target.value })}
                  disabled={isLoading}
                />
              </div>
              <Button onClick={handleManualSubmit} disabled={isLoading}>
                <CheckCircle className="mr-2 h-4 w-4" />
                {isLoading ? 'Cargando...' : 'Validar y Guardar'}
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {/* Uploaded Sequences Table */}
      <Card>
        <CardHeader>
          <CardTitle>Secuencias Cargadas ({uploadedSequences.length})</CardTitle>
          <CardDescription>Historial de secuencias importadas al sistema</CardDescription>
        </CardHeader>
        <CardContent>
          {uploadedSequences.length === 0 ? (
            <p className="text-gray-500">No hay secuencias cargadas aún</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Fuente</TableHead>
                  <TableHead>Longitud</TableHead>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Formato</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {uploadedSequences.map((seq) => (
                  <TableRow key={seq.id}>
                    <TableCell>{seq.nombre}</TableCell>
                    <TableCell>{seq.fuente}</TableCell>
                    <TableCell>{seq.longitud} aa</TableCell>
                    <TableCell>{new Date(seq.fecha_carga).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{seq.formato}</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
