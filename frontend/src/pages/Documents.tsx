import { useState, useEffect, useRef } from 'react';
import { Upload, Trash2, Search } from 'lucide-react';
import { getDocuments, uploadDocumentWithProgress, deleteDocument } from '../services/api';
import { Document } from '../types';

const Documents = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({});
  const [filterType, setFilterType] = useState<string>('all');
  const dropRef = useRef<HTMLDivElement | null>(null);

  const fetchDocuments = async () => {
    const docs = await getDocuments();
    setDocuments(docs);
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    await uploadFile(file);
  };

  const uploadFile = async (file: File) => {
    const allowed = ['.pdf', '.docx', '.txt'];
    const maxBytes = 20 * 1024 * 1024; // 20 MB
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowed.includes(ext)) {
      alert(`Unsupported file type: ${ext}\nOnly PDF, DOCX, and TXT files are supported.`);
      return;
    }

    if (file.size > maxBytes) {
      alert('File too large (max 20 MB)');
      return;
    }

    setUploading(true);
    setUploadProgress(prev => ({ ...prev, [file.name]: 0 }));

    try {
      console.log('Starting upload:', file.name);
      await uploadDocumentWithProgress(file, (percent) => {
        console.log('Upload progress:', percent);
        setUploadProgress(prev => ({ ...prev, [file.name]: percent }));
      });

      console.log('Upload successful');
      setTimeout(() => setUploadProgress(prev => {
        const copy = { ...prev };
        delete copy[file.name];
        return copy;
      }), 1200);

      await fetchDocuments();
      alert('Document uploaded successfully!');
    } catch (error: any) {
      console.error('Upload failed:', error);
      const errorMsg = error?.response?.data?.detail || error?.message || 'Upload failed';
      alert(`Upload failed: ${errorMsg}`);
      setUploadProgress(prev => {
        const copy = { ...prev };
        delete copy[file.name];
        return copy;
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename: string) => {
    if (!confirm(`Delete ${filename}?`)) return;
    await deleteDocument(filename);
    await fetchDocuments();
  };

  const filteredDocs = documents
    .filter(doc => doc.filename.toLowerCase().includes(searchTerm.toLowerCase()))
    .filter(doc => {
      if (filterType === 'all') return true;
      return doc.filename.toLowerCase().endsWith(filterType);
    });

  // Drag & drop handlers
  useEffect(() => {
    const el = dropRef.current;
    if (!el) return;

    const onDragOver = (e: DragEvent) => {
      e.preventDefault();
      el.classList.add('bg-gray-50');
    };

    const onDragLeave = () => el.classList.remove('bg-gray-50');

    const onDrop = (e: DragEvent) => {
      e.preventDefault();
      el.classList.remove('bg-gray-50');
      const file = e.dataTransfer?.files?.[0];
      if (file) uploadFile(file);
    };

    el.addEventListener('dragover', onDragOver as any);
    el.addEventListener('dragleave', onDragLeave as any);
    el.addEventListener('drop', onDrop as any);

    return () => {
      el.removeEventListener('dragover', onDragOver as any);
      el.removeEventListener('dragleave', onDragLeave as any);
      el.removeEventListener('drop', onDrop as any);
    };
  }, [dropRef.current]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Documents</h1>
        <div className="flex items-center gap-3">
          <label className="bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-700 flex items-center">
            <Upload className="w-5 h-5 mr-2" />
            {uploading ? 'Uploading...' : 'Upload Document'}
            <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.docx,.txt" disabled={uploading} />
          </label>

          <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="px-3 py-2 border rounded">
            <option value="all">All</option>
            <option value=".pdf">PDF</option>
            <option value=".docx">DOCX</option>
            <option value=".txt">TXT</option>
          </select>
        </div>
      </div>

      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search documents..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div ref={dropRef} className="mt-4 p-4 border-2 border-dashed rounded text-center text-sm text-gray-500">
          Drag & drop files here to upload (PDF, DOCX, TXT only)
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {filteredDocs.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No documents uploaded yet.</p>
            <p className="text-sm mt-2">Upload a PDF, DOCX, or TXT file to get started.</p>
          </div>
        ) : (
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Chunks</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Uploaded</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredDocs.map((doc) => {
                const fileSize = doc.file_path ? 'N/A' : 'N/A';
                const fileType = doc.filename.substring(doc.filename.lastIndexOf('.')).toUpperCase();
                
                return (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                          {uploadProgress[doc.filename] != null && (
                            <div className="w-40 mt-2 bg-gray-200 rounded overflow-hidden h-2">
                              <div 
                                className="bg-green-500 h-full transition-all duration-300" 
                                style={{ width: `${uploadProgress[doc.filename]}%` }} 
                              />
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        <div>Type: <span className="font-medium">{fileType}</span></div>
                        <div className="text-xs text-gray-500 mt-1">ID: {doc.id}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {doc.chunk_count} chunks
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {new Date(doc.uploaded_at).toLocaleDateString()}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(doc.uploaded_at).toLocaleTimeString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleDelete(doc.filename)}
                        className="text-red-600 hover:text-red-900 flex items-center gap-1"
                        title="Delete document"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Documents;
