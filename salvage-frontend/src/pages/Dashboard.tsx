import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import FileDirectory from '../components/FileDirectory';
import CodeEditor from '../components/CodeEditor';
import { File } from '../types';

const Dashboard: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [refreshCount, setRefreshCount] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access');
      if (!token) navigate('/login');
    };
    checkAuth();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    navigate('/login');
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="md:hidden p-2 hover:bg-gray-700 rounded-lg"
          >
            <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isSidebarOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h1 className="text-xl font-bold text-red-400">SALVAGE</h1>
          </div>
        </div>

        <div className="flex items-center gap-4">
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
            className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-md text-sm transition-colors"
          >
            <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <span>New File</span>
          </button>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 rounded-md text-sm flex items-center gap-2 transition-colors"
          >
            <svg className="w-4 h-4 text-red-100" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span className="hidden md:inline">Logout</span>
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Mobile Overlay */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-20 md:hidden"
            onClick={() => setIsSidebarOpen(false)}
          ></div>
        )}

        {/* Sidebar */}
        <div
          className={`fixed md:relative z-30 h-full w-64 bg-gray-800 border-r border-gray-700 transform transition-transform duration-300 ease-in-out
            ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0`}
        >
          <div className="p-4 h-full flex flex-col">
            <div className="md:hidden flex justify-end mb-2">
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="p-1 text-gray-400 hover:text-red-400"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <FileDirectory
              onFileSelect={(file) => {
                setSelectedFile(file);
                setIsSidebarOpen(false);
              }}
              refresh={refreshCount}
            />
          </div>
        </div>

        {/* Main Content */}
        <div className={`flex-1 bg-gray-900 overflow-auto transition-all duration-300 ${
          isSidebarOpen ? 'ml-64 md:ml-0' : 'ml-0'
        }`}>
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