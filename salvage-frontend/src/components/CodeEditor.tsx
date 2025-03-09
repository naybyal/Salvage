import { useState } from 'react';
import { transpileCode } from '../api';
import Analytics from './Analytics';
import { File } from '../types';

const CodeEditor: React.FC<{ selectedFile?: File | null }> = ({ selectedFile }) => {
  const [cCode, setCCode] = useState(selectedFile?.c_code || '');
  const [rustCode, setRustCode] = useState(selectedFile?.rust_code || '');
  const [isTranspiling, setIsTranspiling] = useState(false);

  const handleTranspile = async () => {
    if (!cCode.trim()) return;
    setIsTranspiling(true);
    try {
      const result = await transpileCode(cCode);
      setRustCode(result);
    } finally {
      setIsTranspiling(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-neutral-300">Code Editor</h2>
        <button
          onClick={handleTranspile}
          disabled={isTranspiling || !cCode.trim()}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50 transition-colors"
        >
          {isTranspiling ? 'Transpiling...' : 'Transpile to Rust'}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 flex-1">
        <div className="h-full flex flex-col">
          <label className="text-sm font-medium mb-2 text-neutral-400">C Code</label>
          <textarea
            value={cCode}
            onChange={(e) => setCCode(e.target.value)}
            className="w-full h-full p-4 bg-neutral-700/30 rounded-lg border border-neutral-600 focus:border-red-500 focus:ring-2 focus:ring-red-500/20 outline-none resize-none text-neutral-200"
          />
        </div>

        <div className="h-full flex flex-col">
          <label className="text-sm font-medium mb-2 text-neutral-400">Rust Code</label>
          <pre className="w-full h-full p-4 bg-neutral-700/30 rounded-lg border border-neutral-600 overflow-auto text-neutral-200">
            {rustCode}
          </pre>
        </div>
      </div>

      {rustCode && <Analytics cCode={cCode} rustCode={rustCode} />}
    </div>
  );
};

export default CodeEditor;