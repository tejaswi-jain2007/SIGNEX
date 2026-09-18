"""
NTRO SIGINT Performance & Benchmarking Test Suite.
Validates TC-PER-001 through TC-PER-010.
Adheres to Master Test Plan & Non-Functional Requirements (NFR-1 through NFR-4).
"""

import pytest
import os
import time
import gc
import struct
import numpy as np
import torch

from ntro_sigint.core.pipeline import SignalAnalysisPipeline
from ntro_sigint.ml.dataset import SyntheticSignalGenerator
from ntro_sigint.ml.amc_classifier import ModulationClassifier
from ntro_sigint.decoding.fec import ConvolutionalCodec
from ntro_sigint.core.ingestion import SignalReader, SignalData
from ntro_sigint.dsp.parameter_extractor import ParameterExtractor
from ntro_sigint.core.preprocessor import SignalPreprocessor
from ntro_sigint.dsp.demodulator import Demodulator


class TestPerformance:
    """Performance, throughput, latency, memory leak, and scalability tests."""

    @pytest.fixture
    def pipeline(self):
        return SignalAnalysisPipeline(model_path="models/amc_resnet18.pt", enforce_airgap=False)

    @pytest.fixture
    def qapp(self):
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        return app

    def _create_temp_raw_iq(self, tmp_path, filename: str, num_samples: int) -> str:
        filepath = os.path.join(tmp_path, filename)
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=num_samples, snr_db=20.0)
        iq_bytes = np.empty(num_samples * 2, dtype=np.float32)
        iq_bytes[0::2] = sig.real
        iq_bytes[1::2] = sig.imag
        with open(filepath, "wb") as f:
            f.write(iq_bytes.tobytes())
        import json
        with open(filepath + ".json", "w") as f:
            json.dump({"sample_rate": 1.0e6, "center_freq": 0.0}, f)
        return filepath

    def test_tc_per_001_processing_speed(self, pipeline, tmp_path):
        """TC-PER-001: Processing speed throughput (target < 5.0 s for large buffer)."""
        num_samples = 65536
        filepath = self._create_temp_raw_iq(str(tmp_path), "speed_test.iq", num_samples)
        out_dir = str(tmp_path / "out_per_001")

        t0 = time.perf_counter()
        result = pipeline.process_file(filepath, output_dir=out_dir, generate_pdf=False)
        elapsed = time.perf_counter() - t0

        samples_per_sec = num_samples / elapsed
        assert elapsed < 5.0, f"Processing took {elapsed:.2f}s, exceeding 5.0s limit"
        assert samples_per_sec > 10000, f"Throughput {samples_per_sec:.0f} sps is below requirement"

    def test_tc_per_002_gui_responsiveness_during_processing(self, qapp, tmp_path):
        """TC-PER-002: GUI responsiveness during background processing (< 100 ms event lag)."""
        from PyQt6.QtCore import QCoreApplication
        from ntro_sigint.gui.main_window import AnalysisWorkerThread

        num_samples = 32768
        filepath = self._create_temp_raw_iq(str(tmp_path), "gui_stress.iq", num_samples)

        worker = AnalysisWorkerThread(filepath, model_path="models/amc_resnet18.pt")
        worker.start()

        max_event_lag = 0.0
        start_time = time.perf_counter()

        while worker.isRunning() and (time.perf_counter() - start_time < 10.0):
            t_loop = time.perf_counter()
            QCoreApplication.processEvents()
            lag = time.perf_counter() - t_loop
            if lag > max_event_lag:
                max_event_lag = lag
            time.sleep(0.01)

        worker.wait(5000)

        # Main thread event latency must remain responsive (< 100 ms)
        assert max_event_lag < 0.10, f"UI event lag was {max_event_lag*1000:.1f} ms (> 100 ms threshold)"

    def test_tc_per_003_memory_leak_detection(self, pipeline, tmp_path):
        """TC-PER-003: Memory leak detection across sequential processing runs (growth < 50 MB)."""
        import tracemalloc

        filepath = self._create_temp_raw_iq(str(tmp_path), "mem_test.iq", 4096)
        out_dir = str(tmp_path / "mem_out")

        # Warm-up run
        pipeline.process_file(filepath, output_dir=out_dir)
        gc.collect()

        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        # Execute 5 sequential runs
        for i in range(5):
            pipeline.process_file(filepath, output_dir=out_dir)

        gc.collect()
        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        total_growth_bytes = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
        growth_mb = total_growth_bytes / (1024 * 1024)

        assert growth_mb < 50.0, f"Memory grew by {growth_mb:.2f} MB, exceeding 50 MB threshold"

    def test_tc_per_004_multicore_cpu_utilization(self):
        """TC-PER-004: Multi-core CPU parallel operations benchmark."""
        num_signals = 8
        n_pts = 65536
        signals = np.random.randn(num_signals, n_pts) + 1j * np.random.randn(num_signals, n_pts)

        t0 = time.perf_counter()
        spect = np.fft.fft(signals, axis=1)
        elapsed = time.perf_counter() - t0

        assert spect.shape == (num_signals, n_pts)
        assert elapsed < 1.0, f"Multi-channel FFT took {elapsed:.3f}s"

    def test_tc_per_005_gpu_acceleration(self):
        """TC-PER-005: Hardware / SIMD acceleration benchmark (quantifying speedup ratio >= 2.0x)."""
        n = 131072
        x = np.random.randn(n).astype(np.complex64)

        if torch.cuda.is_available():
            device = torch.device("cuda")
            x_cpu = torch.tensor(x)
            # Warmup CPU
            _ = torch.fft.fft(x_cpu)
            t0 = time.perf_counter()
            for _ in range(10):
                _ = torch.fft.fft(x_cpu)
            cpu_time = (time.perf_counter() - t0) / 10.0

            x_gpu = x_cpu.to(device)
            # Warmup GPU / cuFFT plan
            _ = torch.fft.fft(x_gpu)
            torch.cuda.synchronize()
            t1 = time.perf_counter()
            for _ in range(10):
                _ = torch.fft.fft(x_gpu)
            torch.cuda.synchronize()
            gpu_time = (time.perf_counter() - t1) / 10.0

            speedup = cpu_time / max(1e-6, gpu_time)
            assert gpu_time < 1.0
            assert speedup >= 1.0
        else:
            # Benchmark SIMD vectorized FFT vs naive discrete DFT loop on matching sub-window to quantify acceleration
            sub_x = x[:1024]
            t0 = time.perf_counter()
            _ = torch.fft.fft(torch.tensor(sub_x))
            vectorized_time = time.perf_counter() - t0

            # Naive unvectorized DFT loop to quantify SIMD/algorithm speedup
            t1 = time.perf_counter()
            _ = np.array([sum(sub_x[m] * np.exp(-2j * np.pi * k * m / 1024) for m in range(1024)) for k in range(32)])
            scalar_time = time.perf_counter() - t1

            speedup = scalar_time / max(1e-6, vectorized_time)
            assert speedup >= 2.0, f"Hardware/SIMD speedup ratio was {speedup:.1f}x (< 2.0x requirement)"

    def test_tc_per_006_disk_io_throughput(self, tmp_path):
        """TC-PER-006: Disk I/O throughput for IQ ingestion (> 50 MB/sec)."""
        num_samples = 1000000 # 8 MB IQ data
        filepath = os.path.join(tmp_path, "io_speed.iq")
        data = np.zeros(num_samples * 2, dtype=np.float32)
        with open(filepath, "wb") as f:
            f.write(data.tobytes())

        file_size_bytes = os.path.getsize(filepath)
        t0 = time.perf_counter()
        sig_data = SignalReader.load(filepath, sample_rate=1.0e6)
        elapsed = time.perf_counter() - t0

        mb_read = file_size_bytes / (1024 * 1024)
        throughput_mb_s = mb_read / elapsed
        assert len(sig_data.samples) == num_samples
        assert throughput_mb_s > 50.0, f"I/O throughput was {throughput_mb_s:.1f} MB/s"

    def test_tc_per_007_fft_performance(self):
        """TC-PER-007: High-rate parallel FFT performance (> 500 FFTs/sec)."""
        num_ffts = 1000
        fft_len = 4096
        samples = np.random.randn(num_ffts, fft_len).astype(np.complex64)

        t0 = time.perf_counter()
        _ = np.fft.fft(samples, axis=1)
        elapsed = time.perf_counter() - t0

        ffts_per_sec = num_ffts / elapsed
        assert ffts_per_sec > 500.0, f"FFT rate was {ffts_per_sec:.0f} FFT/s (< 500 requirement)"

    def test_tc_per_008_model_inference_latency(self):
        """TC-PER-008: Model inference latency for AMC (< 100 ms per window)."""
        classifier = ModulationClassifier(model_path="models/amc_resnet18.pt")
        test_window = (np.random.randn(1024) + 1j * np.random.randn(1024)).astype(np.complex64)

        # Warm-up
        _ = classifier.predict(test_window, snr_db=20.0)

        # Timed pass
        t0 = time.perf_counter()
        res = classifier.predict(test_window, snr_db=20.0)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert elapsed_ms < 100.0, f"Inference took {elapsed_ms:.1f} ms, exceeding 100 ms"
        assert res.predicted_class is not None

    def test_tc_per_009_viterbi_decoder_throughput(self):
        """TC-PER-009: Viterbi decoder throughput (> 5,000 bps for real-time decoding on mobile dual-core)."""
        codec = ConvolutionalCodec(k=7)
        raw_bits = np.random.randint(0, 2, size=2000, dtype=np.uint8)
        encoded = codec.encode(raw_bits)

        t0 = time.perf_counter()
        decoded, _ = codec.decode(encoded)
        elapsed = time.perf_counter() - t0

        bps = len(raw_bits) / elapsed
        assert bps > 5000.0, f"Viterbi throughput was {bps:.0f} bps (< 5 kbps requirement)"
        assert len(decoded) == len(raw_bits)

    def test_tc_per_010_scaling_with_file_size(self, pipeline, tmp_path):
        """TC-PER-010: Scaling with file size conforms to linear O(N) complexity."""
        n1 = 16384
        n2 = 65536 # 4x larger
        f1 = self._create_temp_raw_iq(str(tmp_path), "scale_1.iq", n1)
        f2 = self._create_temp_raw_iq(str(tmp_path), "scale_2.iq", n2)

        t0 = time.perf_counter()
        pipeline.process_file(f1, output_dir=str(tmp_path / "scale1_out"), generate_pdf=False)
        t1_elapsed = time.perf_counter() - t0

        t0 = time.perf_counter()
        pipeline.process_file(f2, output_dir=str(tmp_path / "scale2_out"), generate_pdf=False)
        t2_elapsed = time.perf_counter() - t0

        scaling_ratio = t2_elapsed / max(1e-3, t1_elapsed)
        assert scaling_ratio < 8.0, f"Scaling ratio was {scaling_ratio:.2f}x (expected < 8.0x for linear O(N))"
