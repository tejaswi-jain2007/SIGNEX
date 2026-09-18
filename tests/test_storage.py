"""
Test Suite for Result Storage, PDF Report Generation, and Encryption at Rest.
Validates TC-STORE-001 through TC-STORE-010.
"""

import pytest
import os
import tempfile
import json
import numpy as np

from ntro_sigint.core.exporter import ResultStore, PDFReportGenerator, CryptoStore, SCHEMA_VERSION


class TestStorageAndReporting:

    @pytest.fixture
    def mock_results(self, tmp_path):
        dummy_file = tmp_path / "mock_signal.iq"
        dummy_file.write_bytes(b"\x00\x01\x02\x03" * 1024)

        params = {
            "fs": 20.0e6,
            "center_freq": 100.0e3,
            "symbol_rate": 50.0e3,
            "bandwidth_99pct": 120.0e3,
            "snr_db": 18.5,
            "papr_db": 0.2,
            "cfo_hz": 12.5,
            "spectral_flatness": 0.04
        }
        amc = {
            "predicted_class": "QPSK",
            "confidence": 0.965,
            "is_ood": False,
            "is_low_confidence": False,
            "probabilities": {"QPSK": 0.965, "BPSK": 0.02, "8-PSK": 0.015}
        }
        frames = [
            {
                "sync_index": 128,
                "header": {"transmitter_id": 0x101, "sequence_number": 1, "payload_length": 16},
                "payload_length_bytes": 16,
                "crc_valid": True,
                "fec_status": "CLEAN"
            }
        ]
        return str(dummy_file), params, amc, frames

    def test_tc_store_001_result_persistence_json(self, mock_results, tmp_path):
        """TC-STORE-001: Result persistence (JSON export)."""
        iq_path, params, amc, frames = mock_results
        rec = ResultStore.build_result_record(iq_path, params, amc, extracted_frames=frames)

        out_json = str(tmp_path / "analysis_result.json")
        saved = ResultStore.save_json(rec, out_json)

        assert os.path.exists(saved)
        loaded = ResultStore.load_json(saved)
        assert loaded["parameters"]["symbol_rate"] == 50.0e3
        assert loaded["modulation_classification"]["predicted_class"] == "QPSK"
        assert len(loaded["extracted_frames"]) == 1

    def test_tc_store_002_result_traceability(self, mock_results, tmp_path):
        """TC-STORE-002: Result traceability (input metadata and SHA-256 hash)."""
        iq_path, params, amc, frames = mock_results
        rec = ResultStore.build_result_record(iq_path, params, amc, extracted_frames=frames)

        out_json = str(tmp_path / "traceable_result.json")
        ResultStore.save_json(rec, out_json)

        loaded = ResultStore.load_json(out_json)
        assert "metadata" in loaded
        assert len(loaded["metadata"]["input_sha256"]) == 64 # SHA-256 hex string
        assert loaded["metadata"]["model_version"] == "amc_resnet18_v1.0"
        assert loaded["metadata"]["input_filename"] == "mock_signal.iq"

    def test_tc_store_003_report_generation_pdf(self, mock_results, tmp_path):
        """TC-STORE-003: Report generation (PDF dossier with plots and parameters)."""
        iq_path, params, amc, frames = mock_results
        rec = ResultStore.build_result_record(iq_path, params, amc, extracted_frames=frames)

        # Generate synthetic QPSK constellation for plot
        constellation = np.random.choice([1+1j, 1-1j, -1+1j, -1-1j], 1000) + 0.1 * (np.random.randn(1000) + 1j * np.random.randn(1000))

        pdf_path = str(tmp_path / "NTRO_Analysis_Report.pdf")
        gen_path = PDFReportGenerator.generate_dossier(rec, pdf_path, constellation_samples=constellation)

        assert os.path.exists(gen_path)
        assert os.path.getsize(gen_path) > 1000 # Valid non-empty PDF file

        # Check PDF header magic bytes
        with open(gen_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"

    def test_tc_store_004_batch_export_mapping(self, tmp_path):
        """TC-STORE-004: Batch export with input-to-output mapping manifest."""
        batch_items = [
            {"input": "sig1.iq", "output_json": "sig1_res.json", "output_pdf": "sig1_rep.pdf", "status": "COMPLETED"},
            {"input": "sig2.wav", "output_json": "sig2_res.json", "output_pdf": "sig2_rep.pdf", "status": "COMPLETED"}
        ]
        manifest_path = str(tmp_path / "batch_manifest.json")
        saved_man = ResultStore.export_batch_manifest(batch_items, manifest_path)

        assert os.path.exists(saved_man)
        with open(saved_man, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["total_items"] == 2
            assert data["items"][0]["input"] == "sig1.iq"

    def test_tc_store_005_result_versioning(self, mock_results):
        """TC-STORE-005: Result versioning with strict schema tags."""
        iq_path, params, amc, frames = mock_results
        rec = ResultStore.build_result_record(iq_path, params, amc)

        assert rec["schema_version"] == SCHEMA_VERSION
        assert rec["metadata"]["model_version"] == "amc_resnet18_v1.0"

    def test_tc_store_006_checkpoint_saving(self, tmp_path):
        """TC-STORE-006: Incremental pipeline checkpoint saving."""
        cp_path = str(tmp_path / "pipeline_checkpoint.json")

        # Stage 1: Ingestion
        ResultStore.save_checkpoint("ingestion", {"samples_loaded": 50000, "fs": 20e6}, cp_path)
        cp1 = ResultStore.load_checkpoint(cp_path)
        assert "ingestion" in cp1
        assert cp1["ingestion"]["samples_loaded"] == 50000

        # Stage 2: Parameters (without losing stage 1)
        ResultStore.save_checkpoint("parameters", {"snr_db": 15.2, "symbol_rate": 25e3}, cp_path)
        cp2 = ResultStore.load_checkpoint(cp_path)
        assert "ingestion" in cp2
        assert "parameters" in cp2
        assert cp2["parameters"]["snr_db"] == 15.2

    def test_tc_store_007_result_archive_compression(self, tmp_path):
        """TC-STORE-007: Compressed ZIP archive containing all analysis products."""
        f1 = tmp_path / "result.json"
        f1.write_text('{"status": "ok"}', encoding="utf-8")
        f2 = tmp_path / "payload.bin"
        f2.write_bytes(b"\xAA\xBB\xCC\xDD" * 100)

        arch_path = str(tmp_path / "dossier_archive.zip")
        ResultStore.create_result_archive([str(f1), str(f2)], arch_path)

        assert os.path.exists(arch_path)
        import zipfile
        with zipfile.ZipFile(arch_path, "r") as z:
            names = z.namelist()
            assert "result.json" in names
            assert "payload.bin" in names
            assert z.read("result.json") == b'{"status": "ok"}'

    def test_tc_store_008_encryption_at_rest(self):
        """TC-STORE-008: Authenticated encryption at rest using PBKDF2-HMAC keystream."""
        secret_data = b"TOP_SECRET_AIRGAP_PAYLOAD_TELEMETRY_RECORD_12345"
        password = "NTRO_Master_Passphrase_2026!"

        encrypted = CryptoStore.encrypt_data(secret_data, password)
        # Ciphertext must differ completely from plaintext and contain NSIG header
        assert encrypted != secret_data
        assert encrypted.startswith(b"NSIG")

        # Correct password decrypts perfectly
        decrypted = CryptoStore.decrypt_data(encrypted, password)
        assert decrypted == secret_data

        # Wrong password raises ValueError
        with pytest.raises(ValueError, match="Authentication failed"):
            CryptoStore.decrypt_data(encrypted, "WRONG_PASSWORD")

        # Tampered ciphertext raises ValueError
        tampered = bytearray(encrypted)
        tampered[-1] ^= 0xFF
        with pytest.raises(ValueError):
            CryptoStore.decrypt_data(bytes(tampered), password)

    def test_tc_store_009_metadata_embedding(self, mock_results):
        """TC-STORE-009: Embedded metadata (timestamp, user/operator, model version)."""
        iq_path, params, amc, frames = mock_results
        rec = ResultStore.build_result_record(
            iq_path, params, amc,
            operator_id="ANALYST_AGENT_007",
            model_version="amc_resnet18_v1.0"
        )
        assert rec["metadata"]["operator_id"] == "ANALYST_AGENT_007"
        assert rec["metadata"]["model_version"] == "amc_resnet18_v1.0"
        assert "timestamp_utc" in rec["metadata"]

    def test_tc_store_010_long_term_reproducibility(self, tmp_path):
        """TC-STORE-010: Long-term result backward compatibility & schema migration."""
        legacy_v1 = {
            "schema_version": "1.0",
            "filename": "legacy_rec.iq",
            "model": "legacy_v1.0",
            "parameters": {"fs": 10.0e6}
        }
        legacy_path = str(tmp_path / "legacy.json")
        with open(legacy_path, "w", encoding="utf-8") as f:
            json.dump(legacy_v1, f)

        migrated = ResultStore.load_json(legacy_path)
        assert migrated["schema_version"] == SCHEMA_VERSION
        assert migrated["metadata"]["input_filename"] == "legacy_rec.iq"
        assert migrated["parameters"]["fs"] == 10.0e6
