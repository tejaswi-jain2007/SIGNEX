import React, { useState, useEffect, useRef } from 'react';

export default function VisualizationPanel({ analysisResult, isAnalyzing, activeTab = 'waterfall' }) {
  const [copiedHex, setCopiedHex] = useState(false);
  const [selectedRange, setSelectedRange] = useState('1M');

  // Canvas refs
  const spectrogramCanvasRef = useRef(null);
  const waveformCanvasRef = useRef(null);
  const constellationCanvasRef = useRef(null);

  // -------------------------------------------------------------
  // Render Waveform Canvas (Hot Pink to Violet Spline with Peak Dots from Image)
  // -------------------------------------------------------------
  useEffect(() => {
    if (!analysisResult?.visualizations?.waveform) return;
    const canvas = waveformCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = (canvas.width = canvas.offsetWidth * (window.devicePixelRatio || 1));
    const height = (canvas.height = canvas.offsetHeight * (window.devicePixelRatio || 1));

    const { i } = analysisResult.visualizations.waveform;
    if (!i || i.length === 0) return;

    ctx.fillStyle = '#0D1220';
    ctx.fillRect(0, 0, width, height);

    // Subtle dark grid
    ctx.strokeStyle = '#182138';
    ctx.lineWidth = 1;
    for (let x = 0; x < width; x += width / 8) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += height / 4) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    const maxVal = Math.max(...i.map(Math.abs), 0.1);
    const scaleY = (height / 2 - 18) / maxVal;
    const stepX = width / (i.length - 1);

    // Fill gradient under curve (Hot Pink / Magenta from Image)
    const areaGrad = ctx.createLinearGradient(0, 0, 0, height);
    areaGrad.addColorStop(0, 'rgba(255, 0, 85, 0.45)');
    areaGrad.addColorStop(1, 'rgba(168, 85, 247, 0.0)');

    ctx.fillStyle = areaGrad;
    ctx.beginPath();
    ctx.moveTo(0, height);
    for (let idx = 0; idx < i.length; idx++) {
      const x = idx * stepX;
      const y = height / 2 - i[idx] * scaleY;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(width, height);
    ctx.closePath();
    ctx.fill();

    // Hot Pink Spline Curve Line
    ctx.strokeStyle = '#FF0055';
    ctx.lineWidth = 2.5;
    ctx.shadowColor = '#FF0055';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    for (let idx = 0; idx < i.length; idx++) {
      const x = idx * stepX;
      const y = height / 2 - i[idx] * scaleY;
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Draw White Indicator Dots on Peaks (Matching Image)
    const peakStep = Math.max(1, Math.floor(i.length / 6));
    for (let pIdx = Math.floor(peakStep / 2); pIdx < i.length; pIdx += peakStep) {
      const px = pIdx * stepX;
      const py = height / 2 - i[pIdx] * scaleY;
      ctx.fillStyle = '#FFFFFF';
      ctx.shadowColor = '#FFFFFF';
      ctx.shadowBlur = 6;
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, 2 * Math.PI);
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }, [analysisResult, activeTab]);

  // -------------------------------------------------------------
  // Render Spectrogram Canvas
  // -------------------------------------------------------------
  useEffect(() => {
    if (!analysisResult?.visualizations?.spectrogram) return;
    const canvas = spectrogramCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = (canvas.width = canvas.offsetWidth * (window.devicePixelRatio || 1));
    const height = (canvas.height = canvas.offsetHeight * (window.devicePixelRatio || 1));

    const { matrix_db } = analysisResult.visualizations.spectrogram;
    if (!matrix_db || matrix_db.length === 0) return;

    const nFreqs = matrix_db.length;
    const nTimes = matrix_db[0].length;

    const getNeonColor = (t) => {
      const r = Math.floor(255 * Math.sin(t * Math.PI * 0.8));
      const g = Math.floor(200 * Math.sin(t * Math.PI * 0.9 + 0.2));
      const b = Math.floor(255 * (1 - t * 0.6));
      return `rgb(${r}, ${g}, ${b})`;
    };

    const cellW = width / nTimes;
    const cellH = height / nFreqs;

    let minDb = Infinity, maxDb = -Infinity;
    for (let r = 0; r < nFreqs; r++) {
      for (let c = 0; c < nTimes; c++) {
        const v = matrix_db[r][c];
        if (v < minDb) minDb = v;
        if (v > maxDb) maxDb = v;
      }
    }
    const rangeDb = maxDb - minDb || 1.0;

    for (let f = 0; f < nFreqs; f++) {
      for (let t = 0; t < nTimes; t++) {
        const norm = Math.max(0, Math.min(1, (matrix_db[f][t] - minDb) / rangeDb));
        ctx.fillStyle = getNeonColor(norm);
        ctx.fillRect(t * cellW, height - (f + 1) * cellH, cellW + 1, cellH + 1);
      }
    }
  }, [analysisResult, activeTab]);

  // -------------------------------------------------------------
  // Render Constellation Canvas
  // -------------------------------------------------------------
  useEffect(() => {
    if (!analysisResult?.visualizations?.constellation) return;
    const canvas = constellationCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const size = Math.min(canvas.offsetWidth, canvas.offsetHeight) * (window.devicePixelRatio || 1);
    canvas.width = size;
    canvas.height = size;

    const points = analysisResult.visualizations.constellation;

    ctx.fillStyle = '#0D1220';
    ctx.fillRect(0, 0, size, size);

    ctx.strokeStyle = '#1E2842';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, size / 2);
    ctx.lineTo(size, size / 2);
    ctx.moveTo(size / 2, 0);
    ctx.lineTo(size / 2, size);
    ctx.stroke();

    [0.3, 0.6, 0.9].forEach((r) => {
      ctx.beginPath();
      ctx.arc(size / 2, size / 2, (size / 2 - 16) * r, 0, 2 * Math.PI);
      ctx.stroke();
    });

    if (points.length === 0) return;

    const maxCoord = Math.max(
      ...points.map((p) => Math.max(Math.abs(p.i), Math.abs(p.q))),
      1.2
    );
    const scale = (size / 2 - 22) / maxCoord;

    ctx.fillStyle = '#00D2FF';
    ctx.shadowColor = '#00D2FF';
    ctx.shadowBlur = 5;

    points.forEach((p) => {
      const x = size / 2 + p.i * scale;
      const y = size / 2 - p.q * scale;
      ctx.beginPath();
      ctx.arc(x, y, 2.5, 0, 2 * Math.PI);
      ctx.fill();
    });
    ctx.shadowBlur = 0;
  }, [analysisResult, activeTab]);

  const handleCopyHex = () => {
    if (!analysisResult?.visualizations?.hex_dump) return;
    const text = analysisResult.visualizations.hex_dump
      .map((l) => `${l.offset}  ${l.hex.padEnd(48, ' ')}  |${l.ascii}|`)
      .join('\n');
    navigator.clipboard.writeText(text);
    setCopiedHex(true);
    setTimeout(() => setCopiedHex(false), 2000);
  };

  // Mock vertical spectrum frequency bars from user image
  const spectrumBars = [
    { label: 'CH-1', height: '75%', color: 'from-[#A855F7] to-[#00D2FF]' },
    { label: 'CH-2', height: '45%', color: 'from-[#EC4899] to-[#8B5CF6]' },
    { label: 'CH-3', height: '90%', color: 'from-[#00D2FF] to-[#0066FF]' },
    { label: 'CH-4', height: '60%', color: 'from-[#A855F7] to-[#EC4899]' },
    { label: 'CH-5', height: '35%', color: 'from-[#8B5CF6] to-[#00D2FF]' },
    { label: 'CH-6', height: '80%', color: 'from-[#00D2FF] to-[#38BDF8]' }
  ];

  return (
    <div className="h-full flex flex-col gap-3 min-h-0 overflow-hidden select-none">
      {/* 1. Top Row: Spectrum Frequency Gradient Bars */}
      <div className="dark-card p-3.5 flex flex-col justify-between shrink-0 h-36">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold card-title uppercase tracking-wider">
            SPECTRUM DENSITY & TIME SLICES
          </span>
          <div className="flex space-x-1 dark-card-inner p-1 rounded-xl text-[10px] font-bold">
            {['1D', '1W', '1M', '3M', '6M'].map((range) => (
              <button
                key={range}
                onClick={() => setSelectedRange(range)}
                className={`px-2 py-0.5 rounded-lg transition ${
                  selectedRange === range ? 'bg-[#00D2FF] text-white shadow-xs' : 'card-text-muted hover:text-white'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>

        {/* Multi-frequency Gradient Vertical Bars from Image */}
        <div className="flex items-end justify-between h-20 px-4 pt-2">
          {spectrumBars.map((bar, idx) => (
            <div key={idx} className="flex flex-col items-center gap-1">
              <div
                className={`w-6 rounded-t-lg bg-gradient-to-t ${bar.color} transition-all duration-500 shadow-md`}
                style={{ height: bar.height }}
              />
              <span className="text-[9px] font-mono card-text-muted">{bar.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 2. Middle Row: Main Glowing Waveform / Spectrogram Graph */}
      <div className="dark-card p-3.5 flex-1 min-h-0 flex flex-col justify-between overflow-hidden">
        <div className="flex items-center justify-between mb-1.5 shrink-0">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold card-title uppercase tracking-wider">
              {activeTab === 'waterfall'
                ? 'Time-Domain Waveform & Spectrogram'
                : activeTab === 'constellation'
                ? 'I/Q Constellation & Power Distribution'
                : 'Frame & Bitstream Telemetry'}
            </span>
          </div>

          <span className="text-xs font-mono font-bold text-[#00D2FF]">
            {analysisResult ? `${(analysisResult.duration_sec * 1000).toFixed(1)} ms` : '7,780 SAMPLES'}
          </span>
        </div>

        {/* Dynamic Display Area */}
        <div className="flex-1 min-h-0 w-full relative rounded-xl overflow-hidden border border-[#1A233A] bg-[#0D1220]">
          {activeTab === 'waterfall' && (
            <div className="h-full w-full flex flex-col">
              <canvas ref={waveformCanvasRef} className="w-full h-full absolute inset-0" />
            </div>
          )}

          {activeTab === 'constellation' && (
            <div className="h-full w-full flex items-center justify-center p-2">
              <canvas ref={constellationCanvasRef} className="max-h-[220px] max-w-[220px]" />
            </div>
          )}

          {activeTab === 'payload' && (
            <div className="h-full flex flex-col p-2.5 overflow-y-auto text-xs font-mono">
              <div className="flex justify-between items-center mb-1">
                <span className="text-[11px] font-bold text-slate-300">Synchronized Frames</span>
                <button
                  onClick={handleCopyHex}
                  className="px-2 py-0.5 rounded bg-[#1A233A] hover:bg-[#253252] text-[10px] text-[#00D2FF] font-bold transition"
                >
                  {copiedHex ? 'Copied!' : 'Copy Hex'}
                </button>
              </div>
              <div className="space-y-0.5 select-text text-[11px]">
                {analysisResult?.visualizations?.hex_dump && analysisResult.visualizations.hex_dump.length > 0 ? (
                  analysisResult.visualizations.hex_dump.slice(0, 10).map((line, i) => (
                    <div key={i} className="flex space-x-4 hover:bg-[#1A233A]/60 px-1 rounded transition">
                      <span className="text-[#00D2FF]">{line.offset}</span>
                      <span className="text-white font-semibold">{line.hex}</span>
                      <span className="text-[#FF2E7E]">|{line.ascii}|</span>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-500 py-4 text-center">Run analysis to populate payload.</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
