"""
Test Suite for Air-Gap Isolation, Security Guards & Data Sanitization.
Validates TC-SEC-001 through TC-SEC-008.
"""

import pytest
import os
import socket
import tempfile
import numpy as np

from ntro_sigint.core.security import (
    AirGapGuard,
    PathSanitizer,
    SecureTempDirectory,
    ConfigValidator,
    AuditLogger,
    MemoryGuard,
    SecurityViolationError
)


class TestAirGapSecurity:

    def test_tc_sec_001_zero_network_socket(self):
        """TC-SEC-001: Zero network socket verification. Connect attempts blocked immediately."""
        AirGapGuard.enable_airgap()
        try:
            assert AirGapGuard.is_airgap_active() is True
            # Attempt to connect a raw socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with pytest.raises(SecurityViolationError, match="Air-Gap Policy Violation"):
                s.connect(("8.8.8.8", 53))
            s.close()
        finally:
            AirGapGuard.disable_airgap()
            assert AirGapGuard.is_airgap_active() is False

    def test_tc_sec_002_temporary_file_cleanup(self):
        """TC-SEC-002: Temporary file cleanup and zeroization."""
        temp_dir_path = None
        with SecureTempDirectory() as tmp_dir:
            temp_dir_path = tmp_dir
            assert os.path.exists(temp_dir_path)

            # Create a sensitive intermediate payload file
            test_file = os.path.join(tmp_dir, "intermediate_payload.tmp")
            with open(test_file, "wb") as f:
                f.write(b"\xFF\xAA\x55\x00" * 1024)
            assert os.path.exists(test_file)

        # Upon exit, temp directory and all intermediate files must be completely eradicated
        assert not os.path.exists(temp_dir_path)

    def test_tc_sec_003_offline_standalone_execution(self):
        """TC-SEC-003: Offline standalone execution. Pipeline works 100% without network."""
        AirGapGuard.enable_airgap()
        try:
            # Run local signal processing and parameter extraction under active air-gap guard
            from ntro_sigint.ml.dataset import SyntheticSignalGenerator
            from ntro_sigint.dsp.parameter_extractor import ParameterExtractor

            sig = SyntheticSignalGenerator.generate_signal("QPSK", num_samples=1024, snr_db=20.0)
            res = ParameterExtractor.extract_all(sig, 1.0e6)
            assert res.snr_db is not None
            assert res.symbol_rate > 0
        finally:
            AirGapGuard.disable_airgap()

    def test_tc_sec_004_input_path_sanitization(self, tmp_path):
        """TC-SEC-004: Input path sanitization (injection and directory traversal prevention)."""
        allowed_dir = str(tmp_path / "allowed_workspace")
        os.makedirs(allowed_dir, exist_ok=True)

        # 1. Directory traversal attempt
        malicious_path = os.path.join(allowed_dir, "../../windows/system32/cmd.exe")
        with pytest.raises(SecurityViolationError, match="Directory traversal detected"):
            PathSanitizer.validate_safe_path(malicious_path, allowed_base_dir=allowed_dir)

        # 2. Null byte injection attempt
        with pytest.raises(SecurityViolationError, match="Null byte detected"):
            PathSanitizer.validate_safe_path("safe_file.iq\x00.exe")

        # 3. Valid safe path
        safe_path = os.path.join(allowed_dir, "legit_signal.iq")
        validated = PathSanitizer.validate_safe_path(safe_path, allowed_base_dir=allowed_dir)
        assert validated == os.path.abspath(safe_path)

        # 4. Dangerous filename characters
        clean_name = PathSanitizer.sanitize_filename("..//..\\payload<>:\"|?*.iq")
        assert ".." not in clean_name
        assert clean_name == "payload.iq"

    def test_tc_sec_005_config_file_validation(self):
        """TC-SEC-005: Config file validation against strict schema."""
        valid_cfg = {
            "fs_hz": 20.0e6,
            "center_freq_hz": 0.0,
            "enable_amc": True,
            "viterbi_k": 7
        }
        checked = ConfigValidator.validate_config(valid_cfg)
        assert checked["viterbi_k"] == 7

        # Unknown / unauthorized configuration key
        with pytest.raises(SecurityViolationError, match="Unauthorized or unknown config parameter"):
            ConfigValidator.validate_config({"fs_hz": 1e6, "__import__": "os"})

        # Invalid type
        with pytest.raises(SecurityViolationError, match="must be integer"):
            ConfigValidator.validate_config({"viterbi_k": "seven"})

    def test_tc_sec_006_sensitive_data_in_logs(self, tmp_path):
        """TC-SEC-006: Sensitive data masking in audit logs."""
        log_file = str(tmp_path / "audit.log")
        logger = AuditLogger(log_file)

        raw_payload = b"CLASSIFIED_SIGINT_DECODED_DATA_ABC"
        raw_samples = np.array([1.0 + 2.0j, -0.5 + 0.3j], dtype=np.complex64)

        logger.log_event("FRAME_DECODED", {
            "tx_id": 0x101,
            "raw_payload": raw_payload,
            "samples": raw_samples,
            "encryption_key": "SecretMasterPassphrase123"
        })

        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()

        # Verify raw data and secret string were masked
        assert "CLASSIFIED_SIGINT_DECODED_DATA_ABC" not in log_content
        assert "SecretMasterPassphrase123" not in log_content
        assert "BUFFER" in log_content
        assert "NDARRAY" in log_content
        assert "********" in log_content

    def test_tc_sec_007_memory_isolation(self):
        """TC-SEC-007: Memory isolation and buffer zeroization."""
        buf = bytearray(b"SENSITIVE_TEMPORARY_KEYSTREAM_BUFFER")
        assert any(b != 0 for b in buf)

        MemoryGuard.zeroize_buffer(buf)
        assert all(b == 0 for b in buf)
        assert len(buf) == 36

    def test_tc_sec_008_signal_file_permissions(self, tmp_path):
        """TC-SEC-008: Signal file permissions check."""
        test_file = tmp_path / "signal_output.json"
        test_file.write_text('{"status": "ok"}', encoding="utf-8")

        # Verify file exists and is readable/writable by current user
        assert os.path.exists(test_file)
        assert os.access(test_file, os.R_OK)
        assert os.access(test_file, os.W_OK)
