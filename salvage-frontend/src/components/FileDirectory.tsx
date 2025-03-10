import { useEffect, useState } from 'react';
import { getFiles, deleteFile } from '../api';
import { File } from '../types';

const FileDirectory: React.FC<{
  onFileSelect: (file: File) => void;
  refresh: number;
}> = ({ onFileSelect, refresh }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    const loadFiles = async () => {
      try {
        const data = await getFiles();
        setFiles(data.filter(f => f.id > 0));
      } catch (error) {
        console.error('Error loading files:', error);
      }
    };
    loadFiles();
  }, [refresh]);

  const handleDelete = async (fileId: number) => {
    if (window.confirm('Are you sure you want to delete this file?')) {
      try {
        await deleteFile(fileId);
        setFiles(files.filter(f => f.id !== fileId));
      } catch (error) {
        alert('Failed to delete file');
      }
    }
  };

  return (
    <div className="space-y-2 h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-red-400">Workspace</h2>
        <span className="text-sm text-gray-400">{files.length} files</span>
      </div>
      <ul className="space-y-1 flex-1 overflow-y-auto">
        {files.map((file) => (
          <li
            key={file.id}
            className={`group flex items-center justify-between p-2 rounded-md transition-colors
              ${selectedId === file.id 
                ? 'bg-red-600/20 border border-red-500/30'
                : 'hover:bg-gray-700/30 border border-transparent'}
              cursor-pointer`}
            onClick={() => {
              setSelectedId(file.id);
              onFileSelect(file);
            }}
          >
            <div className="flex items-center gap-3 truncate">
              <div className="w-5 h-5 bg-red-600/20 rounded-sm flex items-center justify-center">
                <svg className="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <span className="text-gray-200 text-sm truncate">{file.name}</span>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(file.id);
              }}
              className="p-1 hover:bg-red-600/20 rounded-md text-gray-400 hover:text-red-300 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileDirectory;