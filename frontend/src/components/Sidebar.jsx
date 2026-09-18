import React from 'react';
import { Home, Shield, Settings, Lock, Layers, Play } from 'lucide-react';

export default function Sidebar({
  activeNav = 'ingestion',
  setActiveNav,
  onRunAnalysis,
  isAnalyzing,
  onOpenBatchModal,
  airgapGuard
}) {
  return (
    <aside className="w-52 h-full flex flex-col justify-between p-3 border-r shrink-0 select-none transition-colors border-[#1E2842]/40 bg-inherit">
      {/* 1. Top Section */}
      <div className="space-y-4">
        <span className="text-[10px] font-mono font-bold tracking-widest text-slate-500 block px-2 uppercase">
          WORKSTATION
        </span>

        {/* Navigation Items (Pills Matching Image) */}
        <nav className="space-y-2">
          {/* Item 1: Overview */}
          <button
            onClick={() => setActiveNav('overview')}
            className={`w-full px-3.5 py-2.5 flex items-center space-x-3 rounded-2xl text-xs font-bold transition ${
              activeNav === 'overview'
                ? 'cyan-pill-active'
                : 'sidebar-pill-inactive'
            }`}
          >
            <Home className="w-4 h-4" />
            <span>Dashboard</span>
          </button>

          {/* Item 2: Ingestion & Analysis (Active Glowing Cyan Pill) */}
          <button
            onClick={() => setActiveNav('ingestion')}
            className={`w-full px-3.5 py-2.5 flex items-center space-x-3 rounded-2xl text-xs font-bold transition ${
              activeNav === 'ingestion'
                ? 'cyan-pill-active'
                : 'sidebar-pill-inactive'
            }`}
          >
            <Shield className="w-4 h-4" />
            <span>Signal Ingest</span>
          </button>

          {/* Item 3: Pipeline Configuration */}
          <button
            onClick={() => setActiveNav('config')}
            className={`w-full px-3.5 py-2.5 flex items-center space-x-3 rounded-2xl text-xs font-bold transition ${
              activeNav === 'config'
                ? 'cyan-pill-active'
                : 'sidebar-pill-inactive'
            }`}
          >
            <Settings className="w-4 h-4" />
            <span>Pipeline Config</span>
          </button>

          {/* Item 4: Air-Gap Guard */}
          <button
            onClick={() => setActiveNav('airgap')}
            className={`w-full px-3.5 py-2.5 flex items-center space-x-3 rounded-2xl text-xs font-bold transition ${
              activeNav === 'airgap'
                ? 'cyan-pill-active'
                : 'sidebar-pill-inactive'
            }`}
          >
            <Lock className="w-4 h-4" />
            <span>Air-Gap Guard</span>
          </button>

          {/* Item 5: Batch Processing Queue */}
          <button
            onClick={onOpenBatchModal}
            className="w-full px-3.5 py-2.5 flex items-center space-x-3 rounded-2xl text-xs font-bold sidebar-pill-inactive"
          >
            <Layers className="w-4 h-4" />
            <span>Batch Queue</span>
          </button>
        </nav>
      </div>

      {/* 2. Bottom Section & Quick Action Button */}
      <div className="space-y-3 pt-4 border-t border-[#1E2842]/30">
        <div>
          <span className="text-[10px] font-mono font-bold text-slate-400 block uppercase">
            STATUS: RESTRICTED
          </span>
          <p className="text-[9px] text-slate-500 font-mono mt-0.5 leading-tight">
            Air-gapped SIGINT Engine v2.0 Active
          </p>
        </div>

        {/* Master Execution Action Pill */}
        <button
          onClick={onRunAnalysis}
          disabled={isAnalyzing}
          className="w-full py-2.5 px-3 rounded-xl cyan-pill-active text-xs font-bold uppercase tracking-wider flex items-center justify-center space-x-2 shadow-lg disabled:opacity-40"
        >
          {isAnalyzing ? (
            <span>RUNNING...</span>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>RUN ANALYSIS</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
