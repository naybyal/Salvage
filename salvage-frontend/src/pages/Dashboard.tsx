import { useState } from 'react';
import CodeEditor from '../components/CodeEditor';
import FileDirectory from '../components/FileDirectory';
import { File } from '../types';

const Dashboard: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login';
  };

  return (
    <div className="h-screen flex flex-col bg-neutral-900 text-white">
      <header className="bg-neutral-800 p-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-red-500 rounded-lg"></div>
          <h1 className="text-xl font-bold">Salvage</h1>
        </div>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
        >
          Logout
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <div className="w-64 border-r border-neutral-700 p-4">
          <FileDirectory onFileSelect={setSelectedFile} />
        </div>

        <div className="flex-1 p-4 bg-neutral-800 overflow-auto">
          <CodeEditor selectedFile={selectedFile} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;