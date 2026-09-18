"""
Unified End-to-End Signal Analysis Pipeline Orchestrator.
Coordinates: Ingestion -> Preprocessing -> Parameter Extraction -> AMC -> Demodulation -> De-interleaving -> FEC -> Correlation -> Export.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List, Tuple
import os
import time
import numpy as np

from ntro_sigint.core.ingestion import SignalReader, SignalData
from ntro_sigint.core.preprocessor import SignalPreprocessor
from ntro_sigint.dsp.parameter_extractor import ParameterExtractor, SignalParameters
from ntro_sigint.ml.amc_classifier import ModulationClassifier, AMCResult
from ntro_sigint.dsp.demodulator import Demodulator, DemodResult
from ntro_sigint.decoding.interleaver import BlockInterleaver
from ntro_sigint.decoding.fec import ConvolutionalCodec, ReedSolomonGF8
from ntro_sigint.correlation.correlator import BitstreamCorrelator, BARKER_13, ParsedFrame
from ntro_sigint.core.exporter import ResultStore, PDFReportGenerator
from ntro_sigint.core.security import AirGapGuard, PathSanitizer


@dataclass
class PipelineExecutionResult:
    """Consolidated outcome of the end-to-end signal intelligence analysis."""
    input_file: str
    sample_rate: float
    duration_sec: float
    parameters: Dict[str, Any]
    classification: Dict[str, Any]
    demodulation: Dict[str, Any]
    frames: List[Dict[str, Any]]
    exported_files: Dict[str, str]
    execution_time_sec: float


class SignalAnalysisPipeline:
    """
    Main pipeline orchestrator for air-gapped SIGINT operations.
    Thread-safe and stateless per-run.
    """

    def __init__(self, model_path: Optional[str] = "models/amc_resnet18.pt", enforce_airgap: bool = True):
        self.model_path = model_path
        if enforce_airgap:
            AirGapGuard.enable_airgap()
        self.classifier = ModulationClassifier(model_path=self.model_path)

    def process_file(
        self,
        filepath: str,
        output_dir: Optional[str] = None,
        fs_override: Optional[float] = None,
        sync_word: Optional[np.ndarray] = None,
        generate_pdf: bool = True,
        deinterleaver_config: Optional[Tuple[int, int]] = None,
        fec_scheme: Optional[str] = None
    ) -> PipelineExecutionResult:
        """
        Executes full end-to-end SIGINT extraction pipeline on a recording.
        """
        t_start = time.perf_counter()
        clean_path = PathSanitizer.validate_safe_path(filepath)

        # 1. Ingestion
        sig_data = SignalReader.load(clean_path, sample_rate=fs_override)
        raw_samples = sig_data.samples
        fs = sig_data.sample_rate
        duration = len(raw_samples) / fs

        # 2. Preprocessing
        clean_samples, prep_stats = SignalPreprocessor.full_pipeline(
            raw_samples, dc_block=True, balance_iq=True, normalize=True
        )

        # 3. Parameter Extraction
        params = ParameterExtractor.extract_all(clean_samples, fs)
        param_dict = params.to_dict()
        param_dict["fs"] = float(params.estimated_fs)
        param_dict["center_freq"] = float(params.center_frequency_offset)
        param_dict["bandwidth_99pct"] = float(params.occupied_bandwidth_99)
        param_dict["cfo_hz"] = float(params.carrier_frequency_offset)

        # 4. Automatic Modulation Classification
        amc_window = clean_samples[:4096] if len(clean_samples) >= 4096 else clean_samples
        amc_res = self.classifier.predict(amc_window, snr_db=params.snr_db)
        amc_dict = {
            "predicted_class": amc_res.predicted_class,
            "confidence": float(amc_res.confidence),
            "is_low_confidence": amc_res.is_low_confidence,
            "is_ood": amc_res.is_ood,
            "probabilities": amc_res.probabilities,
            "features_used": amc_res.features_used
        }

        # 5. Demodulation
        mod_type = amc_res.predicted_class if amc_res.predicted_class in ("BPSK", "QPSK", "8-PSK", "16-QAM", "64-QAM", "2-FSK") else "QPSK"
        demod_out = Demodulator.demodulate(clean_samples, mod_type=mod_type, apply_carrier_sync=True)

        demod_dict = {
            "modulation": demod_out.modulation_type,
            "total_bits": demod_out.num_bits,
            "evm_pct": demod_out.estimated_evm_pct,
            "carrier_phase_error": demod_out.carrier_phase_error
        }

        # 6. De-interleaving & FEC (if configured)
        bits = demod_out.bits
        if deinterleaver_config is not None:
            r, c = deinterleaver_config
            bits = BlockInterleaver.deinterleave(bits, r, c)

        if fec_scheme == "viterbi_k7":
            codec = ConvolutionalCodec(k=7)
            bits, _ = codec.decode(bits)

        # 7. Bitstream Correlation & Telemetry Framing
        frames_summary = []
        frames = []
        if amc_res.predicted_class not in ("Unknown", "AM-DSB", "WBFM") and not amc_res.is_ood:
            marker = sync_word if sync_word is not None else BARKER_13
            frames = BitstreamCorrelator.extract_all_frames(bits, sync_word=marker, max_errors=1)
            for fr in frames[:100]:
                frames_summary.append({
                    "sync_index": fr.sync_index,
                    "header": fr.header,
                    "payload_length_bytes": len(fr.payload_bytes),
                    "crc_valid": fr.crc_valid,
                    "fec_status": fr.fec_status,
                    "hex_preview": fr.payload_bytes[:16].hex().upper()
                })

        # 8. Result Persistence & Export
        exported_files = {}
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(clean_path))[0]
            record = ResultStore.build_result_record(
                input_filepath=clean_path,
                parameters=param_dict,
                amc_result=amc_dict,
                demod_stats=demod_dict,
                extracted_frames=frames_summary
            )

            # JSON export
            json_out = os.path.join(output_dir, f"{base_name}_analysis.json")
            ResultStore.save_json(record, json_out)
            exported_files["json"] = json_out

            # PDF report export
            if generate_pdf:
                pdf_out = os.path.join(output_dir, f"{base_name}_dossier.pdf")
                PDFReportGenerator.generate_dossier(record, pdf_out, constellation_samples=demod_out.symbols)
                exported_files["pdf"] = pdf_out

            # Payload export
            if frames:
                payload_out = os.path.join(output_dir, f"{base_name}_payload.bin")
                with open(payload_out, "wb") as pf:
                    pf.write(frames[0].payload_bytes if hasattr(frames[0], "payload_bytes") else b"")
                exported_files["payload"] = payload_out

        t_elapsed = time.perf_counter() - t_start

        return PipelineExecutionResult(
            input_file=clean_path,
            sample_rate=fs,
            duration_sec=duration,
            parameters=param_dict,
            classification=amc_dict,
            demodulation=demod_dict,
            frames=frames_summary,
            exported_files=exported_files,
            execution_time_sec=t_elapsed
        )

    def process_batch(
        self,
        file_list: List[str],
        output_dir: str,
        generate_pdf: bool = True
    ) -> Dict[str, Any]:
        """Processes multiple recordings sequentially and generates a batch manifest."""
        os.makedirs(output_dir, exist_ok=True)
        manifest_items = []
        batch_start = time.perf_counter()

        for fp in file_list:
            try:
                res = self.process_file(fp, output_dir=output_dir, generate_pdf=generate_pdf)
                manifest_items.append({
                    "input_file": fp,
                    "status": "SUCCESS",
                    "predicted_class": res.classification["predicted_class"],
                    "confidence": res.classification["confidence"],
                    "json_deliverable": res.exported_files.get("json", ""),
                    "pdf_dossier": res.exported_files.get("pdf", ""),
                    "duration_sec": res.execution_time_sec
                })
            except Exception as e:
                manifest_items.append({
                    "input_file": fp,
                    "status": "FAILED",
                    "error": str(e)
                })

        manifest_path = os.path.join(output_dir, "batch_manifest.json")
        ResultStore.export_batch_manifest(manifest_items, manifest_path)
        total_time = time.perf_counter() - batch_start

        return {
            "total_files": len(file_list),
            "manifest_path": manifest_path,
            "items": manifest_items,
            "total_execution_time_sec": total_time
        }
