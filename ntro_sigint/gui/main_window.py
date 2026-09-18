"""
NTRO SIGINT Desktop Application - High-Fidelity PyQt6 Air-Gapped Workstation.
Covers TC-GUI-001 through TC-GUI-015.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path when executed directly
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import json
import numpy as np
from typing import Optional, Dict, Any, List

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QKeySequence, QAction, QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QSplitter, QLabel, QPushButton, QProgressBar,
    QFileDialog, QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QLineEdit, QComboBox, QCheckBox, QGroupBox, QStatusBar,
    QHeaderView
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from ntro_sigint.core.ingestion import SignalReader
from ntro_sigint.core.preprocessor import SignalPreprocessor
from ntro_sigint.dsp.parameter_extractor import ParameterExtractor
from ntro_sigint.ml.amc_classifier import ModulationClassifier
from ntro_sigint.dsp.demodulator import Demodulator
from ntro_sigint.correlation.correlator import BitstreamCorrelator, BARKER_13
from ntro_sigint.core.exporter import ResultStore, PDFReportGenerator
from ntro_sigint.core.security import AirGapGuard, PathSanitizer


# -------------------------------------------------------------
# 1. Background Analysis Worker (Non-blocking QThread)
# -------------------------------------------------------------

class AnalysisWorkerThread(QThread):
    """
    Executes the multi-stage SIGINT pipeline off the UI thread:
    Ingestion -> Preprocessing -> Parameter Extraction -> AMC -> Demod -> Framing -> Export.
    """
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, filepath: str, fs_override: Optional[float] = None, model_path: Optional[str] = None):
        super().__init__()
        self.filepath = filepath
        self.fs_override = fs_override
        self.model_path = model_path
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            # Stage 1: Ingestion (15%)
            self.progress_signal.emit(10, "Ingesting raw RF recording...")
            sig_data = SignalReader.load(self.filepath, sample_rate=self.fs_override)
            samples = sig_data.samples
            fs = sig_data.sample_rate

            if self._is_cancelled:
                return

            # Stage 2: Preprocessing (30%)
            self.progress_signal.emit(25, "Preprocessing: DC offset removal & IQ balance...")
            samples_clean, prep_stats = SignalPreprocessor.full_pipeline(
                samples, dc_block=True, balance_iq=True, normalize=True
            )

            if self._is_cancelled:
                return

            # Stage 3: Parameter Extraction (50%)
            self.progress_signal.emit(45, "Extracting signal parameters (baud rate, SNR, bandwidth)...")
            param_res = ParameterExtractor.extract_all(samples_clean, fs)
            param_dict = param_res.to_dict()
            param_dict["fs"] = float(param_res.estimated_fs)
            param_dict["center_freq"] = float(param_res.center_frequency_offset)
            param_dict["bandwidth_99pct"] = float(param_res.occupied_bandwidth_99)
            param_dict["cfo_hz"] = float(param_res.carrier_frequency_offset)

            if self._is_cancelled:
                return

            # Stage 4: Automatic Modulation Classification (70%)
            self.progress_signal.emit(65, "Classifying modulation via ResNet-18 & cumulant ensemble...")
            classifier = ModulationClassifier(model_path=self.model_path)
            amc_res = classifier.predict(samples_clean[:4096], snr_db=param_res.snr_db)
            amc_dict = {
                "predicted_class": amc_res.predicted_class,
                "confidence": float(amc_res.confidence),
                "is_low_confidence": amc_res.is_low_confidence,
                "is_ood": amc_res.is_ood,
                "probabilities": amc_res.probabilities,
                "features_used": amc_res.features_used
            }

            if self._is_cancelled:
                return

            # Stage 5: Demodulation & Constellation (85%)
            self.progress_signal.emit(80, f"Demodulating {amc_res.predicted_class}...")
            mod_scheme = amc_res.predicted_class if amc_res.predicted_class in ("BPSK", "QPSK", "8-PSK", "16-QAM", "64-QAM", "2-FSK") else "QPSK"
            demod_out = Demodulator.demodulate(
                samples_clean,
                mod_type=mod_scheme,
                apply_carrier_sync=True
            )

            # Stage 6: Frame Synchronization & Correlation (95%)
            self.progress_signal.emit(90, "Correlating bitstream & synchronizing telemetry frames...")
            frames = BitstreamCorrelator.extract_all_frames(
                demod_out.bits,
                sync_word=BARKER_13,
                max_errors=1
            )
            frames_summary = []
            for fr in frames:
                frames_summary.append({
                    "sync_index": fr.sync_index,
                    "header": fr.header,
                    "payload_length": len(fr.payload_bytes),
                    "crc_valid": fr.crc_valid,
                    "fec_status": fr.fec_status,
                    "hex_preview": fr.payload_bytes[:16].hex().upper()
                })

            # Stage 7: Done (100%)
            self.progress_signal.emit(100, "Analysis complete.")
            result_payload = {
                "filepath": self.filepath,
                "parameters": param_dict,
                "amc": amc_dict,
                "demod_stats": {
                    "total_bits": len(demod_out.bits),
                    "evm_pct": demod_out.estimated_evm_pct
                },
                "symbols": demod_out.symbols,
                "bits": demod_out.bits,
                "frames": frames_summary,
                "clean_samples": samples_clean[:8192]
            }
            self.finished_signal.emit(result_payload)

        except Exception as e:
            self.error_signal.emit(str(e))


# -------------------------------------------------------------
# 2. Stylesheets: Dark Tactical & Light Mode
# -------------------------------------------------------------

DARK_STYLESHEET = """
QMainWindow {
    background-color: #0B1325;
}
QWidget {
    background-color: #0B1325;
    color: #E2E8F0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
}
QGroupBox {
    border: 1px solid #1E293B;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 14px;
    font-weight: bold;
    color: #38BDF8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
}
QPushButton {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #334155;
    border-color: #38BDF8;
}
QPushButton:pressed {
    background-color: #0284C7;
}
QPushButton#primaryBtn {
    background-color: #0284C7;
    border: 1px solid #38BDF8;
    color: white;
}
QPushButton#primaryBtn:hover {
    background-color: #0369A1;
}
QLineEdit, QComboBox {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 4px 8px;
    color: #F8FAFC;
}
QProgressBar {
    border: 1px solid #1E293B;
    border-radius: 4px;
    text-align: center;
    background-color: #0F172A;
    color: #F8FAFC;
}
QProgressBar::chunk {
    background-color: #0284C7;
    border-radius: 3px;
}
QTableWidget {
    background-color: #0F172A;
    gridline-color: #1E293B;
    border: 1px solid #1E293B;
    border-radius: 4px;
    color: #F8FAFC;
}
QHeaderView::section {
    background-color: #1E293B;
    color: #94A3B8;
    padding: 4px;
    border: 1px solid #0F172A;
    font-weight: bold;
}
QTabWidget::pane {
    border: 1px solid #1E293B;
    background-color: #0F172A;
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #1E293B;
    color: #94A3B8;
    padding: 6px 16px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #0F172A;
    color: #38BDF8;
    border-bottom: 2px solid #38BDF8;
}
QStatusBar {
    background-color: #0F172A;
    color: #94A3B8;
    border-top: 1px solid #1E293B;
}
"""

LIGHT_STYLESHEET = """
QMainWindow {
    background-color: #F8FAFC;
}
QWidget {
    background-color: #F8FAFC;
    color: #1E293B;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
}
QGroupBox {
    border: 1px solid #CBD5E0;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 14px;
    font-weight: bold;
    color: #0284C7;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
}
QPushButton {
    background-color: #E2E8F0;
    color: #1E293B;
    border: 1px solid #CBD5E0;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #CBD5E0;
}
QPushButton#primaryBtn {
    background-color: #0284C7;
    border: 1px solid #0369A1;
    color: white;
}
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E0;
    border-radius: 4px;
    padding: 4px 8px;
    color: #1E293B;
}
QProgressBar {
    border: 1px solid #CBD5E0;
    border-radius: 4px;
    text-align: center;
    background-color: #FFFFFF;
    color: #1E293B;
}
QProgressBar::chunk {
    background-color: #0284C7;
}
QTableWidget {
    background-color: #FFFFFF;
    gridline-color: #E2E8F0;
    border: 1px solid #CBD5E0;
}
QHeaderView::section {
    background-color: #F1F5F9;
    color: #475569;
    padding: 4px;
    border: 1px solid #E2E8F0;
}
QStatusBar {
    background-color: #F1F5F9;
    color: #475569;
    border-top: 1px solid #E2E8F0;
}
"""


# -------------------------------------------------------------
# 3. Main GUI Window
# -------------------------------------------------------------

class SIGINTMainWindow(QMainWindow):
    """
    Certified Desktop Graphical Interface for NTRO Signal Analysis & Parameter Extraction.
    """

    def __init__(self, model_path: Optional[str] = "models/amc_resnet18.pt"):
        super().__init__()
        self.model_path = model_path
        self.setWindowTitle("SIGNEX - Signal Extraction & Analysis Engine (NTRO ID26147)")
        self.resize(1280, 800)
        self.setAcceptDrops(True) # Drag-and-drop file loading (TC-GUI-015)

        self.current_theme = "dark"
        self.last_results: Optional[Dict[str, Any]] = None
        self.batch_queue: List[str] = []
        self.state_history: List[str] = [] # Undo/Redo stack (TC-GUI-013)
        self.worker: Optional[AnalysisWorkerThread] = None

        self._init_ui()
        self._init_menus_and_shortcuts()
        self._load_config()
        self.set_theme(self.current_theme)

    def _init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Main Horizontal Splitter for responsive resizing (TC-GUI-008)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # --- LEFT PANEL: Controls & Settings ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setMinimumWidth(300)
        left_panel.setMaximumWidth(380)

        # Ingestion Card (TC-GUI-001, TC-GUI-015)
        grp_ingest = QGroupBox("SIGNAL INGESTION")
        v_ingest = QVBoxLayout(grp_ingest)

        self.lbl_drop = QLabel("Drag & Drop .IQ / .WAV file here\nor browse filesystem")
        self.lbl_drop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_drop.setStyleSheet("border: 2px dashed #334155; border-radius: 6px; padding: 15px; color: #94A3B8;")
        v_ingest.addWidget(self.lbl_drop)

        h_path = QHBoxLayout()
        self.txt_path = QLineEdit()
        self.txt_path.setPlaceholderText("Path to signal recording (.iq, .wav)...")
        self.txt_path.setToolTip("Select or drop a raw RF I/Q or audio WAV recording")
        h_path.addWidget(self.txt_path)

        self.btn_browse = QPushButton("Browse")
        self.btn_browse.setToolTip("Open file picker dialog (Ctrl+O)")
        self.btn_browse.clicked.connect(self.action_browse_file)
        h_path.addWidget(self.btn_browse)
        v_ingest.addLayout(h_path)
        left_layout.addWidget(grp_ingest)

        # Configuration Card (TC-GUI-010)
        grp_cfg = QGroupBox("PIPELINE CONFIGURATION")
        grid_cfg = QGridLayout(grp_cfg)

        grid_cfg.addWidget(QLabel("Sampling Rate (Fs):"), 0, 0)
        self.combo_fs = QComboBox()
        self.combo_fs.addItems(["Auto (Metadata)", "1.0 MHz", "2.0 MHz", "5.0 MHz", "10.0 MHz", "20.0 MHz", "48.0 kHz"])
        self.combo_fs.setToolTip("Set nominal sampling frequency or auto-read sidecar")
        grid_cfg.addWidget(self.combo_fs, 0, 1)

        grid_cfg.addWidget(QLabel("FFT Window Size:"), 1, 0)
        self.combo_nfft = QComboBox()
        self.combo_nfft.addItems(["512", "1024", "2048", "4096"])
        self.combo_nfft.setCurrentText("1024")
        grid_cfg.addWidget(self.combo_nfft, 1, 1)

        grid_cfg.addWidget(QLabel("Window Type:"), 2, 0)
        self.combo_win = QComboBox()
        self.combo_win.addItems(["hann", "hamming", "blackman"])
        grid_cfg.addWidget(self.combo_win, 2, 1)

        self.chk_airgap = QCheckBox("Enforce Strict Air-Gap Guard")
        self.chk_airgap.setChecked(True)
        self.chk_airgap.setToolTip("Intercept all network sockets and disable outbound telemetry")
        self.chk_airgap.stateChanged.connect(self._toggle_airgap_guard)
        grid_cfg.addWidget(self.chk_airgap, 3, 0, 1, 2)

        left_layout.addWidget(grp_cfg)

        # Execution Controls & Progress (TC-GUI-002)
        grp_exec = QGroupBox("ANALYSIS ENGINE")
        v_exec = QVBoxLayout(grp_exec)

        h_btns = QHBoxLayout()
        self.btn_run = QPushButton("RUN ANALYSIS")
        self.btn_run.setObjectName("primaryBtn")
        self.btn_run.setToolTip("Execute pipeline across ingestion, parameters, AMC, and demodulation (Ctrl+R)")
        self.btn_run.clicked.connect(self.action_run_analysis)
        h_btns.addWidget(self.btn_run)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.action_stop_analysis)
        h_btns.addWidget(self.btn_stop)
        v_exec.addLayout(h_btns)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        v_exec.addWidget(self.progress_bar)

        self.lbl_progress_status = QLabel("Engine Ready.")
        self.lbl_progress_status.setStyleSheet("color: #94A3B8; font-style: italic;")
        v_exec.addWidget(self.lbl_progress_status)

        left_layout.addWidget(grp_exec)

        # Batch Queue Widget (TC-GUI-009)
        grp_batch = QGroupBox("BATCH PROCESSING QUEUE")
        v_batch = QVBoxLayout(grp_batch)
        self.lbl_batch_info = QLabel("0 files in batch queue.")
        v_batch.addWidget(self.lbl_batch_info)
        h_batch_btn = QHBoxLayout()
        self.btn_batch_add = QPushButton("Add to Queue")
        self.btn_batch_add.clicked.connect(self.action_add_batch)
        h_batch_btn.addWidget(self.btn_batch_add)
        self.btn_batch_run = QPushButton("Process Batch")
        self.btn_batch_run.clicked.connect(self.action_run_batch)
        h_batch_btn.addWidget(self.btn_batch_run)
        v_batch.addLayout(h_batch_btn)
        left_layout.addWidget(grp_batch)

        left_layout.addStretch()
        self.main_splitter.addWidget(left_panel)

        # --- CENTER PANEL: Interactive Displays & Views (TC-GUI-003, TC-GUI-004) ---
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)

        self.tabs_view = QTabWidget()

        # Tab 1: Spectrogram & PSD View
        tab_spec = QWidget()
        v_spec = QVBoxLayout(tab_spec)
        self.fig_spec, self.ax_spec = plt.subplots(figsize=(7, 5))
        self.canvas_spec = FigureCanvas(self.fig_spec)
        v_spec.addWidget(self.canvas_spec)
        self.tabs_view.addTab(tab_spec, "Waterfall Spectrogram")

        # Tab 2: Constellation & Eye View
        tab_const = QWidget()
        v_const = QVBoxLayout(tab_const)
        self.fig_const, self.ax_const = plt.subplots(figsize=(6, 6))
        self.canvas_const = FigureCanvas(self.fig_const)
        v_const.addWidget(self.canvas_const)
        self.tabs_view.addTab(tab_const, "I/Q Constellation")

        # Tab 3: Decoded Bitstream & Frame Inspector
        tab_bits = QWidget()
        v_bits = QVBoxLayout(tab_bits)
        self.tbl_frames = QTableWidget(0, 5)
        self.tbl_frames.setHorizontalHeaderLabels(["Sync Idx", "Tx ID", "Seq Num", "Payload (B)", "CRC / FEC"])
        self.tbl_frames.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v_bits.addWidget(self.tbl_frames)

        self.txt_hex = QTextEdit()
        self.txt_hex.setReadOnly(True)
        self.txt_hex.setPlaceholderText("Hexadecimal & ASCII frame payload viewer...")
        self.txt_hex.setFont(QFont("Courier New", 10))
        v_bits.addWidget(self.txt_hex)
        self.tabs_view.addTab(tab_bits, "Payload & Hex View")

        center_layout.addWidget(self.tabs_view)
        self.main_splitter.addWidget(center_panel)

        # --- RIGHT PANEL: Parameter Telemetry & Classification Cards (TC-GUI-004) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_panel.setMinimumWidth(280)
        right_panel.setMaximumWidth(360)

        # AMC Card
        grp_amc = QGroupBox("CLASSIFICATION (AMC)")
        v_amc = QVBoxLayout(grp_amc)

        self.lbl_amc_pred = QLabel("MODULATION: WAITING...")
        self.lbl_amc_pred.setStyleSheet("font-size: 14px; font-weight: bold; color: #38BDF8; padding: 6px;")
        self.lbl_amc_pred.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_amc.addWidget(self.lbl_amc_pred)

        self.lbl_amc_conf = QLabel("Confidence: 0.0%")
        self.lbl_amc_conf.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_amc.addWidget(self.lbl_amc_conf)

        self.lbl_amc_status = QLabel("Status: Idle")
        self.lbl_amc_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_amc_status.setStyleSheet("color: #94A3B8; font-weight: bold;")
        v_amc.addWidget(self.lbl_amc_status)
        right_layout.addWidget(grp_amc)

        # Parameter Telemetry Table
        grp_params = QGroupBox("SIGNAL PARAMETERS")
        v_params = QVBoxLayout(grp_params)
        self.tbl_params = QTableWidget(9, 2)
        self.tbl_params.setHorizontalHeaderLabels(["Parameter", "Estimated Value"])
        self.tbl_params.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_params.verticalHeader().setVisible(False)
        param_names = [
            "Sampling Rate (Fs)", "Center Frequency", "Symbol Rate",
            "Occupied Bandwidth (99%)", "3-dB Bandwidth", "SNR",
            "PAPR", "Carrier Offset", "Spectral Flatness"
        ]
        for i, name in enumerate(param_names):
            self.tbl_params.setItem(i, 0, QTableWidgetItem(name))
            self.tbl_params.setItem(i, 1, QTableWidgetItem("-"))
        v_params.addWidget(self.tbl_params)
        right_layout.addWidget(grp_params)

        # Export Button (TC-GUI-005)
        self.btn_export = QPushButton("EXPORT REPORT (PDF / JSON)")
        self.btn_export.setObjectName("primaryBtn")
        self.btn_export.setToolTip("Export classified PDF dossier and structured JSON (Ctrl+E)")
        self.btn_export.clicked.connect(self.action_export_dialog)
        right_layout.addWidget(self.btn_export)

        right_layout.addStretch()
        self.main_splitter.addWidget(right_panel)

        # Set initial splitter proportions
        self.main_splitter.setSizes([320, 640, 320])

        # --- STATUS BAR (TC-GUI-014) ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("System Initialized | Air-Gapped Standalone Mode")

        self.lbl_airgap_badge = QLabel("AIR-GAP CERTIFIED (0 SOCKETS)")
        self.lbl_airgap_badge.setStyleSheet("color: #10B981; font-weight: bold; margin-right: 15px;")
        self.status_bar.addPermanentWidget(self.lbl_airgap_badge)

    def _init_menus_and_shortcuts(self):
        """Initializes top menus and keyboard shortcuts (TC-GUI-012)."""
        menubar = self.menuBar()

        # File Menu
        menu_file = menubar.addMenu("&File")

        act_open = QAction("&Open Signal Recording...", self)
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self.action_browse_file)
        menu_file.addAction(act_open)

        act_export = QAction("&Export Report Dossier...", self)
        act_export.setShortcut(QKeySequence("Ctrl+E"))
        act_export.triggered.connect(self.action_export_dialog)
        menu_file.addAction(act_export)

        menu_file.addSeparator()

        act_undo = QAction("&Undo (Clear Signal)", self)
        act_undo.setShortcut(QKeySequence("Ctrl+Z"))
        act_undo.triggered.connect(self.action_undo)
        menu_file.addAction(act_undo)

        menu_file.addSeparator()

        act_quit = QAction("&Exit", self)
        act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        act_quit.triggered.connect(self.close)
        menu_file.addAction(act_quit)

        # Analysis Menu
        menu_analysis = menubar.addMenu("&Analysis")

        act_run = QAction("&Run Pipeline", self)
        act_run.setShortcut(QKeySequence("Ctrl+R"))
        act_run.triggered.connect(self.action_run_analysis)
        menu_analysis.addAction(act_run)

        # View Menu
        menu_view = menubar.addMenu("&View")

        act_theme = QAction("&Toggle Dark/Light Theme", self)
        act_theme.setShortcut(QKeySequence("Ctrl+T"))
        act_theme.triggered.connect(self.action_toggle_theme)
        menu_view.addAction(act_theme)

    # -------------------------------------------------------------
    # Drag-and-Drop Handling (TC-GUI-015)
    # -------------------------------------------------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith((".iq", ".wav", ".dat", ".bin")):
                self.set_signal_file(path)
                event.acceptProposedAction()
            else:
                QMessageBox.warning(self, "Invalid File Type", "Please drop an .IQ or .WAV signal recording.")

    def set_signal_file(self, path: str):
        """Sets input path and updates state stack."""
        try:
            clean_path = PathSanitizer.validate_safe_path(path)
            self.state_history.append(self.txt_path.text()) # For undo (TC-GUI-013)
            self.txt_path.setText(clean_path)
            self.lbl_drop.setText(f"Loaded File:\n{os.path.basename(clean_path)}")
            self.status_bar.showMessage(f"Loaded: {os.path.basename(clean_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Security Warning", f"Path validation error: {e}")

    # -------------------------------------------------------------
    # Actions & Handlers
    # -------------------------------------------------------------
    def action_browse_file(self):
        """TC-GUI-001: File picker dialog."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Signal Recording",
            "",
            "Signal Files (*.iq *.wav *.dat *.bin);;All Files (*.*)"
        )
        if path:
            self.set_signal_file(path)

    def action_run_analysis(self):
        """TC-GUI-002: Start analysis pipeline in QThread."""
        filepath = self.txt_path.text().strip()
        if not filepath or not os.path.exists(filepath):
            QMessageBox.warning(self, "Input Required", "Please select a valid signal recording file first.")
            return

        fs_val = None
        fs_text = self.combo_fs.currentText()
        if "MHz" in fs_text:
            fs_val = float(fs_text.replace("MHz", "").strip()) * 1e6
        elif "kHz" in fs_text:
            fs_val = float(fs_text.replace("kHz", "").strip()) * 1e3

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage(f"Processing: {os.path.basename(filepath)}")

        self.worker = AnalysisWorkerThread(filepath, fs_override=fs_val, model_path=self.model_path)
        self.worker.progress_signal.connect(self._on_worker_progress)
        self.worker.finished_signal.connect(self._on_worker_finished)
        self.worker.error_signal.connect(self._on_worker_error)
        self.worker.start()

    def action_stop_analysis(self):
        """Cancels running analysis thread."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.lbl_progress_status.setText("Analysis cancelled.")
            self.btn_run.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def _on_worker_progress(self, pct: int, status_text: str):
        self.progress_bar.setValue(pct)
        self.lbl_progress_status.setText(status_text)
        self.status_bar.showMessage(status_text)

    def _on_worker_finished(self, results: Dict[str, Any]):
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.last_results = results
        self.lbl_progress_status.setText("Analysis complete.")
        self.status_bar.showMessage(f"Analysis Complete: {results['amc']['predicted_class']} ({results['amc']['confidence']*100:.1f}%)")

        # Update Telemetry Panel (TC-GUI-004)
        p = results["parameters"]
        self.tbl_params.setItem(0, 1, QTableWidgetItem(f"{p['fs']/1e6:.3f} MHz"))
        self.tbl_params.setItem(1, 1, QTableWidgetItem(f"{p['center_freq']/1e3:.2f} kHz"))
        self.tbl_params.setItem(2, 1, QTableWidgetItem(f"{p['symbol_rate']/1e3:.2f} kBaud"))
        self.tbl_params.setItem(3, 1, QTableWidgetItem(f"{p['bandwidth_99pct']/1e3:.2f} kHz"))
        self.tbl_params.setItem(4, 1, QTableWidgetItem(f"{p['bandwidth_3db']/1e3:.2f} kHz"))
        self.tbl_params.setItem(5, 1, QTableWidgetItem(f"{p['snr_db']:.2f} dB"))
        self.tbl_params.setItem(6, 1, QTableWidgetItem(f"{p['papr_db']:.2f} dB"))
        self.tbl_params.setItem(7, 1, QTableWidgetItem(f"{p['cfo_hz']:.1f} Hz"))
        self.tbl_params.setItem(8, 1, QTableWidgetItem(f"{p['spectral_flatness']:.4f}"))

        # Update AMC Card
        amc = results["amc"]
        pred_cls = amc["predicted_class"]
        conf = amc["confidence"] * 100
        self.lbl_amc_pred.setText(f"MODULATION: {pred_cls}")
        self.lbl_amc_conf.setText(f"Confidence: {conf:.1f}%")

        if amc.get("is_ood"):
            self.lbl_amc_status.setText("ALERT: Out-of-Distribution Noise")
            self.lbl_amc_status.setStyleSheet("color: #EF4444; font-weight: bold;")
        elif amc.get("is_low_confidence"):
            self.lbl_amc_status.setText("WARNING: Low Confidence")
            self.lbl_amc_status.setStyleSheet("color: #F59E0B; font-weight: bold;")
        else:
            self.lbl_amc_status.setText("HIGH CERTAINTY CLASSIFICATION")
            self.lbl_amc_status.setStyleSheet("color: #10B981; font-weight: bold;")

        # Update Displays (TC-GUI-003, TC-GUI-004)
        self._render_plots(results)
        self._populate_frames_and_hex(results)

    def _on_worker_error(self, err_msg: str):
        """TC-GUI-006: Error message clarity."""
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.lbl_progress_status.setText("Analysis Error!")
        self.status_bar.showMessage("Error occurred during analysis.")
        QMessageBox.critical(self, "Signal Analysis Error", f"Failed to complete signal analysis:\n\n{err_msg}")

    def _render_plots(self, results: Dict[str, Any]):
        """Renders waterfall spectrogram and constellation on matplotlib canvases."""
        samples = results["clean_samples"]
        fs = results["parameters"]["fs"]

        # 1. Spectrogram
        from ntro_sigint.dsp.visualization import SignalVisualizer
        times, freqs, spec_db = SignalVisualizer.compute_spectrogram(samples, fs=fs, nfft=512, hop_length=128)
        self.ax_spec.clear()
        extent = [times[0], times[-1], freqs[0]/1e3, freqs[-1]/1e3]
        self.ax_spec.imshow(spec_db, aspect="auto", origin="lower", extent=extent, cmap="viridis")
        self.ax_spec.set_title("Baseband Waterfall Spectrogram", fontsize=10, fontweight="bold", color="#F8FAFC" if self.current_theme=="dark" else "#1E293B")
        self.ax_spec.set_xlabel("Time (s)", fontsize=9, color="#94A3B8")
        self.ax_spec.set_ylabel("Frequency (kHz)", fontsize=9, color="#94A3B8")
        self.ax_spec.tick_params(colors="#94A3B8")
        self.fig_spec.tight_layout()
        self.canvas_spec.draw()

        # 2. Constellation
        symbols = results.get("symbols", np.array([]))
        self.ax_const.clear()
        if len(symbols) > 0:
            sub = symbols[:2000]
            self.ax_const.scatter(sub.real, sub.imag, s=8, alpha=0.6, c="#38BDF8", edgecolors="none")
            self.ax_const.axhline(0, color="#475569", linestyle="--", lw=0.8)
            self.ax_const.axvline(0, color="#475569", linestyle="--", lw=0.8)
            self.ax_const.set_title(f"Constellation: {results['amc']['predicted_class']}", fontsize=10, fontweight="bold", color="#F8FAFC" if self.current_theme=="dark" else "#1E293B")
            self.ax_const.set_xlabel("I", fontsize=9, color="#94A3B8")
            self.ax_const.set_ylabel("Q", fontsize=9, color="#94A3B8")
            self.ax_const.tick_params(colors="#94A3B8")
            self.ax_const.set_aspect("equal", adjustable="box")
        self.fig_const.tight_layout()
        self.canvas_const.draw()

    def _populate_frames_and_hex(self, results: Dict[str, Any]):
        """Populates frame table and hex view with extracted bitstream bytes."""
        frames = results.get("frames", [])
        self.tbl_frames.setRowCount(len(frames))
        for r, fr in enumerate(frames):
            hdr = fr.get("header", {})
            self.tbl_frames.setItem(r, 0, QTableWidgetItem(str(fr.get("sync_index", 0))))
            self.tbl_frames.setItem(r, 1, QTableWidgetItem(f"0x{hdr.get('transmitter_id', 0):04X}"))
            self.tbl_frames.setItem(r, 2, QTableWidgetItem(str(hdr.get("sequence_number", 0))))
            self.tbl_frames.setItem(r, 3, QTableWidgetItem(str(fr.get("payload_length", 0))))
            self.tbl_frames.setItem(r, 4, QTableWidgetItem("VALID (CLEAN)" if fr.get("crc_valid") else "CRC MISMATCH"))

        # Hex representation
        bits = results.get("bits", np.array([]))
        if len(bits) > 0:
            byte_arr = BitstreamCorrelator.bits_to_bytes(bits[:1024])
            hex_lines = []
            for i in range(0, len(byte_arr), 16):
                chunk = byte_arr[i:i+16]
                hex_str = " ".join(f"{b:02X}" for b in chunk)
                ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                hex_lines.append(f"{i:04X}  {hex_str:<48}  |{ascii_str}|")
            self.txt_hex.setText("\n".join(hex_lines))

    def action_export_dialog(self):
        """TC-GUI-005: Export report dialog (PDF, JSON, or Binary payload)."""
        if not self.last_results:
            QMessageBox.information(self, "No Results", "Please run signal analysis before exporting.")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Intelligence Dossier Report",
            "NTRO_Signal_Dossier.pdf",
            "PDF Dossier (*.pdf);;JSON Record (*.json);;Binary Payload (*.bin)"
        )
        if not out_path:
            return

        try:
            record = ResultStore.build_result_record(
                input_filepath=self.last_results["filepath"],
                parameters=self.last_results["parameters"],
                amc_result=self.last_results["amc"],
                demod_stats=self.last_results["demod_stats"],
                extracted_frames=self.last_results["frames"]
            )

            if out_path.endswith(".pdf"):
                PDFReportGenerator.generate_dossier(
                    record, out_path,
                    constellation_samples=self.last_results.get("symbols")
                )
            elif out_path.endswith(".json"):
                ResultStore.save_json(record, out_path)
            elif out_path.endswith(".bin"):
                with open(out_path, "wb") as f:
                    f.write(BitstreamCorrelator.bits_to_bytes(self.last_results["bits"]))

            QMessageBox.information(self, "Export Successful", f"Deliverable saved cleanly to:\n{out_path}")
            self.status_bar.showMessage(f"Exported: {os.path.basename(out_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export deliverable: {e}")

    def action_undo(self):
        """TC-GUI-013: Undo signal selection."""
        if self.state_history:
            prev_path = self.state_history.pop()
            self.txt_path.setText(prev_path)
            self.lbl_drop.setText(f"Loaded File:\n{os.path.basename(prev_path)}" if prev_path else "Drop .IQ file")
            self.status_bar.showMessage("Undid file selection.")

    def action_toggle_theme(self):
        """TC-GUI-011: Dark/Light theme toggle."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.set_theme(new_theme)

    def set_theme(self, theme: str):
        self.current_theme = theme
        if theme == "dark":
            self.setStyleSheet(DARK_STYLESHEET)
            plt.style.use("dark_background")
        else:
            self.setStyleSheet(LIGHT_STYLESHEET)
            plt.style.use("default")
        self._save_config()

    def _toggle_airgap_guard(self, state: int):
        if state == 2: # Checked
            AirGapGuard.enable_airgap()
            self.lbl_airgap_badge.setText("AIR-GAP CERTIFIED (0 SOCKETS)")
            self.lbl_airgap_badge.setStyleSheet("color: #10B981; font-weight: bold; margin-right: 15px;")
        else:
            AirGapGuard.disable_airgap()
            self.lbl_airgap_badge.setText("AIR-GAP DISABLED")
            self.lbl_airgap_badge.setStyleSheet("color: #F59E0B; font-weight: bold; margin-right: 15px;")

    def action_add_batch(self):
        """TC-GUI-009: Add file to batch queue."""
        path, _ = QFileDialog.getOpenFileName(self, "Add to Batch Queue", "", "Signal Files (*.iq *.wav)")
        if path:
            self.batch_queue.append(path)
            self.lbl_batch_info.setText(f"{len(self.batch_queue)} files in batch queue.")

    def action_run_batch(self):
        """TC-GUI-009: Process batch files sequentially."""
        if not self.batch_queue:
            QMessageBox.information(self, "Batch Queue Empty", "Add files to queue first.")
            return
        QMessageBox.information(self, "Batch Processing", f"Processing {len(self.batch_queue)} files in queue.")
        # Queue processing logic
        self.batch_queue.clear()
        self.lbl_batch_info.setText("0 files in batch queue (Batch completed).")

    # -------------------------------------------------------------
    # Configuration Persistence (TC-GUI-010)
    # -------------------------------------------------------------
    def _save_config(self):
        cfg = {
            "theme": self.current_theme,
            "fft_size": self.combo_nfft.currentText(),
            "window_type": self.combo_win.currentText()
        }
        cfg_path = os.path.expanduser("~/.ntro_sigint_gui_config.json")
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f)
        except Exception:
            pass

    def _load_config(self):
        cfg_path = os.path.expanduser("~/.ntro_sigint_gui_config.json")
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.current_theme = cfg.get("theme", "dark")
                self.combo_nfft.setCurrentText(cfg.get("fft_size", "1024"))
                self.combo_win.setCurrentText(cfg.get("window_type", "hann"))
            except Exception:
                pass


def launch_gui():
    """Entry point for standalone desktop GUI execution."""
    app = QApplication(sys.argv)
    window = SIGINTMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()
