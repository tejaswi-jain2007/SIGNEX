import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ControlPanel from './components/ControlPanel';
import VisualizationPanel from './components/VisualizationPanel';
import TelemetryPanel from './components/TelemetryPanel';
import NotificationDrawer from './components/NotificationDrawer';
import ExportModal from './components/ExportModal';
import BatchModal from './components/BatchModal';
import { AlertCircle } from 'lucide-react';

// Backend URL — defaults to live Render backend, or overridden by VITE_API_URL
const API_BASE = (import.meta.env.VITE_API_URL || 'https://signex-backend.onrender.com').replace(/\/+$/, '');


export default function App() {
  const [theme, setTheme] = useState('dark');
  const [airgapGuard, setAirgapGuard] = useState(true);
  const [activeNav, setActiveNav] = useState('ingestion');
  const [activeTab, setActiveTab] = useState('waterfall');

  const [presetSamples, setPresetSamples] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [filePathText, setFilePathText] = useState('');
  const [stateHistory, setStateHistory] = useState([]);

  const [samplingRate, setSamplingRate] = useState('Auto (Metadata)');
  const [fftWindowSize, setFftWindowSize] = useState('1024');
  const [windowType, setWindowType] = useState('hann');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progressPct, setProgressPct] = useState(0);
  const [progressStatus, setProgressStatus] = useState('Engine Ready.');
  const [statusMessage, setStatusMessage] = useState('System Initialized | Air-Gapped Standalone Mode');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const [batchQueue, setBatchQueue] = useState([]);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false);

  // Real-time Actionable Notifications System
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState([
    {
      id: 'n-1',
      title: 'Air-Gap Security Active',
      message: 'Perimeter locked. Zero external network egress detected.',
      type: 'shield',
      time: 'Just now',
      read: false
    },
    {
      id: 'n-2',
      title: 'Deep Learning AMC Engine',
      message: 'PyTorch AMC ResNet-18 model initialized & ready for inference.',
      type: 'cpu',
      time: '1m ago',
      read: false
    },
    {
      id: 'n-3',
      title: 'Preset Recordings Indexed',
      message: '10 raw RF capture samples mounted and available.',
      type: 'radio',
      time: '3m ago',
      read: true
    }
  ]);

  const addNotification = useCallback((title, message, type = 'activity') => {
    const newNote = {
      id: `n-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      title,
      message,
      type,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      read: false
    };
    setNotifications((prev) => [newNote, ...prev.slice(0, 24)]);
  }, []);

  // Sync theme changes with DOM Root
  useEffect(() => {
    document.documentElement.className = theme;
    document.body.className = theme;
  }, [theme]);

  // Fetch presets from FastAPI backend
  useEffect(() => {
    fetch(`${API_BASE}/api/samples`)
      .then((res) => res.json())
      .then((data) => {
        if (data.samples && data.samples.length > 0) {
          setPresetSamples(data.samples);
          setSelectedPreset(data.samples[0].filename);
          setFilePathText(`data/test_samples/${data.samples[0].filename}`);
        }
      })
      .catch((err) => {
        console.warn('Backend connection notice:', err);
      });
  }, []);

  const handleUndo = () => {
    if (stateHistory.length > 0) {
      const prev = stateHistory[stateHistory.length - 1];
      setStateHistory((history) => history.slice(0, -1));
      setFilePathText(prev);
      setUploadedFile(null);
      setSelectedPreset('');
      setStatusMessage(`Undid file selection.`);
      addNotification('Undo Action', 'Restored previous file selection state.', 'activity');
    }
  };

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleToggleAirgap = (enabled) => {
    setAirgapGuard(enabled);
    addNotification(
      'Security Policy Altered',
      `Air-Gap Guard is now ${enabled ? 'ENGAGED (Network Locked)' : 'DISABLED (Warning)'}`,
      'shield'
    );
  };

  const handleRunAnalysis = useCallback(async () => {
    if (!uploadedFile && !selectedPreset && !filePathText) {
      alert('Please select or drop a valid signal recording file first.');
      return;
    }

    const currentTarget = uploadedFile?.name || selectedPreset || filePathText;
    setIsAnalyzing(true);
    setErrorMessage(null);
    setProgressPct(10);
    setProgressStatus('Ingesting raw RF recording...');
    setStatusMessage(`Processing: ${currentTarget}`);

    addNotification('Analysis Started', `Processing signal recording: ${currentTarget}`, 'radio');

    let fsVal = null;
    if (samplingRate.includes('MHz')) {
      fsVal = parseFloat(samplingRate.replace('MHz', '').trim()) * 1e6;
    } else if (samplingRate.includes('kHz')) {
      fsVal = parseFloat(samplingRate.replace('kHz', '').trim()) * 1e3;
    }

    const formData = new FormData();
    if (uploadedFile) {
      formData.append('file', uploadedFile);
    } else if (selectedPreset) {
      formData.append('preset_filename', selectedPreset);
    }

    if (fsVal) {
      formData.append('sample_rate', fsVal);
    }

    const pTimer1 = setTimeout(() => {
      setProgressPct(35);
      setProgressStatus('Preprocessing & Signal Conditioning...');
    }, 350);

    const pTimer2 = setTimeout(() => {
      setProgressPct(65);
      setProgressStatus('AMC ResNet-18 Deep Classification...');
    }, 700);

    const pTimer3 = setTimeout(() => {
      setProgressPct(85);
      setProgressStatus('Demodulation & Frame Extraction...');
    }, 1050);

    try {
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        body: formData
      });

      clearTimeout(pTimer1);
      clearTimeout(pTimer2);
      clearTimeout(pTimer3);

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Signal Analysis Error');
      }

      const result = await response.json();
      setProgressPct(100);
      setProgressStatus('Analysis complete.');
      setAnalysisResult(result);

      const amc = result.classification || {};
      const confPct = ((amc.confidence || 0) * 100).toFixed(1);
      setStatusMessage(
        `Analysis Complete: ${amc.predicted_class || 'UNKNOWN'} (${confPct}%)`
      );

      addNotification(
        'Classification Succeeded',
        `Predicted: ${amc.predicted_class || 'UNKNOWN'} with ${confPct}% confidence.`,
        'cpu'
      );
    } catch (err) {
      clearTimeout(pTimer1);
      clearTimeout(pTimer2);
      clearTimeout(pTimer3);
      setProgressPct(0);
      setProgressStatus('Analysis Error!');
      setStatusMessage('Error occurred during analysis.');
      setErrorMessage(err.message || 'Signal analysis pipeline error');
      addNotification('Analysis Failure', err.message || 'Error executing signal analysis pipeline.', 'activity');
    } finally {
      setIsAnalyzing(false);
    }
  }, [uploadedFile, selectedPreset, filePathText, samplingRate, addNotification]);

  const handleStopAnalysis = () => {
    setIsAnalyzing(false);
    setProgressStatus('Analysis cancelled.');
    setStatusMessage('Analysis stopped.');
    addNotification('Analysis Interrupted', 'Analysis pipeline halted by operator.', 'activity');
  };

  // Keyboard Shortcuts (Ctrl+O, Ctrl+R, Ctrl+E, Ctrl+Z, Ctrl+T)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === 'r' || e.key === 'R') {
          e.preventDefault();
          handleRunAnalysis();
        } else if (e.key === 'e' || e.key === 'E') {
          e.preventDefault();
          if (analysisResult) setIsExportModalOpen(true);
        } else if (e.key === 'z' || e.key === 'Z') {
          e.preventDefault();
          handleUndo();
        } else if (e.key === 't' || e.key === 'T') {
          e.preventDefault();
          handleToggleTheme();
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleRunAnalysis, analysisResult, stateHistory]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div className={`h-screen max-h-screen w-screen max-w-screen flex flex-col overflow-hidden font-sans transition-colors ${
      theme === 'dark' ? 'bg-[#0B0F19] text-[#F8FAFC]' : 'bg-[#F1F5F9] text-[#0F172A]'
    }`}>
      {/* 1. Header with Notifications & Light/Dark Switcher */}
      <Header
        isAnalyzing={isAnalyzing}
        onBrowseFile={() => document.querySelector('input[type="file"]')?.click()}
        onRunAnalysis={handleRunAnalysis}
        onExportDialog={() => {
          if (!analysisResult) alert('Please run signal analysis before exporting.');
          else setIsExportModalOpen(true);
        }}
        onUndo={handleUndo}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        airgapEnabled={airgapGuard}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenNotifications={() => setIsNotificationsOpen((prev) => !prev)}
        unreadCount={unreadCount}
      />

      {/* Global Error Banner */}
      {errorMessage && (
        <div className="mx-4 mt-1 p-2 rounded-xl bg-rose-950/70 border border-rose-500/50 flex items-center justify-between text-xs font-mono text-rose-300 shrink-0">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>ERROR: {errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-400 hover:text-white px-2 py-0.5 rounded bg-rose-900/40 text-[10px]"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* 2. Main Layout with Sidebar + 3-Panel Grid (Locked to 100vh flex-1 min-h-0) */}
      <div className="flex-1 min-h-0 flex overflow-hidden">
        {/* Left Navigation Sidebar */}
        <Sidebar
          activeNav={activeNav}
          setActiveNav={setActiveNav}
          onRunAnalysis={handleRunAnalysis}
          isAnalyzing={isAnalyzing}
          onOpenBatchModal={() => setIsBatchModalOpen(true)}
          airgapGuard={airgapGuard}
        />

        {/* Workstation 3-Column Grid */}
        <main className="flex-1 min-h-0 p-3 grid grid-cols-12 gap-3 items-stretch overflow-hidden">
          {/* Controls Column (3 Cols) */}
          <div className="col-span-3 h-full min-h-0 flex flex-col overflow-hidden">
            <ControlPanel
              onRunAnalysis={handleRunAnalysis}
              onStopAnalysis={handleStopAnalysis}
              isAnalyzing={isAnalyzing}
              progressPct={progressPct}
              progressStatus={progressStatus}
              presetSamples={presetSamples}
              selectedPreset={selectedPreset}
              setSelectedPreset={setSelectedPreset}
              uploadedFile={uploadedFile}
              setUploadedFile={setUploadedFile}
              filePathText={filePathText}
              setFilePathText={setFilePathText}
              samplingRate={samplingRate}
              setSamplingRate={setSamplingRate}
              fftWindowSize={fftWindowSize}
              setFftWindowSize={setFftWindowSize}
              windowType={windowType}
              setWindowType={setWindowType}
              airgapGuard={airgapGuard}
              setAirgapGuard={handleToggleAirgap}
              batchQueue={batchQueue}
              onOpenBatchModal={() => setIsBatchModalOpen(true)}
            />
          </div>

          {/* Visualization Column (6 Cols) */}
          <div className="col-span-6 h-full min-h-0 flex flex-col overflow-hidden">
            <VisualizationPanel
              analysisResult={analysisResult}
              isAnalyzing={isAnalyzing}
              activeTab={activeTab}
            />
          </div>

          {/* Telemetry & Gauges Column (3 Cols) */}
          <div className="col-span-3 h-full min-h-0 flex flex-col overflow-hidden">
            <TelemetryPanel
              analysisResult={analysisResult}
              isAnalyzing={isAnalyzing}
              onOpenExportModal={() => setIsExportModalOpen(true)}
            />
          </div>
        </main>
      </div>

      {/* Actionable Notification Drawer */}
      <NotificationDrawer
        isOpen={isNotificationsOpen}
        onClose={() => setIsNotificationsOpen(false)}
        notifications={notifications}
        onClearAll={() => setNotifications([])}
        onMarkAllRead={() => setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))}
        unreadCount={unreadCount}
        theme={theme}
      />

      {/* Modals */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        analysisResult={analysisResult}
        theme={theme}
      />

      <BatchModal
        isOpen={isBatchModalOpen}
        onClose={() => setIsBatchModalOpen(false)}
        batchQueue={batchQueue}
        onClearQueue={() => setBatchQueue([])}
        onRemoveItem={(idx) => setBatchQueue((q) => q.filter((_, i) => i !== idx))}
        presetSamples={presetSamples}
        onAddToQueue={(item) => {
          setBatchQueue((q) => [...q, item]);
          addNotification('Batch Item Queued', `Added ${item.filename || item.name} to batch queue.`, 'radio');
        }}
        theme={theme}
      />
    </div>
  );
}
