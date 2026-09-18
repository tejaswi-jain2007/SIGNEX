import React from 'react';
import { X, ShieldCheck, Cpu, Radio, Activity, BellOff } from 'lucide-react';

export default function NotificationDrawer({
  isOpen,
  onClose,
  notifications = [],
  onClearAll,
  onMarkAllRead,
  unreadCount = 0,
  theme = 'dark'
}) {
  if (!isOpen) return null;
  const isDark = theme === 'dark';

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end p-4 pt-16 bg-black/40 backdrop-blur-xs">
      <div
        className={`w-96 rounded-2xl shadow-2xl border p-4 animate-in fade-in zoom-in-95 duration-150 relative ${
          isDark
            ? 'bg-[#121829] border-[#1E2842] text-[#F8FAFC]'
            : 'bg-white border-[#E2E8F0] text-[#0F172A]'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-inherit">
          <div className="flex items-center space-x-2">
            <h3 className="text-xs font-bold font-mono uppercase tracking-wider">
              System Alerts & Intercepts
            </h3>
            {unreadCount > 0 && (
              <span className="px-1.5 py-0.5 rounded-full bg-[#FF0055] text-white text-[9px] font-bold">
                {unreadCount} New
              </span>
            )}
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-700/20 text-slate-400 hover:text-white transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Action Toolbar */}
        <div className="flex items-center justify-between py-2 text-[10px] font-mono text-slate-400 border-b border-inherit mb-2">
          <span>Real-time Intercept Bus</span>
          <div className="flex space-x-3">
            {unreadCount > 0 && (
              <button
                onClick={onMarkAllRead}
                className="hover:text-[#00D2FF] font-bold transition cursor-pointer"
              >
                Mark Read
              </button>
            )}
            <button
              onClick={onClearAll}
              className="hover:text-rose-400 font-bold transition cursor-pointer"
            >
              Clear All
            </button>
          </div>
        </div>

        {/* Notifications List */}
        <div className="max-h-80 overflow-y-auto space-y-2 pr-1 text-xs font-mono">
          {notifications.length === 0 ? (
            <div className="text-center py-8 text-slate-500 flex flex-col items-center gap-1.5">
              <BellOff className="w-6 h-6 text-slate-500" />
              <span>No active notifications.</span>
            </div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`p-2.5 rounded-xl border transition flex items-start space-x-2.5 ${
                  n.read
                    ? isDark ? 'bg-[#0D1220]/60 border-[#1A233A] opacity-70' : 'bg-slate-50 border-slate-200 opacity-70'
                    : isDark ? 'bg-[#0D1220] border-[#00D2FF]/40' : 'bg-sky-50/70 border-sky-300'
                }`}
              >
                <div className={`p-1.5 rounded-lg shrink-0 mt-0.5 ${
                  isDark ? 'bg-[#141B2D]' : 'bg-slate-200/70'
                }`}>
                  {n.type === 'shield' ? (
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                  ) : n.type === 'cpu' ? (
                    <Cpu className="w-3.5 h-3.5 text-purple-500" />
                  ) : n.type === 'radio' ? (
                    <Radio className="w-3.5 h-3.5 text-[#00D2FF]" />
                  ) : (
                    <Activity className="w-3.5 h-3.5 text-amber-500" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className={`font-bold text-[11px] truncate ${
                      isDark ? 'text-slate-200' : 'text-slate-800'
                    }`}>
                      {n.title}
                    </span>
                    <span className="text-[9px] text-slate-400">{n.time}</span>
                  </div>
                  <p className={`text-[10px] mt-0.5 leading-snug ${
                    isDark ? 'text-slate-400' : 'text-slate-600'
                  }`}>
                    {n.message}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="mt-3 pt-2 border-t border-inherit flex justify-between items-center text-[10px] font-mono text-slate-400">
          <span>SIGNEX Security Policy</span>
          <span className="text-emerald-500 font-bold">AIR-GAP 100%</span>
        </div>
      </div>
    </div>
  );
}
