import React, { useRef } from 'react';
import { Upload, Play, Plus, Minus } from 'lucide-react';

export default function ControlPanel({
  onRunAnalysis,
  onStopAnalysis,
  isAnalyzing,
  progressPct = 0,
  presetSamples = [],
  selectedPreset,
  setSelectedPreset,
  uploadedFile,
  setUploadedFile,
  filePathText,
  setFilePathText,
  samplingRate,
  setSamplingRate,
  fftWindowSize,
  setFftWindowSize,
  windowType,
  setWindowType,
  airgapGuard,
  setAirgapGuard,
  batchQueue = [],
  onOpenBatchModal
}) {
  const fileInputRef = useRef(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setUploadedFile(file);
      setSelectedPreset('');
      setFilePathText(file.name);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadedFile(file);
      setSelectedPreset('');
      setFilePathText(file.name);
    }
  };

  const handlePresetSelect = (presetName) => {
    setSelectedPreset(presetName);
    setUploadedFile(null);
    setFilePathText(presetName ? `data/test_samples/${presetName}` : '');
  };

  const inputClass = `w-full px-3 py-1.5 rounded-xl form-input text-xs font-mono transition`;

  return (
    <div className="flex flex-col h-full justify-between gap-3 overflow-y-auto pr-0.5 select-none text-xs">
      {/* 1. Top Ingestion & Action Pill */}
      <div className="dark-card p-4 flex items-center justify-between">
        <div>
          <h4 className="text-xs font-bold card-title uppercase tracking-wider">
            SIGNAL INGESTION
          </h4>
          <p className="text-[11px] card-text-muted font-mono mt-0.5 truncate max-w-[170px]">
            {uploadedFile?.name || selectedPreset || 'Select .IQ / .WAV file'}
          </p>
        </div>

        {/* Circular Action Button (+) from Image */}
        <button
          onClick={() => fileInputRef.current?.click()}
          className="round-action-btn shrink-0"
          title="Browse file (+)"
        >
          <Plus className="w-5 h-5 stroke-[2.5]" />
        </button>

        <input
          ref={fileInputRef}
          type="file"
          accept=".iq,.wav,.raw,.dat,.npy,.bin"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* 2. Analysis Engine Quick Card */}
      <div className="dark-card p-4 flex items-center justify-between">
        <div>
          <h4 className="text-xs font-bold card-title uppercase tracking-wider">
            ANALYSIS ENGINE
          </h4>
          <p className="text-[11px] card-text-muted font-mono mt-0.5">
            {isAnalyzing ? `Running ${progressPct}%` : 'Engine Ready (Ctrl+R)'}
          </p>
        </div>

        {/* Circular Action Button Play/Stop from Image */}
        <button
          onClick={isAnalyzing ? onStopAnalysis : onRunAnalysis}
          disabled={!isAnalyzing && !uploadedFile && !selectedPreset && !filePathText}
          className="round-action-btn shrink-0 disabled:opacity-40"
          title="Run / Stop Analysis"
        >
          {isAnalyzing ? (
            <Minus className="w-5 h-5 stroke-[2.5]" />
          ) : (
            <Play className="w-4 h-4 fill-current ml-0.5" />
          )}
        </button>
      </div>

      {/* 3. Drop Zone & Preset Selection */}
      <div className="dark-card p-3.5 space-y-2">
        <span className="text-[11px] font-bold card-title block uppercase tracking-wider">
          Target File & Preset
        </span>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          onClick={() => fileInputRef.current?.click()}
          className="border border-dashed border-[#1E2846] hover:border-[#00D2FF] dark-card-inner p-2.5 text-center cursor-pointer transition"
        >
          <div className="flex items-center justify-center gap-2">
            <Upload className="w-4 h-4 text-[#00D2FF]" />
            <p className="text-xs font-bold card-title truncate">
              {uploadedFile ? uploadedFile.name : selectedPreset ? selectedPreset : 'Drop .IQ file or browse'}
            </p>
          </div>
        </div>

        <select
          value={selectedPreset}
          onChange={(e) => handlePresetSelect(e.target.value)}
          className={inputClass}
        >
          <option value="">-- Choose Sample Capture --</option>
          {presetSamples.map((s) => (
            <option key={s.filename} value={s.filename}>
              [{s.modulation}] {s.filename} ({(s.sample_rate / 1e6).toFixed(1)} MSps)
            </option>
          ))}
        </select>
      </div>

      {/* 4. PIPELINE CONFIGURATION */}
      <div className="dark-card p-3.5 space-y-2">
        <span className="text-[11px] font-bold card-title block uppercase tracking-wider">
          PIPELINE CONFIGURATION
        </span>

        <div className="space-y-1.5 text-xs font-mono">
          <div className="grid grid-cols-2 items-center gap-2">
            <label className="card-text-muted">Sampling Rate:</label>
            <select
              value={samplingRate}
              onChange={(e) => setSamplingRate(e.target.value)}
              className={inputClass}
            >
              <option value="Auto (Metadata)">Auto (Metadata)</option>
              <option value="1.0 MHz">1.0 MHz</option>
              <option value="2.0 MHz">2.0 MHz</option>
              <option value="5.0 MHz">5.0 MHz</option>
              <option value="10.0 MHz">10.0 MHz</option>
              <option value="20.0 MHz">20.0 MHz</option>
              <option value="48.0 kHz">48.0 kHz</option>
            </select>
          </div>

          <div className="grid grid-cols-2 items-center gap-2">
            <label className="card-text-muted">FFT Window:</label>
            <select
              value={fftWindowSize}
              onChange={(e) => setFftWindowSize(e.target.value)}
              className={inputClass}
            >
              <option value="512">512</option>
              <option value="1024">1024</option>
              <option value="2048">2048</option>
              <option value="4096">4096</option>
            </select>
          </div>

          <div className="grid grid-cols-2 items-center gap-2">
            <label className="card-text-muted">Window Type:</label>
            <select
              value={windowType}
              onChange={(e) => setWindowType(e.target.value)}
              className={inputClass}
            >
              <option value="hann">hann</option>
              <option value="hamming">hamming</option>
              <option value="blackman">blackman</option>
            </select>
          </div>

          <div className="pt-1 flex items-center justify-between border-t border-[#1E2842]/40">
            <label className="flex items-center space-x-2 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={airgapGuard}
                onChange={(e) => setAirgapGuard(e.target.checked)}
                className="w-3.5 h-3.5 rounded bg-inherit border-[#1E2842] text-[#00D2FF] focus:ring-0 cursor-pointer"
              />
              <span className="card-title font-bold text-[11px]">
                Air-Gap Guard
              </span>
            </label>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
        </div>
      </div>

      {/* 5. BATCH PROCESSING QUEUE */}
      <div className="dark-card p-3 flex items-center justify-between">
        <div>
          <span className="text-[11px] font-bold card-title block uppercase">
            BATCH QUEUE
          </span>
          <span className="text-[10px] card-text-muted font-mono">
            {batchQueue.length} files queued
          </span>
        </div>

        <button
          onClick={onOpenBatchModal}
          className="px-3 py-1.5 rounded-xl bg-[#1A233A] hover:bg-[#253252] text-xs font-bold text-white border border-[#2A395C] transition shadow-xs"
        >
          Open Queue
        </button>
      </div>
    </div>
  );
}
