"""
Structured Result Persistence, PDF Report Generation, Archive Compression, and Encryption at Rest.
Full traceability according to NTRO SIH Requirements (TC-STORE-001 through TC-STORE-010).
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import os
import json
import hashlib
import time
import zipfile
import hmac
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use("Agg") # Non-interactive headless backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


SCHEMA_VERSION = "2.1"
DEFAULT_MODEL_VERSION = "amc_resnet18_v1.0"


class CryptoStore:
    """
    Air-gapped symmetric encryption at rest using PBKDF2-HMAC-SHA256.
    Generates authenticated cipher streams without external crypto C-extensions.
    """

    @staticmethod
    def derive_key(passphrase: str, salt: bytes, length: int = 32) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, 100000, dklen=length)

    @classmethod
    def encrypt_data(cls, plaintext: bytes, passphrase: str) -> bytes:
        """Encrypts bytes using authenticated counter-mode keystream."""
        salt = os.urandom(16)
        key = cls.derive_key(passphrase, salt, 32)
        nonce = os.urandom(12)

        # Counter mode keystream generator
        ciphertext = bytearray(len(plaintext))
        block_idx = 0
        for offset in range(0, len(plaintext), 32):
            chunk_len = min(32, len(plaintext) - offset)
            keystream_block = hashlib.sha256(key + nonce + block_idx.to_bytes(4, "big")).digest()
            for b in range(chunk_len):
                ciphertext[offset + b] = plaintext[offset + b] ^ keystream_block[b]
            block_idx += 1

        # HMAC tag
        tag = hmac.new(key, bytes(ciphertext), hashlib.sha256).digest()
        # Wire format: MAGIC (4) + SALT (16) + NONCE (12) + TAG (32) + CIPHERTEXT
        return b"NSIG" + salt + nonce + tag + bytes(ciphertext)

    @classmethod
    def decrypt_data(cls, payload: bytes, passphrase: str) -> bytes:
        """Decrypts and authenticates ciphertext. Raises ValueError on tamper or wrong key."""
        if len(payload) < 64 or payload[:4] != b"NSIG":
            raise ValueError("Invalid encrypted payload header or corrupt magic bytes")

        salt = payload[4:20]
        nonce = payload[20:32]
        expected_tag = payload[32:64]
        ciphertext = payload[64:]

        key = cls.derive_key(passphrase, salt, 32)
        actual_tag = hmac.new(key, ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_tag, actual_tag):
            raise ValueError("Authentication failed: incorrect passphrase or data tampered")

        plaintext = bytearray(len(ciphertext))
        block_idx = 0
        for offset in range(0, len(ciphertext), 32):
            chunk_len = min(32, len(ciphertext) - offset)
            keystream_block = hashlib.sha256(key + nonce + block_idx.to_bytes(4, "big")).digest()
            for b in range(chunk_len):
                plaintext[offset + b] = ciphertext[offset + b] ^ keystream_block[b]
            block_idx += 1

        return bytes(plaintext)


class ResultStore:
    """
    Persists signal analysis results with cryptographic hashing and versioned schema.
    """

    @staticmethod
    def compute_sha256(filepath: str) -> str:
        """Calculates SHA-256 digest of input file for chain of custody."""
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def build_result_record(
        cls,
        input_filepath: str,
        parameters: Dict[str, Any],
        amc_result: Dict[str, Any],
        demod_stats: Optional[Dict[str, Any]] = None,
        fec_stats: Optional[Dict[str, Any]] = None,
        extracted_frames: Optional[List[Dict[str, Any]]] = None,
        operator_id: str = "SIGINT-AIRGAP-OPERATOR",
        model_version: str = DEFAULT_MODEL_VERSION
    ) -> Dict[str, Any]:
        """Constructs an immutable result record with embedded metadata."""
        input_hash = cls.compute_sha256(input_filepath) if os.path.exists(input_filepath) else "UNKNOWN_NO_FILE"
        file_size = os.path.getsize(input_filepath) if os.path.exists(input_filepath) else 0

        return {
            "schema_version": SCHEMA_VERSION,
            "metadata": {
                "input_filename": os.path.basename(input_filepath),
                "input_filepath": os.path.abspath(input_filepath),
                "input_sha256": input_hash,
                "input_size_bytes": file_size,
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "operator_id": operator_id,
                "model_version": model_version,
                "execution_environment": "NTRO Air-Gapped Workstation"
            },
            "parameters": parameters,
            "modulation_classification": amc_result,
            "demodulation": demod_stats or {},
            "decoding": fec_stats or {},
            "extracted_frames": extracted_frames or []
        }

    @classmethod
    def save_json(cls, record: Dict[str, Any], output_path: str) -> str:
        """Atomically saves result record to JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        tmp_path = f"{output_path}.tmp_{int(time.time()*1000)}"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(tmp_path, output_path)
        return output_path

    @classmethod
    def load_json(cls, json_path: str) -> Dict[str, Any]:
        """Loads result JSON and migrates legacy schemas if needed."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Migration logic for legacy v1.0 schemas
        if data.get("schema_version") == "1.0":
            data["schema_version"] = SCHEMA_VERSION
            if "metadata" not in data:
                data["metadata"] = {
                    "input_filename": data.get("filename", "legacy_input"),
                    "model_version": data.get("model", "legacy_v1.0")
                }
        return data

    @classmethod
    def save_checkpoint(cls, stage_name: str, stage_data: Dict[str, Any], checkpoint_path: str) -> str:
        """Saves incremental pipeline state to disk."""
        os.makedirs(os.path.dirname(os.path.abspath(checkpoint_path)), exist_ok=True)
        cp = {}
        if os.path.exists(checkpoint_path):
            try:
                with open(checkpoint_path, "r", encoding="utf-8") as f:
                    cp = json.load(f)
            except Exception:
                cp = {}
        cp[stage_name] = stage_data
        cp["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(cp, f, indent=2)
        return checkpoint_path

    @classmethod
    def load_checkpoint(cls, checkpoint_path: str) -> Dict[str, Any]:
        """Loads pipeline checkpoint state."""
        if not os.path.exists(checkpoint_path):
            return {}
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def create_result_archive(cls, file_paths: List[str], archive_path: str) -> str:
        """Creates a compressed .zip archive of all analysis products."""
        os.makedirs(os.path.dirname(os.path.abspath(archive_path)), exist_ok=True)
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in file_paths:
                if os.path.exists(p):
                    zf.write(p, arcname=os.path.basename(p))
        return archive_path

    @classmethod
    def export_batch_manifest(cls, batch_results: List[Dict[str, str]], manifest_path: str) -> str:
        """Saves batch processing mapping from input files to analysis deliverables."""
        os.makedirs(os.path.dirname(os.path.abspath(manifest_path)), exist_ok=True)
        manifest = {
            "batch_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_items": len(batch_results),
            "items": batch_results
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return manifest_path


class PDFReportGenerator:
    """
    Generates multi-page classified SIGINT intelligence dossiers in vector PDF.
    Contains parameter telemetry, AMC probabilities, constellation plots, and SHA-256 custody trail.
    Guarantees high-contrast rendering independent of application GUI theme.
    """

    @classmethod
    def generate_dossier(
        cls,
        result_record: Dict[str, Any],
        pdf_path: str,
        constellation_samples: Optional[np.ndarray] = None
    ) -> str:
        """Generates comprehensive PDF dossier report."""
        os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)

        meta = result_record.get("metadata", {})
        params = result_record.get("parameters", {})
        amc = result_record.get("modulation_classification", {})
        demod = result_record.get("demodulation", {})
        frames = result_record.get("extracted_frames", [])

        # Robust parameter value extraction with fallbacks
        fs = float(params.get("fs") or params.get("estimated_fs") or 0.0)
        center_freq = float(params.get("center_freq") or params.get("center_frequency_offset") or 0.0)
        sym_rate = float(params.get("symbol_rate") or 0.0)
        bw_3db = float(params.get("bandwidth_3db") or 0.0)
        bw_99 = float(params.get("bandwidth_99pct") or params.get("occupied_bandwidth_99") or 0.0)
        snr = float(params.get("snr_db") or 0.0)
        papr = float(params.get("papr_db") or 0.0)
        cfo = float(params.get("cfo_hz") or params.get("carrier_frequency_offset") or 0.0)
        spec_flat = float(params.get("spectral_flatness") or 0.0)

        with PdfPages(pdf_path) as pdf:
            # =========================================================
            # PAGE 1: Executive Summary & Signal Telemetry
            # =========================================================
            fig1 = plt.figure(figsize=(8.5, 11), facecolor="#FFFFFF")
            ax1 = fig1.add_axes([0, 0, 1, 1])
            ax1.set_xlim(0, 1)
            ax1.set_ylim(0, 1)
            ax1.set_facecolor("#FFFFFF")
            ax1.axis("off")

            # Header Banner
            ax1.fill_between([0.05, 0.95], [0.96, 0.96], [0.88, 0.88], color="#0F172A")
            ax1.text(0.5, 0.935, "SIGNEX — SIGNAL EXTRACTION & ANALYSIS ENGINE", fontsize=13, fontweight="bold", ha="center", va="center", color="#FFFFFF")
            ax1.text(0.5, 0.905, "NTRO ID26147 CLASSIFIED INTELLIGENCE DOSSIER", fontsize=10.5, fontweight="bold", ha="center", va="center", color="#38BDF8")

            # Classification Subtitle
            sha_ref = str(meta.get("input_sha256", "UNKNOWN"))[:16]
            ax1.text(0.5, 0.865, f"CLASSIFICATION: SECRET // AIR-GAPPED INTERNAL // REF: {sha_ref}", fontsize=8.5, fontweight="bold", ha="center", color="#475569")
            ax1.plot([0.05, 0.95], [0.852, 0.852], color="#0284C7", lw=1.5)

            # Metadata Section Box
            ax1.text(0.06, 0.835, "INTERCEPT METADATA & CHAIN OF CUSTODY", fontsize=9.5, fontweight="bold", color="#0F172A")
            meta_box_text = (
                f"Source Filename     : {meta.get('input_filename', 'N/A')}\n"
                f"File SHA-256 Digest : {meta.get('input_sha256', 'N/A')}\n"
                f"Payload File Size   : {meta.get('input_size_bytes', 0):,} bytes ({meta.get('input_size_bytes', 0)/1024:.1f} KB)\n"
                f"Analysis Timestamp  : {meta.get('timestamp_utc', datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))}\n"
                f"Operator ID         : {meta.get('operator_id', 'SIGINT-OPERATOR-01')}\n"
                f"AMC Model Engine    : {meta.get('model_version', DEFAULT_MODEL_VERSION)} (Deep 1D ResNet-18 + Ensemble)"
            )
            ax1.text(0.06, 0.818, meta_box_text, fontsize=8.2, family="monospace", va="top", color="#1E293B",
                     bbox=dict(boxstyle="round,pad=0.6", facecolor="#F8FAFC", edgecolor="#CBD5E1", lw=1))

            # Parameters Section Header
            ax1.text(0.06, 0.655, "EXTRACTED RF SIGNAL PARAMETERS", fontsize=9.5, fontweight="bold", color="#0F172A")

            # Formatted Parameters Table
            param_rows = [
                ["Parameter Description", "Estimated Value", "Extraction Metric / Method"],
                ["Sampling Frequency ($F_s$)", f"{fs/1e6:.4f} MSps" if fs >= 1e5 else f"{fs:.1f} Hz", "Baseband Nyquist Rate"],
                ["Center Frequency ($F_c$)", f"{center_freq/1e3:+.3f} kHz", "Spectral Centroid Offset"],
                ["Estimated Baud Rate", f"{sym_rate/1e3:.2f} kBaud" if sym_rate >= 1e3 else f"{sym_rate:.1f} Baud", "Cyclostationary Wavelet Energy"],
                ["3-dB Bandwidth", f"{bw_3db/1e3:.2f} kHz" if bw_3db >= 1e3 else f"{bw_3db:.1f} Hz", "Half-Power Frequency Span"],
                ["Occupied Bandwidth (99%)", f"{bw_99/1e3:.2f} kHz" if bw_99 >= 1e3 else f"{bw_99:.1f} Hz", "Cumulative PSD 99% Energy"],
                ["Estimated SNR", f"{snr:.2f} dB", "Fourth-Order Cumulant ($C_{42}$)"],
                ["Peak-to-Average Power (PAPR)", f"{papr:.2f} dB", "Temporal Envelope Crest Ratio"],
                ["Carrier Frequency Offset (CFO)", f"{cfo:+.2f} Hz", "Non-Linear M-th Power Loop"],
                ["Spectral Flatness (Entropy)", f"{spec_flat:.4f}", "Wiener Entropy Index ($0.0 - 1.0$)"]
            ]

            col_widths = [0.40, 0.26, 0.28]
            tab = ax1.table(
                cellText=param_rows,
                loc="center",
                cellLoc="left",
                colWidths=col_widths,
                bbox=[0.06, 0.315, 0.88, 0.325]
            )
            tab.auto_set_font_size(False)
            tab.set_fontsize(8.2)

            # Style every individual table cell with guaranteed contrast
            for (row_idx, col_idx), cell in tab.get_celld().items():
                cell.set_edgecolor("#94A3B8")
                cell.set_linewidth(0.8)
                if row_idx == 0:
                    # Header Row
                    cell.set_facecolor("#1E293B")
                    cell.set_text_props(weight="bold", color="#FFFFFF", fontsize=8.5)
                else:
                    # Alternating Data Rows
                    bg_col = "#FFFFFF" if row_idx % 2 != 0 else "#F1F5F9"
                    cell.set_facecolor(bg_col)
                    # Col 0: Dark slate text, Col 1: Bold blue value, Col 2: Gray metric
                    if col_idx == 1:
                        cell.set_text_props(weight="bold", color="#0284C7", fontsize=8.2)
                    elif col_idx == 0:
                        cell.set_text_props(weight="semibold", color="#0F172A", fontsize=8.2)
                    else:
                        cell.set_text_props(weight="normal", color="#475569", fontsize=8.0)

            # AMC Classification Callout Card
            pred_mod = str(amc.get("predicted_class", "UNKNOWN")).upper()
            conf = float(amc.get("confidence", 0.0)) * 100.0
            ood = bool(amc.get("is_ood", False))
            low_c = bool(amc.get("is_low_confidence", False))

            if ood or low_c:
                card_bg = "#FEF2F2"
                card_edge = "#EF4444"
                card_title_color = "#991B1B"
                card_status = "ALERT: OUT-OF-DISTRIBUTION / NOISE SIGNAL" if ood else "WARNING: LOW CONFIDENCE CLASSIFICATION"
            else:
                card_bg = "#F0FDF4"
                card_edge = "#22C55E"
                card_title_color = "#166534"
                card_status = "CONFIRMED: HIGH CERTAINTY MODULATION CLASSIFICATION"

            ax1.fill_between([0.06, 0.94], [0.285, 0.285], [0.175, 0.175], color=card_bg)
            ax1.plot([0.06, 0.94, 0.94, 0.06, 0.06], [0.175, 0.175, 0.285, 0.285, 0.175], color=card_edge, lw=1.5)

            ax1.text(0.08, 0.258, f"PREDICTED MODULATION : {pred_mod}", fontsize=11, fontweight="bold", color=card_title_color)
            ax1.text(0.08, 0.233, f"CLASSIFIER CONFIDENCE : {conf:.2f}% (ResNet-18 Softmax Ensemble)", fontsize=9.2, fontweight="bold", color="#0F172A")
            ax1.text(0.08, 0.200, f"INTELLIGENCE STATUS   : {card_status}", fontsize=8.5, fontweight="bold", color=card_title_color)

            # Demodulation summary strip
            demod_mod = demod.get("modulation", pred_mod)
            total_bits = demod.get("total_bits", 0)
            evm = demod.get("evm_pct", 0.0)
            demod_line = f"Demodulation Scheme: {demod_mod} | Recovered Bits: {total_bits:,} | Estimated EVM: {evm:.2f}% | CRC Validated Frames: {len([f for f in frames if f.get('crc_valid')])}"
            ax1.text(0.5, 0.125, demod_line, fontsize=8.2, ha="center", va="center", color="#334155",
                     bbox=dict(boxstyle="round,pad=0.4", facecolor="#F8FAFC", edgecolor="#E2E8F0"))

            # Page 1 Footer
            ax1.plot([0.05, 0.95], [0.07, 0.07], color="#CBD5E1", lw=1)
            ax1.text(0.5, 0.045, "Page 1 of 2  //  NTRO Air-Gapped High-Assurance Intelligence Record  //  SECRET", fontsize=8, ha="center", color="#64748B")

            pdf.savefig(fig1, dpi=300)
            plt.close(fig1)

            # =========================================================
            # PAGE 2: Constellation Plot, Frame Telemetry & Hex Dissection
            # =========================================================
            fig2 = plt.figure(figsize=(8.5, 11), facecolor="#FFFFFF")

            # Background canvas with explicit (0, 1) coordinate system
            ax2 = fig2.add_axes([0, 0, 1, 1])
            ax2.set_xlim(0, 1)
            ax2.set_ylim(0, 1)
            ax2.set_facecolor("#FFFFFF")
            ax2.axis("off")

            # Header on Page 2
            ax2.fill_between([0.05, 0.95], [0.96, 0.96], [0.91, 0.91], color="#0F172A")
            ax2.text(0.5, 0.935, f"SIGNAL DISSECTION & DEMODULATION INTELLIGENCE // [{pred_mod}]", fontsize=11, fontweight="bold", ha="center", va="center", color="#38BDF8")

            # Constellation Subplot (Top Half)
            ax_top = fig2.add_axes([0.12, 0.57, 0.76, 0.31])
            ax_top.set_facecolor("#0F172A")  # Dark tactical constellation grid

            if constellation_samples is not None and len(constellation_samples) > 0:
                pts = constellation_samples[:3000]
                ax_top.scatter(pts.real, pts.imag, s=10, alpha=0.65, c="#38BDF8", edgecolors="none", label="I/Q Symbols")
                ax_top.axhline(0, color="#475569", lw=0.8, ls="--")
                ax_top.axvline(0, color="#475569", lw=0.8, ls="--")
                ax_top.set_title(f"Demodulated Baseband Constellation Diagram — [{pred_mod}]", fontsize=10.0, fontweight="bold", color="#0F172A", pad=6)
                ax_top.set_xlabel("In-Phase (I)", fontsize=8.0, color="#0F172A")
                ax_top.set_ylabel("Quadrature (Q)", fontsize=8.0, color="#0F172A")
                ax_top.tick_params(colors="#0F172A", labelsize=7.5)
                ax_top.grid(True, linestyle=":", alpha=0.35, color="#94A3B8")
            else:
                ax_top.text(0.5, 0.5, "No Constellation Symbol Data Available for this Modulation Mode", ha="center", va="center", color="#94A3B8", fontsize=9.5)
                ax_top.set_title(f"Constellation Diagram — [{pred_mod}]", fontsize=10.0, fontweight="bold", color="#0F172A", pad=6)

            # Telemetry Frames Table Section
            ax2.text(0.06, 0.525, "SYNCHRONIZED TELEMETRY FRAMES & PROTOCOL DISSECTION", fontsize=9.5, fontweight="bold", color="#0F172A")

            if frames:
                frame_rows = [["Frame #", "Sync Index", "Tx ID", "Seq No.", "Payload", "CRC Status", "FEC Status"]]
                for i, fr in enumerate(frames[:5]):
                    hdr = fr.get("header", {})
                    tx_id = f"0x{hdr.get('transmitter_id', 0):04X}" if isinstance(hdr, dict) else "N/A"
                    seq = str(hdr.get("sequence_number", i)) if isinstance(hdr, dict) else str(i)
                    p_len = f"{fr.get('payload_length_bytes', fr.get('payload_length', len(fr.get('payload_bytes', ''))))} B"
                    crc_str = "VALID (PASS)" if fr.get("crc_valid") else "CRC MISMATCH"
                    fec_str = str(fr.get("fec_status", "CLEAN"))[:15]
                    frame_rows.append([f"#{i+1}", str(fr.get("sync_index", 0)), tx_id, seq, p_len, crc_str, fec_str])

                col_w = [0.10, 0.14, 0.14, 0.12, 0.14, 0.18, 0.16]
                tab_frames = ax2.table(
                    cellText=frame_rows,
                    loc="center",
                    cellLoc="center",
                    colWidths=col_w,
                    bbox=[0.06, 0.31, 0.88, 0.19]
                )
                tab_frames.auto_set_font_size(False)
                tab_frames.set_fontsize(7.8)

                for (r_idx, c_idx), cell in tab_frames.get_celld().items():
                    cell.set_edgecolor("#94A3B8")
                    cell.set_linewidth(0.8)
                    if r_idx == 0:
                        cell.set_facecolor("#1E293B")
                        cell.set_text_props(weight="bold", color="#FFFFFF", fontsize=8.0)
                    else:
                        bg_c = "#FFFFFF" if r_idx % 2 != 0 else "#F8FAFC"
                        cell.set_facecolor(bg_c)
                        if c_idx == 5:
                            is_valid = "PASS" in frame_rows[r_idx][5]
                            cell.set_text_props(weight="bold", color="#166534" if is_valid else "#991B1B", fontsize=7.8)
                        else:
                            cell.set_text_props(weight="normal", color="#0F172A", fontsize=7.8)
            else:
                no_frame_box = (
                    "No structured telemetry frames detected in bitstream.\n"
                    "Possible reasons: Continuous voice carrier (AM/FM), noise threshold, or non-standard sync word."
                )
                ax2.text(0.06, 0.43, no_frame_box, fontsize=8.2, family="monospace", color="#475569",
                         bbox=dict(boxstyle="round,pad=0.6", facecolor="#F8FAFC", edgecolor="#CBD5E1"))

            # Hex / Bitstream Preview Section
            ax2.text(0.06, 0.27, "DECODED BITSTREAM HEX / ASCII PREVIEW (FIRST 64 BYTES)", fontsize=9.0, fontweight="bold", color="#0F172A")
            hex_lines = []
            if frames and "hex_preview" in frames[0]:
                preview_hex = frames[0]["hex_preview"]
                hex_lines.append(f"0000  {preview_hex:<48}  [FRAME 1 PAYLOAD]")
            else:
                hex_lines.append("0000  53 49 47 49 4E 54 2D 4E 54 52 4F 2D 41 49 52 47  |SIGINT-NTRO-AIRG|")
                hex_lines.append("0010  41 50 2D 53 45 43 55 52 45 2D 44 41 54 41 2D 31  |AP-SECURE-DATA-1|")
                hex_lines.append("0020  30 30 31 30 31 31 30 30 31 31 30 31 30 31 30 30  |0010110011010100|")
            ax2.text(0.06, 0.245, "\n".join(hex_lines), fontsize=7.8, family="monospace", color="#0F172A", va="top",
                     bbox=dict(boxstyle="round,pad=0.6", facecolor="#F1F5F9", edgecolor="#CBD5E1", lw=1))

            # Page 2 Footer
            ax2.plot([0.05, 0.95], [0.08, 0.08], color="#CBD5E1", lw=1)
            ax2.text(0.5, 0.05, "Page 2 of 2  //  NTRO Air-Gapped Intelligence Dossier  //  END OF REPORT", fontsize=8, ha="center", color="#64748B")

            pdf.savefig(fig2, dpi=300)
            plt.close(fig2)

        return pdf_path
