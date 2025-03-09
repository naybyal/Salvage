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
    <div className="space-y-2">
      <h2 className="text-lg font-semibold mb-4 text-neutral-300">Your Files</h2>
      <ul className="space-y-1">
        {files.map((file) => (
          <li
            key={file.id}
            className={`group relative flex items-center p-2 rounded-lg cursor-pointer transition-colors text-sm ${
              selectedId === file.id 
                ? 'bg-red-500/20 border border-red-500/30' 
                : 'hover:bg-neutral-700/50'
            }`}
          >
            <span
              className="text-neutral-300 flex-1"
              onClick={() => {
                setSelectedId(file.id);
                onFileSelect(file);
              }}
            >
              {file.name}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(file.id);
              }}
              className="ml-2 text-red-400 hover:text-red-300 opacity-70 hover:opacity-100 transition-opacity"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileDirectory;