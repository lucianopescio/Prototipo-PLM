import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Database, Edit, Trash2, Download, Upload, CheckCircle, Clock } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { toast } from 'sonner';

export function DatasetManagement() {
  const [datasets, setDatasets] = useState([
    { 
      id: 1, 
      name: 'Protein_Kinases_2024', 
      version: 'v1.2', 
      records: 1250, 
      size: '24.5 MB', 
      status: 'Curado',
      lastModified: '2025-11-05',
      format: 'FAIR',
      source: 'UniProt'
    },
    { 
      id: 2, 
      name: 'Antibody_Sequences', 
      version: 'v2.0', 
      records: 856, 
      size: '18.2 MB', 
      status: 'En revisión',
      lastModified: '2025-11-06',
      format: 'FAIR',
      source: 'PDB'
    },
    { 
      id: 3, 
      name: 'P53_Variants', 
      version: 'v1.0', 
      records: 342, 
      size: '8.7 MB', 
      status: 'Curado',
      lastModified: '2025-11-04',
      format: 'FAIR',
      source: 'Manual'
    },
  ]);

  const handleExport = (datasetName: string) => {
    try {
      // Crear datos CSV simulados
      const csvData = `nombre,version,registros,tamaño,estado,ultima_modificacion,formato,fuente
${datasets.find(d => d.name === datasetName)?.name || datasetName},v1.0,1000,15MB,Curado,${new Date().toISOString().slice(0, 10)},FAIR,Exportado
Secuencia_001,Proteína A,MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG,PLM_Predicted,${new Date().toISOString()}
Secuencia_002,Proteína B,MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFPQVFQMQADAVPKCFAGAVTTDPLDMHGDTPECNCGDNGQTTQQRGSLLCTCGPGKDNFTTNDDGFLDNLGHGISNVMTGGDDPEGNEELLKLMAGGVGGHISGCNQSSVTMRVGGPRSDLLRPDTSGFESMVVDPSDSAAPNRRPSPTQFNGSMDLSIQGYGKDYDTQAKGVLSIQMTTLGSLHHCAISPKPIGSVHDWVWKPECWDGQNFGQDSYVQNPLLLTGKIPRSRLPKSLR,Lab_Validated,${new Date().toISOString()}
Secuencia_003,Proteína C,ATGAGCGATAAATTGTTGATGCTCAAACCTGCAGAAGATGGTTATGTCATGAGCGATTTTACCTCTGGCTGGTATGAGCGATTTTACCTC,Twin_Simulated,${new Date().toISOString()}`;

      // Crear y descargar archivo
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.href = url;
      link.download = `${datasetName}_export_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast.success(`Dataset ${datasetName} exportado exitosamente`, {
        description: 'El archivo CSV se ha descargado correctamente'
      });
    } catch (error) {
      toast.error('Error al exportar dataset', {
        description: 'No se pudo completar la descarga'
      });
    }
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.fasta,.txt';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        toast.success(`Importando ${file.name}`, {
          description: 'Procesando archivo...'
        });
        // Simular procesamiento
        setTimeout(() => {
          const newDataset = {
            id: datasets.length + 1,
            name: file.name.replace(/\.[^/.]+$/, ''),
            version: 'v1.0',
            records: Math.floor(Math.random() * 1000) + 100,
            size: `${(file.size / (1024*1024)).toFixed(1)} MB`,
            status: 'En revisión',
            lastModified: new Date().toISOString().split('T')[0],
            format: 'FAIR',
            source: 'Importado'
          };
          setDatasets([...datasets, newDataset]);
          toast.success('Dataset importado exitosamente');
        }, 2000);
      }
    };
    input.click();
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Gestión de Datasets</h1>
          <p className="text-gray-600">Curación, estandarización y control de calidad (HU-006, HU-012, HU-014)</p>
        </div>
        <Button onClick={handleImport}>
          <Upload className="mr-2 h-4 w-4" />
          Importar Dataset
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Datasets</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl">156</div>
            <p className="text-xs text-gray-600 mt-1">2.4 GB de datos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Curados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-green-600">124</div>
            <p className="text-xs text-gray-600 mt-1">79.5% del total</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">En Revisión</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-yellow-600">28</div>
            <p className="text-xs text-gray-600 mt-1">Requieren atención</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Cumplimiento FAIR</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-blue-600">98%</div>
            <p className="text-xs text-gray-600 mt-1">Estándares cumplidos</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Table */}
      <Card>
        <CardHeader>
          <CardTitle>Datasets Registrados</CardTitle>
          <CardDescription>Administra versiones, metadatos y control de calidad</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input placeholder="Buscar datasets..." className="max-w-sm" />
          </div>
          
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Versión</TableHead>
                <TableHead>Registros</TableHead>
                <TableHead>Tamaño</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Última Modificación</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {datasets.map((dataset) => (
                <TableRow key={dataset.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Database className="h-4 w-4 text-blue-600" />
                      <div>
                        <p>{dataset.name}</p>
                        <p className="text-xs text-gray-600">{dataset.source}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{dataset.version}</Badge>
                  </TableCell>
                  <TableCell>{dataset.records.toLocaleString()}</TableCell>
                  <TableCell>{dataset.size}</TableCell>
                  <TableCell>
                    <Badge variant={dataset.status === 'Curado' ? 'default' : 'secondary'}>
                      {dataset.status === 'Curado' ? (
                        <CheckCircle className="mr-1 h-3 w-3" />
                      ) : (
                        <Clock className="mr-1 h-3 w-3" />
                      )}
                      {dataset.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{dataset.lastModified}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Editar Dataset: {dataset.name}</DialogTitle>
                            <DialogDescription>Actualiza metadatos y configuración</DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 mt-4">
                            <div>
                              <Label htmlFor="dataset-name">Nombre</Label>
                              <Input id="dataset-name" defaultValue={dataset.name} />
                            </div>
                            <div>
                              <Label htmlFor="dataset-version">Versión</Label>
                              <Input id="dataset-version" defaultValue={dataset.version} />
                            </div>
                            <div>
                              <Label htmlFor="dataset-description">Descripción</Label>
                              <Textarea 
                                id="dataset-description" 
                                placeholder="Describe el contenido y propósito del dataset..."
                                rows={3}
                              />
                            </div>
                            <div>
                              <Label htmlFor="dataset-license">Licencia</Label>
                              <Input id="dataset-license" placeholder="Ej: CC BY 4.0" />
                            </div>
                            <Button className="w-full">Guardar Cambios</Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                      
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => handleExport(dataset.name)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* FAIR Principles Card */}
      <Card>
        <CardHeader>
          <CardTitle>Cumplimiento de Principios FAIR</CardTitle>
          <CardDescription>Findable, Accessible, Interoperable, Reusable</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p>Findable</p>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <p className="text-xs text-gray-600">Metadatos completos y identificadores únicos</p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p>Accessible</p>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <p className="text-xs text-gray-600">Protocolos estándar de acceso</p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p>Interoperable</p>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <p className="text-xs text-gray-600">Formatos compatibles (CSV, FASTA)</p>
            </div>
            
            <div className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p>Reusable</p>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <p className="text-xs text-gray-600">Licencias y proveniencia clara</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
