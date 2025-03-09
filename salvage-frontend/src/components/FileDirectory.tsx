import { useEffect, useState } from 'react';
import { getFiles } from '../api';
import { File } from '../types';

const FileDirectory: React.FC<{ onFileSelect: (file: File) => void }> = ({ onFileSelect }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  useEffect(() => {
    const loadFiles = async () => {
      try {
        const data = await getFiles();
        setFiles(data);
      } catch (error) {
        console.error('Error loading files:', error);
      }
    };
    loadFiles();
  }, []);

  return (
    <div className="space-y-2">
      <h2 className="text-lg font-semibold mb-4 text-neutral-300">Your Files</h2>
      <ul className="space-y-1">
        {files.map((file) => (
          <li
            key={file.id}
            onClick={() => {
              setSelectedId(file.id);
              onFileSelect(file);
            }}
            className={`p-3 rounded-lg cursor-pointer transition-colors ${
              selectedId === file.id 
                ? 'bg-red-500/20 border border-red-500/30' 
                : 'hover:bg-neutral-700/50'
            }`}
          >
            <span className="text-neutral-300">{file.name}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileDirectory;