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

  // Load from localStorage on initial load
  useEffect(() => {
    const savedState = localStorage.getItem('currentFile');
    if (savedState) {
      const { c, rust } = JSON.parse(savedState);
      setCCode(c);
      setRustCode(rust);
    }
  }, []);

  // Persist to localStorage on change
  useEffect(() => {
    localStorage.setItem('currentFile', JSON.stringify({
      c: cCode,
      rust: rustCode
    }));
  }, [cCode, rustCode]);

  useEffect(() => {
    if (selectedFile) {
      setCCode(selectedFile.c_code);
      setRustCode(selectedFile.rust_code || '');
      setCurrentFile(selectedFile);
      setIsTranspiled(!!selectedFile.rust_code);

      // Update localStorage with selected file
      localStorage.setItem('currentFile', JSON.stringify({
        c: selectedFile.c_code,
        rust: selectedFile.rust_code || ''
      }));
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

      // Auto-save after successful transpilation
      if (currentFile?.id) {
        await handleSave();
      }
    } finally {
      setIsTranspiling(false);
    }
  };

  const handleCopyCode = async () => {
    try {
      await navigator.clipboard.writeText(rustCode);
      alert('Code copied to clipboard!');
    } catch (err) {
      alert('Failed to copy code');
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
      alert('File saved successfully!');
    } catch (error) {
      alert('Failed to save file');
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-6 gap-4">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('c')}
            className={`px-3 py-1.5 rounded-lg text-sm ${
              activeTab === 'c' 
                ? 'bg-red-600 hover:bg-red-700' 
                : 'bg-neutral-700 hover:bg-neutral-600'
            }`}
          >
            C Code
          </button>
          {isTranspiled && (
            <button
              onClick={() => setActiveTab('rust')}
              className={`px-3 py-1.5 rounded-lg text-sm ${
                activeTab === 'rust' 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-neutral-700 hover:bg-neutral-600'
              }`}
            >
              Rust Code
            </button>
          )}
        </div>

        <div className="flex gap-2">
          {isTranspiled && (
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                showAnalytics ? 'bg-red-700' : 'bg-red-600 hover:bg-red-700'
              }`}
            >
              Analytics
            </button>
          )}
          <button
            onClick={handleTranspile}
            disabled={isTranspiling || !cCode.trim()}
            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 rounded-lg text-sm disabled:opacity-50 transition-colors"
          >
            {isTranspiling ? 'Transpiling...' : 'Transpile'}
          </button>
          <button
            onClick={handleSave}
            disabled={!rustCode.trim()}
            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 rounded-lg text-sm disabled:opacity-50 transition-colors"
          >
            Save
          </button>
        </div>
      </div>

      <div className="flex-1 bg-neutral-700/30 rounded-lg border border-neutral-600 overflow-hidden relative">
        {activeTab === 'c' ? (
          <textarea
            value={cCode}
            onChange={(e) => setCCode(e.target.value)}
            className="w-full h-full p-4 bg-transparent resize-none outline-none text-neutral-200 font-mono text-sm"
            placeholder="// Enter your C code here..."
          />
        ) : (
          <div className="relative h-full">
            <pre className="w-full h-full p-4 overflow-auto bg-transparent text-neutral-200 font-mono text-sm">
              {rustCode || '// Transpile C code to see Rust equivalent'}
            </pre>
            {rustCode && (
              <button
                onClick={handleCopyCode}
                className="absolute right-2 top-2 p-1.5 bg-neutral-800 rounded-lg hover:bg-neutral-700 transition-colors"
                title="Copy code"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 text-neutral-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
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