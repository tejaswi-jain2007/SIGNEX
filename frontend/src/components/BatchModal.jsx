import React, { useState } from 'react';
import { X, Play, Trash2, Plus, CheckCircle, AlertCircle, RefreshCw, FileText } from 'lucide-react';

export default function BatchModal({
  isOpen,
  onClose,
  batchQueue = [],
  onClearQueue,
  onRemoveItem,
  onRunBatchItem,
  presetSamples = [],
  onAddToQueue,
  theme = 'dark'
}) {
  if (!isOpen) return null;

  const [isProcessing, setIsProcessing] = useState(false);
  const [currentIdx, setCurrentIdx] = useState(-1);
  const [batchResults, setBatchResults] = useState([]);
  const [selectedPresetToAdd, setSelectedPresetToAdd] = useState('');

  const isDark = theme === 'dark';

  const handleStartBatch = async () => {
    if (batchQueue.length === 0 || isProcessing) return;
    setIsProcessing(true);
    setBatchResults([]);

    const results = [];
    for (let i = 0; i < batchQueue.length; i++) {
      setCurrentIdx(i);
      const item = batchQueue[i];

      try {
        const formData = new FormData();
        if (item.file) {
          formData.append('file', item.file);
        } else if (item.presetFilename) {
          formData.append('preset_filename', item.presetFilename);
        }

        const apiBase = (import.meta.env.VITE_API_URL || 'https://signex-backend.onrender.com').replace(/\/+$/, '');
        const response = await fetch(`${apiBase}/api/analyze`, {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('Analysis failed');
        }

        const resData = await response.json();
        results.push({
          filename: item.displayName || item.file?.name || item.presetFilename,
          status: 'SUCCESS',
          modulation: resData.classification?.predicted_class || 'UNKNOWN',
          confidence: ((resData.classification?.confidence || 0) * 100).toFixed(1) + '%',
          snr: `${(resData.parameters?.snr_db || 0).toFixed(2)} dB`,
          pdfUrl: resData.downloads?.pdf
        });
      } catch (err) {
        results.push({
          filename: item.displayName || item.file?.name || item.presetFilename,
          status: 'FAILED',
          modulation: 'ERR',
          confidence: '0.0%',
          snr: 'N/A',
          pdfUrl: null
        });
      }
      setBatchResults([...results]);
    }

    setIsProcessing(false);
    setCurrentIdx(-1);
  };

  const handleAddPreset = () => {
    if (!selectedPresetToAdd) return;
    onAddToQueue({
      presetFilename: selectedPresetToAdd,
      displayName: selectedPresetToAdd
    });
    setSelectedPresetToAdd('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div
        className={`w-full max-w-2xl rounded-xl border shadow-2xl p-6 relative flex flex-col max-h-[85vh] ${
          isDark
            ? 'bg-[#0B1325] border-[#1E293B] text-[#E2E8F0]'
            : 'bg-[#FFFFFF] border-[#CBD5E0] text-[#1E293B]'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-inherit">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider font-mono">
              BATCH PROCESSING QUEUE
            </h3>
            <p className="text-[11px] text-slate-400 font-mono">
              {batchQueue.length} files currently queued for sequential execution.
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="p-1 rounded hover:bg-slate-700/30 text-slate-400 hover:text-white transition disabled:opacity-40"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Add Bar */}
        <div className="flex items-center space-x-2 my-3">
          <select
            value={selectedPresetToAdd}
            onChange={(e) => setSelectedPresetToAdd(e.target.value)}
            disabled={isProcessing}
            className={`flex-1 px-3 py-1.5 rounded border text-xs font-mono focus:outline-none ${
              isDark ? 'bg-[#1E293B] border-[#334155] text-white' : 'bg-[#F1F5F9] border-[#CBD5E0] text-black'
            }`}
          >
            <option value="">-- Select Test Capture to Add --</option>
            {presetSamples.map((s) => (
              <option key={s.filename} value={s.filename}>
                [{s.modulation}] {s.filename}
              </option>
            ))}
          </select>
          <button
            onClick={handleAddPreset}
            disabled={!selectedPresetToAdd || isProcessing}
            className="px-3 py-1.5 rounded bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-bold font-mono flex items-center gap-1 transition disabled:opacity-40"
          >
            <Plus className="w-4 h-4" /> Add
          </button>
          <button
            onClick={onClearQueue}
            disabled={batchQueue.length === 0 || isProcessing}
            className="px-3 py-1.5 rounded bg-rose-950/40 hover:bg-rose-900 border border-rose-500/30 text-rose-300 text-xs font-bold font-mono flex items-center gap-1 transition disabled:opacity-40"
          >
            <Trash2 className="w-4 h-4" /> Clear
          </button>
        </div>

        {/* Queue & Results List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1 my-2">
          {batchQueue.length === 0 ? (
            <div className="text-center py-10 text-xs font-mono text-slate-500">
              Queue is empty. Select preset files or add captures to batch process.
            </div>
          ) : (
            batchQueue.map((item, idx) => {
              const res = batchResults[idx];
              const isCurrent = idx === currentIdx;

              return (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border text-xs font-mono flex items-center justify-between transition ${
                    isCurrent
                      ? 'border-[#38BDF8] bg-[#0284C7]/15'
                      : res?.status === 'SUCCESS'
                      ? 'border-emerald-500/40 bg-emerald-950/20'
                      : res?.status === 'FAILED'
                      ? 'border-rose-500/40 bg-rose-950/20'
                      : isDark
                      ? 'bg-[#0F172A] border-[#1E293B]'
                      : 'bg-[#F8FAFC] border-[#CBD5E0]'
                  }`}
                >
                  <div className="flex items-center space-x-3 truncate">
                    <span className="text-slate-500 font-bold">#{idx + 1}</span>
                    <span className="font-bold truncate text-white">
                      {item.displayName || item.file?.name || item.presetFilename}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 shrink-0">
                    {isCurrent ? (
                      <span className="flex items-center gap-1 text-[#38BDF8] font-bold animate-pulse">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Processing...
                      </span>
                    ) : res ? (
                      <div className="flex items-center space-x-3">
                        <span className="text-emerald-400 font-bold">
                          {res.modulation} ({res.confidence})
                        </span>
                        <span className="text-slate-400">{res.snr}</span>
                        {res.pdfUrl && (
                          <a
                            href={`http://127.0.0.1:8000${res.pdfUrl}`}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[#38BDF8] hover:underline flex items-center gap-0.5"
                          >
                            <FileText className="w-3 h-3" /> PDF
                          </a>
                        )}
                      </div>
                    ) : (
                      <button
                        onClick={() => onRemoveItem(idx)}
                        disabled={isProcessing}
                        className="text-slate-500 hover:text-rose-400 p-1"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Actions */}
        <div className="pt-3 border-t border-inherit flex items-center justify-between">
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="px-4 py-1.5 rounded bg-slate-700/30 hover:bg-slate-700 text-xs font-mono transition disabled:opacity-40"
          >
            Close
          </button>

          <button
            onClick={handleStartBatch}
            disabled={batchQueue.length === 0 || isProcessing}
            className="px-5 py-2 rounded bg-gradient-to-r from-[#0284C7] to-[#0369A1] hover:from-[#38BDF8] hover:to-[#0284C7] text-white text-xs font-bold font-mono flex items-center gap-2 shadow-lg transition disabled:opacity-40"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Processing Queue ({currentIdx + 1}/{batchQueue.length})...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current text-emerald-300" />
                <span>Process Entire Batch</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
