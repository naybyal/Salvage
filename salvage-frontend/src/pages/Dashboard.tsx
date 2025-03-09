import { useState } from 'react';
import FileDirectory from '../components/FileDirectory';
import CodeEditor from '../components/CodeEditor';
import { File } from '../types';

const Dashboard: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [refreshCount, setRefreshCount] = useState(0);

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    window.location.href = '/login';
  };

  return (
    <div className="h-screen flex flex-col bg-neutral-900 text-white">
      <header className="bg-neutral-800 p-4 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-red-500 rounded-lg"></div>
            <h1 className="text-xl font-bold">Salvage</h1>
          </div>
          <button
            onClick={() => {
              setSelectedFile({
                id: -Date.now(),
                name: `Untitled-${refreshCount + 1}`,
                c_code: '',
                rust_code: '',
                created_at: new Date().toISOString()
              });
              setRefreshCount(c => c + 1);
            }}
            className="px-3 py-1.5 bg-neutral-700 hover:bg-neutral-600 rounded-lg text-sm transition-colors"
          >
            New File
          </button>
        </div>
        <button
          onClick={handleLogout}
          className="px-3 py-1.5 bg-red-600 hover:bg-red-700 rounded-lg text-sm transition-colors"
        >
          Logout
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <div className="w-64 border-r border-neutral-700 p-4">
          <FileDirectory
            onFileSelect={setSelectedFile}
            refresh={refreshCount}
          />
        </div>

        <div className="flex-1 p-4 bg-neutral-800 overflow-auto">
          <CodeEditor
            selectedFile={selectedFile}
            onNewFile={() => setRefreshCount(c => c + 1)}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;