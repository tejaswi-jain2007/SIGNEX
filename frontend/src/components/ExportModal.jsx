import React, { useState } from 'react';
import { FileText, Download, Binary, X, CheckCircle, Shield } from 'lucide-react';

export default function ExportModal({ isOpen, onClose, analysisResult, theme = 'dark' }) {
  if (!isOpen || !analysisResult) return null;

  const { downloads = {}, filename = 'signal_capture' } = analysisResult;
  const baseName = filename.replace(/\.[^/.]+$/, '');

  const handleDownload = (url, downloadName) => {
    if (!url) return;
    const fullUrl = url.startsWith('http') ? url : `http://127.0.0.1:8000${url}`;
    const link = document.createElement('a');
    link.href = fullUrl;
    link.download = downloadName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const isDark = theme === 'dark';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div
        className={`w-full max-w-lg rounded-xl border shadow-2xl p-6 relative animate-in fade-in zoom-in-95 duration-150 ${
          isDark
            ? 'bg-[#0B1325] border-[#1E293B] text-[#E2E8F0]'
            : 'bg-[#FFFFFF] border-[#CBD5E0] text-[#1E293B]'
        }`}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-3 border-b border-inherit">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-[#38BDF8]" />
            <h3 className="text-sm font-bold uppercase tracking-wider font-mono">
              Export Intelligence Deliverable
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-slate-700/30 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-xs font-mono text-slate-400 mt-3 mb-4">
          Select intelligence deliverable format to export for target recording: <br />
          <strong className={isDark ? 'text-white' : 'text-slate-900'}>{filename}</strong>
        </p>

        {/* Deliverable Options */}
        <div className="space-y-3">
          {/* Option 1: PDF Dossier */}
          <div
            className={`p-3.5 rounded-lg border flex items-center justify-between transition ${
              isDark
                ? 'bg-[#0F172A] border-[#1E293B] hover:border-[#38BDF8]/60'
                : 'bg-[#F8FAFC] border-[#CBD5E0] hover:border-[#0284C7]'
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold font-mono">PDF Dossier (*.pdf)</h4>
                <p className="text-[11px] text-slate-400">
                  Full intelligence report with parameters table, AMC verdict, and constellation plot.
                </p>
              </div>
            </div>
            <button
              onClick={() => handleDownload(downloads.pdf, `${baseName}_dossier.pdf`)}
              className="px-3 py-1.5 rounded bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-bold font-mono transition"
            >
              Export PDF
            </button>
          </div>

          {/* Option 2: JSON Record */}
          <div
            className={`p-3.5 rounded-lg border flex items-center justify-between transition ${
              isDark
                ? 'bg-[#0F172A] border-[#1E293B] hover:border-[#38BDF8]/60'
                : 'bg-[#F8FAFC] border-[#CBD5E0] hover:border-[#0284C7]'
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded bg-sky-500/10 text-[#38BDF8] border border-sky-500/20">
                <Download className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold font-mono">JSON Record (*.json)</h4>
                <p className="text-[11px] text-slate-400">
                  Structured machine-readable JSON metadata and raw telemetry frames.
                </p>
              </div>
            </div>
            <button
              onClick={() => handleDownload(downloads.json, `${baseName}_analysis.json`)}
              className="px-3 py-1.5 rounded bg-[#1E293B] hover:bg-[#334155] border border-[#334155] text-white text-xs font-bold font-mono transition"
            >
              Export JSON
            </button>
          </div>

          {/* Option 3: Binary Payload */}
          <div
            className={`p-3.5 rounded-lg border flex items-center justify-between transition ${
              isDark
                ? 'bg-[#0F172A] border-[#1E293B] hover:border-[#38BDF8]/60'
                : 'bg-[#F8FAFC] border-[#CBD5E0] hover:border-[#0284C7]'
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                <Binary className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-xs font-bold font-mono">Binary Payload (*.bin)</h4>
                <p className="text-[11px] text-slate-400">
                  Raw demodulated bitstream converted to 8-bit binary octets.
                </p>
              </div>
            </div>
            <button
              onClick={() => handleDownload(downloads.bin, `${baseName}_payload.bin`)}
              disabled={!downloads.bin}
              className="px-3 py-1.5 rounded bg-[#1E293B] hover:bg-[#334155] border border-[#334155] text-white text-xs font-bold font-mono transition disabled:opacity-40"
            >
              Export BIN
            </button>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="mt-5 pt-3 border-t border-inherit flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-slate-700/40 hover:bg-slate-700 text-xs font-mono font-semibold transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
