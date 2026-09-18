import React, { useState, useEffect } from 'react';
import { Bell, Menu, Shield, Sun, Moon } from 'lucide-react';
import SignexLogo from './SignexLogo';

export default function Header({
  isAnalyzing,
  onBrowseFile,
  onRunAnalysis,
  onExportDialog,
  onUndo,
  theme,
  onToggleTheme,
  airgapEnabled,
  activeTab,
  setActiveTab,
  onOpenNotifications,
  unreadCount = 5
}) {
  const [openMenu, setOpenMenu] = useState(false);
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toTimeString().substring(0, 8));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const isDark = theme === 'dark';

  return (
    <header className={`px-5 py-2.5 flex items-center justify-between select-none border-b shrink-0 transition-colors ${
      isDark
        ? 'bg-[#0B0F19]/95 border-[#1E2842]/60 text-[#F8FAFC]'
        : 'bg-[#FFFFFF]/95 border-[#E2E8F0] text-[#0F172A]'
    }`}>
      {/* 1. Left: Logo Badge & User / Notification Pills */}
      <div className="flex items-center space-x-3.5">
        <SignexLogo className="h-8" />

        {/* User Avatar Circle from Image */}
        <div
          onClick={onOpenNotifications}
          className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#FF0055] to-[#FF5588] p-0.5 shadow-md flex items-center justify-center cursor-pointer hover:scale-105 transition"
          title="Operator Profile & System Health"
        >
          <div className={`w-full h-full rounded-full flex items-center justify-center text-xs font-bold ${
            isDark ? 'bg-[#0D1220]' : 'bg-white'
          }`}>
            <Shield className="w-4 h-4 text-[#FF2E7E]" />
          </div>
        </div>

        {/* Notification Bell with Badge from Image */}
        <button
          onClick={onOpenNotifications}
          className={`relative p-2 rounded-xl border cursor-pointer transition hover:scale-105 ${
            isDark
              ? 'bg-[#141B2D] border-[#1E2842] text-slate-300 hover:text-white'
              : 'bg-slate-100 border-slate-200 text-slate-700 hover:text-black'
          }`}
          title="View System Alerts & Intercepts"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-[#FF0055] text-white text-[9px] font-bold flex items-center justify-center shadow-sm">
              {unreadCount}
            </span>
          )}
        </button>
      </div>

      {/* 2. Center: Horizontal Navigation Tabs from Image */}
      <div className="hidden md:flex items-center space-x-8 text-xs font-medium">
        <button
          onClick={() => setActiveTab('waterfall')}
          className={`pb-1 transition font-bold relative ${
            activeTab === 'waterfall'
              ? isDark ? 'text-white border-b-2 border-white' : 'text-blue-600 border-b-2 border-blue-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Waterfall Spectrogram
        </button>

        <button
          onClick={() => setActiveTab('constellation')}
          className={`pb-1 transition font-bold relative ${
            activeTab === 'constellation'
              ? isDark ? 'text-white border-b-2 border-white' : 'text-blue-600 border-b-2 border-blue-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          I/Q Constellation
        </button>

        <button
          onClick={() => setActiveTab('payload')}
          className={`pb-1 transition font-bold relative ${
            activeTab === 'payload'
              ? isDark ? 'text-white border-b-2 border-white' : 'text-blue-600 border-b-2 border-blue-600'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Payload & Hex View
        </button>

        <button
          onClick={onExportDialog}
          className="text-slate-400 hover:text-slate-200 pb-1 font-bold"
        >
          Export Report
        </button>
      </div>

      {/* 3. Right: Live Clock & Theme Switcher */}
      <div className="flex items-center space-x-3">
        <div className={`hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full border text-xs font-mono ${
          isDark
            ? 'bg-[#141B2D] border-[#1E2842] text-slate-300'
            : 'bg-slate-100 border-slate-200 text-slate-700'
        }`}>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>{timeStr}</span>
        </div>

        {/* Theme Toggle Button */}
        <button
          onClick={onToggleTheme}
          className={`p-2 rounded-xl border transition ${
            isDark
              ? 'bg-[#141B2D] border-[#1E2842] text-amber-400 hover:text-amber-300'
              : 'bg-slate-100 border-slate-200 text-sky-600 hover:text-sky-700'
          }`}
          title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
}
