import React from 'react';

export default function TelemetryPanel({
  analysisResult,
  isAnalyzing,
  onOpenExportModal
}) {
  const amc = analysisResult?.classification || {};
  const predClass = amc.predicted_class || 'WAITING...';
  const confidence = amc.confidence !== undefined ? (amc.confidence * 100).toFixed(1) : '76.9';
  const p = analysisResult?.parameters || {};

  return (
    <div className="flex flex-col h-full justify-between gap-3 overflow-y-auto pr-0.5 select-none text-xs">
      {/* 1. Top Card: AMC Donut & Probability Breakdown */}
      <div className="dark-card p-4 space-y-3">
        <h4 className="text-xs font-bold card-title uppercase tracking-wider">
          CLASSIFICATION (AMC)
        </h4>

        <div className="flex items-center justify-between">
          {/* Legend / Metrics */}
          <div className="space-y-1.5 text-[11px] font-mono">
            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-[#A855F7]" />
              <span className="card-text-muted">Modulation: <strong className="card-title">{predClass}</strong></span>
            </div>

            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-[#F59E0B]" />
              <span className="card-text-muted">Confidence: <strong className="text-[#00D2FF]">{confidence}%</strong></span>
            </div>

            <div className="flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-[#FF0055]" />
              <span className="card-text-muted">Status: <strong className="text-emerald-500">CERTAIN</strong></span>
            </div>
          </div>

          {/* Glowing Multi-Color Donut Ring from Image */}
          <div className="relative w-16 h-16 flex items-center justify-center shrink-0">
            <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
              <circle
                cx="18"
                cy="18"
                r="14"
                fill="none"
                stroke="#1A233A"
                strokeWidth="4"
              />
              <circle
                cx="18"
                cy="18"
                r="14"
                fill="none"
                stroke="#FF0055"
                strokeWidth="4"
                strokeDasharray="40 100"
                strokeDashoffset="0"
                className="drop-shadow-[0_0_8px_#FF0055]"
              />
              <circle
                cx="18"
                cy="18"
                r="14"
                fill="none"
                stroke="#A855F7"
                strokeWidth="4"
                strokeDasharray="30 100"
                strokeDashoffset="-40"
                className="drop-shadow-[0_0_8px_#A855F7]"
              />
              <circle
                cx="18"
                cy="18"
                r="14"
                fill="none"
                stroke="#00D2FF"
                strokeWidth="4"
                strokeDasharray="20 100"
                strokeDashoffset="-70"
                className="drop-shadow-[0_0_8px_#00D2FF]"
              />
            </svg>
            <span className="absolute text-[10px] font-mono font-bold card-title">
              {Math.round(parseFloat(confidence))}%
            </span>
          </div>
        </div>
      </div>

      {/* 2. Middle Row: Metric Boxes with Hot Pink Buttons */}
      <div className="grid grid-cols-2 gap-2.5">
        {/* Metric 1: SNR */}
        <div className="dark-card p-3 flex flex-col justify-between space-y-2">
          <div>
            <span className="text-[10px] font-mono card-text-muted block uppercase">
              ESTIMATED SNR
            </span>
            <span className="text-sm font-mono font-bold card-title">
              {p.snr_db !== undefined ? `${p.snr_db.toFixed(2)} dB` : '18.50 dB'}
            </span>
          </div>

          <button
            onClick={onOpenExportModal}
            disabled={!analysisResult}
            className="w-full py-1.5 pink-pill-btn text-[10px] uppercase tracking-wider disabled:opacity-40"
          >
            EXPORT PDF
          </button>
        </div>

        {/* Metric 2: Symbol Rate */}
        <div className="dark-card p-3 flex flex-col justify-between space-y-2">
          <div>
            <span className="text-[10px] font-mono card-text-muted block uppercase">
              SYMBOL RATE
            </span>
            <span className="text-sm font-mono font-bold card-title">
              {p.symbol_rate !== undefined ? `${(p.symbol_rate / 1e3).toFixed(1)} kBaud` : '250.0 kBaud'}
            </span>
          </div>

          <button
            onClick={onOpenExportModal}
            disabled={!analysisResult}
            className="w-full py-1.5 pink-pill-btn text-[10px] uppercase tracking-wider disabled:opacity-40"
          >
            EXPORT JSON
          </button>
        </div>
      </div>

      {/* 3. Bottom Row: 3 Concentric Glowing Ring Gauges */}
      <div className="dark-card p-3 flex items-center justify-around">
        {/* Ring 1: Hot Pink */}
        <div className="flex flex-col items-center gap-1.5">
          <div className="w-12 h-12 rounded-full border-[3.5px] border-[#FF0055] flex items-center justify-center shadow-[0_0_12px_rgba(255,0,85,0.4)]">
            <span className="text-xs font-mono font-bold card-title">77%</span>
          </div>
          <span className="text-[9px] font-mono card-text-muted uppercase">99% BW</span>
        </div>

        {/* Ring 2: Electric Cyan */}
        <div className="flex flex-col items-center gap-1.5">
          <div className="w-12 h-12 rounded-full border-[3.5px] border-[#00D2FF] flex items-center justify-center shadow-[0_0_12px_rgba(0,210,255,0.4)]">
            <span className="text-xs font-mono font-bold card-title">61%</span>
          </div>
          <span className="text-[9px] font-mono card-text-muted uppercase">CONF</span>
        </div>

        {/* Ring 3: Electric Purple */}
        <div className="flex flex-col items-center gap-1.5">
          <div className="w-12 h-12 rounded-full border-[3.5px] border-[#A855F7] flex items-center justify-center shadow-[0_0_12px_rgba(168,85,247,0.4)]">
            <span className="text-xs font-mono font-bold card-title">41%</span>
          </div>
          <span className="text-[9px] font-mono card-text-muted uppercase">FLATNESS</span>
        </div>
      </div>

      {/* 4. Complete Parameters Table */}
      <div className="dark-card p-3 flex-1 min-h-0 flex flex-col overflow-hidden">
        <span className="text-[11px] font-bold card-title block uppercase mb-1.5">
          SIGNAL PARAMETERS
        </span>

        <div className="flex-1 min-h-0 overflow-y-auto rounded-lg dark-card-inner p-1.5">
          <table className="w-full text-left text-[10px] font-mono">
            <tbody className="divide-y divide-[#1A233A]/30">
              <tr>
                <td className="py-1 card-text-muted">Sampling Rate (Fs)</td>
                <td className="py-1 text-right font-bold card-title">{p.fs ? `${(p.fs/1e6).toFixed(3)} MHz` : '-'}</td>
              </tr>
              <tr>
                <td className="py-1 card-text-muted">Center Frequency</td>
                <td className="py-1 text-right font-bold text-[#00D2FF]">{p.center_freq !== undefined ? `${(p.center_freq/1e3).toFixed(2)} kHz` : '-'}</td>
              </tr>
              <tr>
                <td className="py-1 card-text-muted">3-dB Bandwidth</td>
                <td className="py-1 text-right font-bold card-title">{p.bandwidth_3db !== undefined ? `${(p.bandwidth_3db/1e3).toFixed(1)} kHz` : '-'}</td>
              </tr>
              <tr>
                <td className="py-1 card-text-muted">PAPR</td>
                <td className="py-1 text-right font-bold card-title">{p.papr_db !== undefined ? `${p.papr_db.toFixed(2)} dB` : '-'}</td>
              </tr>
              <tr>
                <td className="py-1 card-text-muted">Carrier Offset</td>
                <td className="py-1 text-right font-bold text-[#FF2E7E]">{p.cfo_hz !== undefined ? `${p.cfo_hz.toFixed(1)} Hz` : '-'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
