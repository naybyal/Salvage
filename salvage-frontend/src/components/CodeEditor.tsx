import { useState, useEffect } from 'react';
import { transpileCode, saveFile } from '../api';
import Analytics from './Analytics';
import { File } from '../types';

const CodeEditor: React.FC<{
  selectedFile?: File | null;
  onNewFile: () => void;
}> = ({ selectedFile, onNewFile }) => {
  const [activeTab, setActiveTab] = useState<'c' | 'rust'>('c');
  const [cCode, setCCode] = useState('');
  const [rustCode, setRustCode] = useState('');
  const [isTranspiling, setIsTranspiling] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [currentFile, setCurrentFile] = useState<File | null>(null);
  const [isTranspiled, setIsTranspiled] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (selectedFile) {
      setCCode(selectedFile.c_code);
      setRustCode(selectedFile.rust_code || '');
      setCurrentFile(selectedFile);
      setIsTranspiled(!!selectedFile.rust_code);
    }
  }, [selectedFile]);

  const handleTranspile = async () => {
    if (!cCode.trim()) return;
    setIsTranspiling(true);
    try {
      const result = await transpileCode(cCode);
      setRustCode(result);
      setIsTranspiled(true);
      setActiveTab('rust');
    } finally {
      setIsTranspiling(false);
    }
  };

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(rustCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const handleSave = async () => {
    if (!cCode.trim() || !rustCode.trim()) return;

    let fileName = currentFile?.name;
    const isNewFile = !currentFile?.id || currentFile.id < 0;

    if (isNewFile) {
      fileName = prompt('Enter file name:', currentFile?.name || 'new-file');
      if (!fileName) return;
    }

    try {
      const fileData = await saveFile({
        id: currentFile?.id,
        name: fileName!,
        c_code: cCode,
        rust_code: rustCode
      });

      setCurrentFile(fileData);
      onNewFile();

      if (isNewFile) {
        setSelectedFile(fileData);
      }
    } catch (error) {
      alert('Failed to save file');
    }
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <div className="flex justify-between items-center p-4 border-b border-gray-700">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('c')}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
              activeTab === 'c' 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            C Code
          </button>
          {isTranspiled && (
            <button
              onClick={() => setActiveTab('rust')}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                activeTab === 'rust' 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1.5M14 4l2-1.5M6 7l-2 1M4 7l2-1M6 7v2.5M12 21l-2-1.5M12 21l2-1.5M12 21v-5.5M12 13.5V10l-2 1.5" />
              </svg>
              Rust Code
            </button>
          )}
        </div>

        <div className="flex gap-2">
          {isTranspiled && (
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              Analytics
            </button>
          )}
          <button
            onClick={handleTranspile}
            disabled={isTranspiling || !cCode.trim()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50"
          >
            {isTranspiling ? 'Transpiling...' : 'Transpile'}
          </button>
          <button
            onClick={handleSave}
            disabled={!rustCode.trim()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50"
          >
            Save
          </button>
        </div>
      </div>

      <div className="flex-1 relative">
        {activeTab === 'c' ? (
          <textarea
            value={cCode}
            onChange={(e) => setCCode(e.target.value)}
            className="w-full h-full p-6 bg-gray-800/50 resize-none outline-none text-gray-200 font-mono text-sm"
            placeholder="// Enter your C code here..."
          />
        ) : (
          <div className="relative h-full">
            <pre className="w-full h-full p-6 bg-gray-800/50 text-gray-200 font-mono text-sm overflow-auto">
              {rustCode || '// Transpile C code to see Rust equivalent'}
            </pre>
            {rustCode && (
              <button
                onClick={handleCopyCode}
                className="absolute top-4 right-4 p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
              >
                <svg className="w-5 h-5 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
            )}
          </div>
        )}
      </div>

      {showAnalytics && <Analytics cCode={cCode} rustCode={rustCode} />}
    </div>
  );
};

export default CodeEditor;