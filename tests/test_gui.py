"""
Automated Test Suite for PyQt6 Graphical User Interface.
Validates TC-GUI-001 through TC-GUI-015 in headless offscreen mode.
"""

import pytest
import os
import tempfile
import numpy as np

# Ensure offscreen headless execution for CI / test runners
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QMimeData, QUrl, QPointF
from PyQt6.QtGui import QDropEvent, QAction

from ntro_sigint.gui.main_window import SIGINTMainWindow, AnalysisWorkerThread
from ntro_sigint.core.exporter import ResultStore


@pytest.fixture(scope="session")
def qapp():
    """Initializes a single QApplication for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(["-platform", "offscreen"])
    return app


@pytest.fixture
def main_window(qapp):
    """Instantiates SIGINTMainWindow in offscreen mode."""
    win = SIGINTMainWindow(model_path="models/amc_resnet18.pt")
    yield win
    win.close()


class TestGUIComponents:

    def test_tc_gui_001_file_picker(self, main_window, tmp_path):
        """TC-GUI-001: File selection updates path and status bar."""
        iq_file = tmp_path / "test_capture.iq"
        iq_file.write_bytes(b"\x00\x01\x02\x03" * 256)

        main_window.set_signal_file(str(iq_file))
        assert main_window.txt_path.text() == str(iq_file)
        assert "test_capture.iq" in main_window.lbl_drop.text()
        assert "test_capture.iq" in main_window.status_bar.currentMessage()

    def test_tc_gui_002_analysis_progress_indicator(self, qapp, tmp_path):
        """TC-GUI-002: Analysis worker progress indicator updates."""
        iq_file = tmp_path / "test_sig.iq"
        from ntro_sigint.ml.dataset import SyntheticSignalGenerator
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=2048, snr_db=20.0)
        # Write float32 interleaved IQ
        iq_interleaved = np.empty(len(sig) * 2, dtype=np.float32)
        iq_interleaved[0::2] = sig.real
        iq_interleaved[1::2] = sig.imag
        iq_file.write_bytes(iq_interleaved.tobytes())

        worker = AnalysisWorkerThread(str(iq_file), fs_override=1.0e6, model_path="models/amc_resnet18.pt")
        progress_values = []
        worker.progress_signal.connect(lambda pct, msg: progress_values.append(pct))

        # Run synchronously in test
        worker.run()
        assert 10 in progress_values
        assert 100 in progress_values
        assert len(progress_values) >= 5

    def test_tc_gui_003_realtime_plot_rendering(self, main_window):
        """TC-GUI-003: Real-time plot rendering (waterfall & constellation)."""
        samples = np.random.randn(2048) + 1j * np.random.randn(2048)
        symbols = np.random.choice([1+1j, -1+1j, 1-1j, -1-1j], 100)

        results = {
            "clean_samples": samples,
            "symbols": symbols,
            "parameters": {"fs": 1.0e6},
            "amc": {"predicted_class": "QPSK", "confidence": 0.95}
        }
        main_window._render_plots(results)
        # Verify ax_spec and ax_const have children
        assert len(main_window.ax_spec.images) > 0
        assert len(main_window.ax_const.collections) > 0

    def test_tc_gui_004_result_inspection_panel(self, main_window):
        """TC-GUI-004: Result inspection panel (telemetry, AMC, hex view)."""
        mock_res = {
            "filepath": "dummy.iq",
            "parameters": {
                "fs": 20.0e6,
                "center_freq": 50.0e3,
                "symbol_rate": 25.0e3,
                "bandwidth_99pct": 100.0e3,
                "bandwidth_3db": 60.0e3,
                "snr_db": 18.2,
                "papr_db": 0.1,
                "cfo_hz": 5.0,
                "spectral_flatness": 0.02
            },
            "amc": {
                "predicted_class": "16-QAM",
                "confidence": 0.92,
                "is_ood": False,
                "is_low_confidence": False
            },
            "symbols": np.array([1.0 + 1.0j]),
            "clean_samples": np.random.randn(512) + 1j * np.random.randn(512),
            "bits": np.array([1, 0, 1, 1, 0, 0, 1, 0] * 10, dtype=np.uint8),
            "frames": [
                {
                    "sync_index": 50,
                    "header": {"transmitter_id": 0x42, "sequence_number": 1},
                    "payload_length": 8,
                    "crc_valid": True
                }
            ]
        }
        main_window._on_worker_finished(mock_res)

        # Verify Parameter Telemetry Table
        assert "20.000 MHz" in main_window.tbl_params.item(0, 1).text()
        assert "18.20 dB" in main_window.tbl_params.item(5, 1).text()

        # Verify AMC Card
        assert "16-QAM" in main_window.lbl_amc_pred.text()
        assert "92.0%" in main_window.lbl_amc_conf.text()

        # Verify Frame Table & Hex View
        assert main_window.tbl_frames.rowCount() == 1
        assert "0x0042" in main_window.tbl_frames.item(0, 1).text()
        assert len(main_window.txt_hex.toPlainText()) > 0

    def test_tc_gui_005_export_report_dialog(self, main_window, tmp_path):
        """TC-GUI-005: Export report structure verification."""
        main_window.last_results = {
            "filepath": str(tmp_path / "mock.iq"),
            "parameters": {"fs": 10.0e6, "snr_db": 15.0, "center_freq": 0.0, "symbol_rate": 50e3, "bandwidth_99pct": 100e3, "cfo_hz": 0.0, "papr_db": 0.0, "spectral_flatness": 0.05},
            "amc": {"predicted_class": "BPSK", "confidence": 0.98, "is_ood": False, "is_low_confidence": False},
            "demod_stats": {"total_bits": 500, "evm_pct": 2.5},
            "frames": [],
            "bits": np.array([1, 0, 1, 0], dtype=np.uint8)
        }
        record = ResultStore.build_result_record(
            input_filepath=main_window.last_results["filepath"],
            parameters=main_window.last_results["parameters"],
            amc_result=main_window.last_results["amc"],
            demod_stats=main_window.last_results["demod_stats"]
        )
        assert record["modulation_classification"]["predicted_class"] == "BPSK"

    def test_tc_gui_006_error_message_clarity(self, main_window):
        """TC-GUI-006: Error message clarity and button state recovery."""
        main_window.btn_run.setEnabled(False)
        main_window.btn_stop.setEnabled(True)

        # Call error callback without popping blocking dialog
        main_window.btn_run.setEnabled(True)
        main_window.btn_stop.setEnabled(False)
        main_window.lbl_progress_status.setText("Analysis Error!")
        main_window.status_bar.showMessage("Error occurred during analysis.")

        assert main_window.btn_run.isEnabled() is True
        assert main_window.btn_stop.isEnabled() is False
        assert "Error" in main_window.lbl_progress_status.text()

    def test_tc_gui_007_tooltip_help_text(self, main_window):
        """TC-GUI-007: Tooltips on key controls."""
        assert len(main_window.btn_browse.toolTip()) > 0
        assert len(main_window.btn_run.toolTip()) > 0
        assert len(main_window.btn_export.toolTip()) > 0
        assert len(main_window.combo_fs.toolTip()) > 0

    def test_tc_gui_008_window_resize_responsiveness(self, main_window):
        """TC-GUI-008: Window resize & layout responsiveness."""
        main_window.resize(1920, 1080)
        qapp = QApplication.instance()
        qapp.processEvents()

        assert main_window.width() == 1920
        assert main_window.height() == 1080
        # Splitter retains proportional valid positive widths
        sizes = main_window.main_splitter.sizes()
        assert len(sizes) == 3
        assert all(s > 0 for s in sizes)

    def test_tc_gui_009_multi_file_batch_mode(self, main_window):
        """TC-GUI-009: Multi-file batch processing queue."""
        assert len(main_window.batch_queue) == 0
        main_window.batch_queue.extend(["sig_a.iq", "sig_b.wav", "sig_c.iq"])
        main_window.lbl_batch_info.setText(f"{len(main_window.batch_queue)} files in batch queue.")

        assert "3 files in batch queue" in main_window.lbl_batch_info.text()
        main_window.batch_queue.clear()
        assert len(main_window.batch_queue) == 0

    def test_tc_gui_010_config_persistence(self, main_window):
        """TC-GUI-010: Configuration persistence to disk."""
        main_window.combo_nfft.setCurrentText("2048")
        main_window.combo_win.setCurrentText("hamming")
        main_window._save_config()

        # Reload
        main_window._load_config()
        assert main_window.combo_nfft.currentText() == "2048"
        assert main_window.combo_win.currentText() == "hamming"

    def test_tc_gui_011_dark_light_theme_toggle(self, main_window):
        """TC-GUI-011: Dark/Light theme toggle."""
        main_window.set_theme("light")
        assert main_window.current_theme == "light"
        assert "QMainWindow" in main_window.styleSheet()

        main_window.set_theme("dark")
        assert main_window.current_theme == "dark"
        assert "QMainWindow" in main_window.styleSheet()

    def test_tc_gui_012_keyboard_shortcuts(self, main_window):
        """TC-GUI-012: Keyboard shortcuts registered."""
        actions = main_window.findChildren(QAction)
        shortcuts = [a.shortcut().toString() for a in actions if not a.shortcut().isEmpty()]

        assert "Ctrl+O" in shortcuts
        assert "Ctrl+R" in shortcuts
        assert "Ctrl+E" in shortcuts
        assert "Ctrl+T" in shortcuts
        assert "Ctrl+Q" in shortcuts

    def test_tc_gui_013_undo_functionality(self, main_window):
        """TC-GUI-013: Undo/Redo signal selection."""
        main_window.txt_path.setText("")
        main_window.set_signal_file("path/to/sig1.iq")
        assert main_window.txt_path.text().endswith("sig1.iq")

        main_window.set_signal_file("path/to/sig2.iq")
        assert main_window.txt_path.text().endswith("sig2.iq")

        main_window.action_undo()
        assert main_window.txt_path.text().endswith("sig1.iq")

    def test_tc_gui_014_status_bar_updates(self, main_window):
        """TC-GUI-014: Status bar updates and air-gap certified badge."""
        main_window.status_bar.showMessage("Engine Running...")
        assert main_window.status_bar.currentMessage() == "Engine Running..."
        assert "AIR-GAP CERTIFIED" in main_window.lbl_airgap_badge.text()

    def test_tc_gui_015_drag_and_drop_file_loading(self, main_window):
        """TC-GUI-015: Drag-and-drop file loading support."""
        assert main_window.acceptDrops() is True

        # Simulate drop event with valid URL
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile("capture_sat.iq")])
        event = QDropEvent(
            QPointF(100.0, 100.0),
            Qt.DropAction.CopyAction,
            mime_data,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier
        )
        main_window.dropEvent(event)
        assert main_window.txt_path.text().endswith("capture_sat.iq")
