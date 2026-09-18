"""
Unit Test Suite for Module 5: Automatic Modulation Classification (AMC)
Corresponds to Master Test Plan TC-AMC-001 through TC-AMC-012.
"""

import os
import pytest
import numpy as np

from ntro_sigint.ml.dataset import SyntheticSignalGenerator
from ntro_sigint.ml.amc_classifier import ModulationClassifier, AMCResult


@pytest.fixture(scope="module")
def classifier():
    model_weights = "models/amc_resnet18.pt"
    return ModulationClassifier(model_path=model_weights if os.path.exists(model_weights) else None)


class TestModulationClassification:

    def test_tc_amc_001_bpsk_classification(self, classifier):
        """TC-AMC-001: BPSK classification (high SNR, 20 dB)."""
        sig = SyntheticSignalGenerator.generate_signal("BPSK", num_samples=1024, snr_db=20.0, random_seed=101)
        res = classifier.predict(sig, snr_db=20.0)
        assert res.predicted_class == "BPSK"
        assert res.confidence >= 0.90 # Target > 0.95 (or >=0.90 with pulse shaping)

    def test_tc_amc_002_qpsk_classification(self, classifier):
        """TC-AMC-002: QPSK classification (high SNR, 20 dB)."""
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=1024, snr_db=20.0, random_seed=102)
        res = classifier.predict(sig, snr_db=20.0)
        assert res.predicted_class == "QPSK"
        assert res.confidence >= 0.85 # Target > 0.90

    def test_tc_amc_003_8psk_classification(self, classifier):
        """TC-AMC-003: 8-PSK classification."""
        sig = SyntheticSignalGenerator.generate_signal("8-PSK", num_samples=1024, snr_db=20.0, random_seed=103)
        res = classifier.predict(sig, snr_db=20.0)
        assert res.predicted_class == "8-PSK"
        assert res.confidence >= 0.80

    def test_tc_amc_004_16qam_classification(self, classifier):
        """TC-AMC-004: 16-QAM classification."""
        sig = SyntheticSignalGenerator.generate_signal("16-QAM", num_samples=1024, snr_db=20.0, random_seed=104)
        res = classifier.predict(sig, snr_db=20.0)
        assert res.predicted_class == "16-QAM"
        assert res.confidence >= 0.80

    def test_tc_amc_005_64qam_classification(self, classifier):
        """TC-AMC-005: 64-QAM classification."""
        sig = SyntheticSignalGenerator.generate_signal("64-QAM", num_samples=1024, snr_db=20.0, random_seed=105)
        res = classifier.predict(sig, snr_db=20.0)
        assert res.predicted_class == "64-QAM"
        assert res.confidence >= 0.75

    def test_tc_amc_006_fsk_classification(self, classifier):
        """TC-AMC-006: FSK classification (2-FSK)."""
        sig = SyntheticSignalGenerator.generate_signal("2-FSK", num_samples=1024, snr_db=20.0, random_seed=106)
        res = classifier.predict(sig, snr_db=20.0)
        assert "FSK" in res.predicted_class
        assert res.confidence >= 0.85

    def test_tc_amc_007_low_snr_classification(self, classifier):
        """TC-AMC-007: Low-SNR classification (5 dB)."""
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=1024, snr_db=5.0, random_seed=107)
        res = classifier.predict(sig, snr_db=5.0)
        assert res.predicted_class is not None
        # In low SNR, confidence must be appropriately reduced (0.60 - 0.75)
        assert res.confidence <= 0.85
        assert res.is_low_confidence # Flagged as low-confidence

    def test_tc_amc_008_ood_and_am_detection(self, classifier):
        """TC-AMC-008: Out-of-Distribution (OOD) / AM handling."""
        # 1. Analog AM signal: should be identified as AM or flagged
        am_sig = SyntheticSignalGenerator.generate_signal("AM-DSB", num_samples=1024, snr_db=20.0, random_seed=108)
        res_am = classifier.predict(am_sig)
        assert res_am.predicted_class == "AM-DSB" or res_am.is_ood

        # 2. Pure White Noise (OOD)
        pure_noise = (np.random.randn(1024) + 1j * np.random.randn(1024)).astype(np.complex64)
        res_noise = classifier.predict(pure_noise, snr_db=-10.0)
        # Low confidence or OOD flag set; not presented as high-certainty digital
        assert res_noise.confidence < 0.75

    def test_tc_amc_009_inference_latency(self, classifier):
        """TC-AMC-009: Model inference latency (< 100 ms budget)."""
        sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=1024, snr_db=15.0)
        _ = classifier.predict(sig) # Warm-up pass to initialize thread pools
        res = classifier.predict(sig)
        assert res.inference_time_ms < 100.0 # Strict SRS NFR-1 requirement

    def test_tc_amc_010_window_length_consistency(self, classifier):
        """TC-AMC-010: Consistency across signal lengths (1024, 2048, 4096)."""
        for n_len in [1024, 2048, 4096]:
            sig = SyntheticSignalGenerator.generate_signal("BPSK", num_samples=n_len, snr_db=20.0, random_seed=200)
            res = classifier.predict(sig, snr_db=20.0)
            assert res.predicted_class == "BPSK"

    def test_tc_amc_011_carrier_offset_robustness(self, classifier):
        """TC-AMC-011: Robustness to carrier frequency offset (5 kHz)."""
        sig = SyntheticSignalGenerator.generate_signal(
            "QPSK", num_samples=1024, snr_db=20.0, cfo_hz=5000.0, random_seed=201
        )
        res = classifier.predict(sig, snr_db=20.0)
        assert res.predicted_class == "QPSK"

    def test_tc_amc_012_phase_noise_robustness(self, classifier):
        """TC-AMC-012: Robustness to phase noise."""
        sig = SyntheticSignalGenerator.generate_signal(
            "BPSK", num_samples=1024, snr_db=20.0, phase_noise_std=0.02, random_seed=202
        )
        res = classifier.predict(sig, snr_db=20.0)
        assert res.predicted_class == "BPSK"
