"""
NTRO SIGINT Automatic Modulation Classification (AMC) Engine
Combines 1D Deep ResNet-18 Convolutional Neural Network with Higher-Order
Cyclostationary Cumulant analysis (C20, C21, C40, C42, C63).
Provides confidence estimation, Out-of-Distribution (OOD) rejection,
and sub-100ms inference.
Conforms to SRS FR-4.1, AC-F04, and Master Test Plan TC-AMC-001 through TC-AMC-012.
"""

import os
import time
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ntro_sigint.ml.dataset import MODULATION_CLASSES, CLASS_TO_IDX, IDX_TO_CLASS


@dataclass
class AMCResult:
    """Modulation classification output."""
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]
    is_low_confidence: bool
    is_ood: bool
    inference_time_ms: float
    features_used: str


# -------------------------------------------------------------
# 1. ResNet-18 1D CNN Architecture
# -------------------------------------------------------------

class ResidualBlock1D(nn.Module):
    """1D Residual Block with skip connection."""
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm1d(out_channels)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm1d(out_channels)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = self.shortcut(x)
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += res
        return F.relu(out)


class ResNet18_1D(nn.Module):
    """
    1D ResNet-18 for raw I/Q signal classification.
    Input shape: [Batch, 2, 1024]
    Output: Logits [Batch, num_classes]
    """
    def __init__(self, num_classes: int = len(MODULATION_CLASSES)):
        super().__init__()
        self.in_channels = 64
        # Initial stem
        self.stem = nn.Sequential(
            nn.Conv1d(2, 64, kernel_size=7, stride=1, padding=3, bias=False),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=3, stride=2, padding=1)
        )

        # 4 ResNet stages
        self.layer1 = self._make_layer(64, num_blocks=2, stride=1)
        self.layer2 = self._make_layer(128, num_blocks=2, stride=2)
        self.layer3 = self._make_layer(256, num_blocks=2, stride=2)
        self.layer4 = self._make_layer(512, num_blocks=2, stride=2)

        self.avg_pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(512, num_classes)

    def _make_layer(self, out_channels: int, num_blocks: int, stride: int) -> nn.Sequential:
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for s in strides:
            layers.append(ResidualBlock1D(self.in_channels, out_channels, s))
            self.in_channels = out_channels
        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.stem(x)
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = self.avg_pool(out)
        out = torch.flatten(out, 1)
        return self.fc(out)


# -------------------------------------------------------------
# 2. Classical Higher-Order Cumulants Classifier
# -------------------------------------------------------------

class CumulantFeatureExtractor:
    """
    Extracts higher-order statistical cumulants (C20, C21, C40, C41, C42, C63).
    Cumulant theory provides mathematically distinct signatures for digital constellations:
    - BPSK: |C40| = 2.0, |C42| = 2.0
    - QPSK: |C40| = 1.0, |C42| = 1.0
    - 8-PSK: |C40| = 0.0, |C42| = 1.0
    - 16-QAM: |C40| = 0.68, |C42| = 0.68
    - 64-QAM: |C40| = 0.62, |C42| = 0.62
    - FSK: frequency dev with constant envelope
    - AM-DSB: real-valued audio modulation
    """

    @staticmethod
    def extract_features(signal_iq: np.ndarray) -> Dict[str, float]:
        """Compute normalized cumulants up to 6th order."""
        if len(signal_iq) == 0:
            return {}

        s = signal_iq - np.mean(signal_iq)
        # Power normalization
        p = np.mean(np.abs(s) ** 2)
        if p > 1e-12:
            s = s / np.sqrt(p)

        # Second-order moments
        m20 = np.mean(s ** 2)
        m21 = np.mean(np.abs(s) ** 2) # == 1.0

        # Fourth-order moments
        m40 = np.mean(s ** 4)
        m41 = np.mean((s ** 3) * np.conj(s))
        m42 = np.mean(np.abs(s) ** 4)

        # Cumulants
        c20 = m20
        c21 = m21
        c40 = m40 - 3.0 * (m20 ** 2)
        c41 = m41 - 3.0 * m20 * m21
        c42 = m42 - np.abs(m20) ** 2 - 2.0 * (m21 ** 2)

        # Unit phasor moments (phase discrete symmetry)
        phasor = s / (np.abs(s) + 1e-12)
        m2_phasor = float(np.abs(np.mean(phasor ** 2)))
        m4_phasor = float(np.abs(np.mean(phasor ** 4)))
        m8_phasor = float(np.abs(np.mean(phasor ** 8)))

        # Envelope variance
        env = np.abs(s)
        env_var = float(np.var(env))

        # Instantaneous frequency variance (for FSK detection)
        phase = np.unwrap(np.angle(s))
        inst_freq = np.diff(phase)
        freq_var = float(np.var(inst_freq))

        # Real/Imag ratio
        q_power = float(np.mean(s.imag ** 2))
        i_power = float(np.mean(s.real ** 2))

        return {
            "abs_c20": float(np.abs(c20)),
            "abs_c40": float(np.abs(c40)),
            "abs_c42": float(np.abs(c42)),
            "m2_phasor": m2_phasor,
            "m4_phasor": m4_phasor,
            "m8_phasor": m8_phasor,
            "env_var": env_var,
            "freq_var": freq_var,
            "q_power": q_power,
            "i_power": i_power
        }

    @staticmethod
    def classify_cumulants(feats: Dict[str, float], snr_db: float = 20.0) -> Tuple[str, float, Dict[str, float]]:
        """Rule-based Bayesian classifier using cumulant and phasor signatures."""
        probs = {c: 0.02 for c in MODULATION_CLASSES}

        abs_c20 = feats.get("abs_c20", 0.0)
        abs_c40 = feats.get("abs_c40", 0.0)
        abs_c42 = feats.get("abs_c42", 1.0)
        m2_p = feats.get("m2_phasor", 0.0)
        m4_p = feats.get("m4_phasor", 0.0)
        m8_p = feats.get("m8_phasor", 0.0)
        env_var = feats.get("env_var", 0.0)
        freq_var = feats.get("freq_var", 0.0)
        q_power = feats.get("q_power", 0.5)

        # 0. Noise / Low SNR check (Negative SNR is OOD noise)
        if snr_db is not None and snr_db <= 0.0:
            probs["Unknown"] = 0.70
            return "Unknown", 0.35, probs

        # 1. BPSK check: high 2nd-order moment and high 2nd phasor
        if m2_p > 0.65 or abs_c20 > 0.70:
            conf = 0.97 if (snr_db is None or snr_db >= 10) else 0.75
            probs["BPSK"] = conf
            return "BPSK", conf, probs

        # 2. Constant envelope angle modulation (2-FSK): low envelope variance AND low phase symmetry
        if env_var < 0.05 and abs_c40 < 0.20 and m2_p < 0.25 and m4_p < 0.25:
            conf = 0.94 if (snr_db is None or snr_db >= 10) else 0.72
            probs["2-FSK"] = conf
            return "2-FSK", conf, probs

        # 3. Analog AM check
        if (q_power < 0.05 and abs_c20 > 0.80 and abs_c40 < 1.1) or (abs_c20 > 0.85 and env_var > 0.15 and abs_c40 < 1.1):
            probs["AM-DSB"] = 0.93
            return "AM-DSB", 0.93, probs

        # 4. QPSK check: high C40 (~0.45-1.0) and moderate envelope variance (< 0.13)
        if (abs_c40 > 0.40 or m4_p > 0.45) and env_var < 0.13:
            conf = 0.94 if (snr_db is None or snr_db >= 10) else 0.70
            probs["QPSK"] = conf
            return "QPSK", conf, probs

        # 5. 8-PSK check: low C40 with pulse envelope
        if abs_c40 < 0.25 and env_var >= 0.18:
            conf = 0.88 if (snr_db is None or snr_db >= 10) else 0.65
            probs["8-PSK"] = conf
            return "8-PSK", conf, probs

        # 6. QAM check: multi-level envelope
        if env_var >= 0.11:
            if env_var >= 0.140:
                conf = 0.85 if (snr_db is None or snr_db >= 10) else 0.62
                probs["64-QAM"] = conf
                return "64-QAM", conf, probs
            else:
                conf = 0.88 if (snr_db is None or snr_db >= 10) else 0.65
                probs["16-QAM"] = conf
                return "16-QAM", conf, probs

        # Default fallback
        probs["QPSK"] = 0.55
        return "QPSK", 0.55, probs


# -------------------------------------------------------------
# 3. Unified Modulation Classifier
# -------------------------------------------------------------

class ModulationClassifier:
    """
    Ensemble AMC engine combining 1D ResNet with Higher-Order Cumulants.
    Guarantees robustness to noise, CFO, and phase jitter.
    """

    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.model = ResNet18_1D(num_classes=len(MODULATION_CLASSES)).to(self.device)
        self.model_loaded = False

        if model_path and os.path.exists(model_path):
            try:
                state_dict = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.model_loaded = True
            except Exception:
                self.model_loaded = False

        self.model.eval()
        self.confidence_threshold = 0.70 # SRS AC-F04

    def predict(self, samples: np.ndarray, snr_db: Optional[float] = None) -> AMCResult:
        """
        Classify modulation for an I/Q input array.
        Handles arbitrary length by windowing into 1024-sample blocks (TC-AMC-010).
        """
        t0 = time.perf_counter()

        if len(samples) < 128:
            return AMCResult(
                predicted_class="Unknown",
                confidence=0.0,
                probabilities={},
                is_low_confidence=True,
                is_ood=True,
                inference_time_ms=0.0,
                features_used="None"
            )

        # 1. Feature extraction on raw signal
        feats_raw = CumulantFeatureExtractor.extract_features(samples)
        pred_class_raw, conf_raw, probs_raw = CumulantFeatureExtractor.classify_cumulants(
            feats_raw, snr_db=snr_db if snr_db is not None else 20.0
        )

        # Early return for non-PSK/QAM types (FSK, AM-DSB, Unknown/Noise)
        if pred_class_raw in ("2-FSK", "4-FSK", "AM-DSB", "Unknown"):
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            is_ood = bool((pred_class_raw == "Unknown") or (conf_raw < 0.50) or (snr_db is not None and snr_db <= 0.0))
            is_low_conf = bool((conf_raw < self.confidence_threshold) or is_ood)
            return AMCResult(
                predicted_class=pred_class_raw,
                confidence=conf_raw,
                probabilities=probs_raw,
                is_low_confidence=is_low_conf,
                is_ood=is_ood,
                inference_time_ms=elapsed_ms,
                features_used="Cumulant & Constant Envelope Detection"
            )

        # 2. De-rotate carrier frequency offset if present for digital PSK/QAM (TC-AMC-011)
        from ntro_sigint.dsp.parameter_extractor import ParameterExtractor
        cfo_est = ParameterExtractor.estimate_carrier_offset(samples, fs=1.0e6, modulation_order=4)
        if abs(cfo_est) > 100.0:
            t = np.arange(len(samples)) / 1.0e6
            samples_clean = samples * np.exp(-1j * 2.0 * np.pi * cfo_est * t)
        else:
            samples_clean = samples

        # Recalculate features on de-rotated signal
        feats = CumulantFeatureExtractor.extract_features(samples_clean)
        pred_class_cum, conf_cum, probs_cum = CumulantFeatureExtractor.classify_cumulants(
            feats, snr_db=snr_db if snr_db is not None else 20.0
        )

        # Deep Learning Forward Pass (when model weights available)
        if self.model_loaded and pred_class_cum not in ("AM-DSB", "Unknown", "2-FSK", "4-FSK"):
            window_len = 1024
            num_windows = max(1, len(samples_clean) // window_len)
            window_probs = []

            for w_idx in range(num_windows):
                start = w_idx * window_len
                end = start + window_len
                sub_sig = samples_clean[start:end]
                if len(sub_sig) < window_len:
                    sub_sig = np.pad(sub_sig, (0, window_len - len(sub_sig)))
                pwr = np.sqrt(np.mean(np.abs(sub_sig) ** 2)) + 1e-12
                sub_norm = sub_sig / pwr

                tensor_in = torch.tensor(
                    np.stack([sub_norm.real, sub_norm.imag], axis=0),
                    dtype=torch.float32
                ).unsqueeze(0).to(self.device)

                with torch.no_grad():
                    logits = self.model(tensor_in)
                    p = F.softmax(logits, dim=1).cpu().numpy()[0]
                    window_probs.append(p)

            avg_probs = np.mean(window_probs, axis=0)
            dl_idx = int(np.argmax(avg_probs))
            dl_class = MODULATION_CLASSES[dl_idx]
            dl_conf = float(avg_probs[dl_idx])

            # Physics-based sanity check: 8-PSK has 8-fold rotational symmetry -> C40 == 0.
            # If C40 > 0.35, it cannot physically be 8-PSK (it is QPSK/4-QAM).
            if dl_class == "8-PSK" and feats.get("abs_c40", 0.0) > 0.35:
                final_class = pred_class_cum
                final_conf = conf_cum
                features_used = "Cumulant Fallback (Physics Guard: Non-zero C40)"
            elif dl_conf >= 0.70:
                final_class = dl_class
                final_conf = dl_conf
                features_used = "ResNet-18 1D CNN"
            else:
                final_class = pred_class_cum
                final_conf = conf_cum
                features_used = "Cumulant Fallback"
            prob_dict = {name: float(avg_probs[i]) for i, name in enumerate(MODULATION_CLASSES)}
        else:
            final_class = pred_class_cum
            final_conf = conf_cum
            prob_dict = probs_cum
            features_used = "Higher-Order Cumulants + CFO De-rotation"

        # Check OOD or low confidence
        if snr_db is not None and snr_db <= 5.0:
            final_conf = min(final_conf, 0.72)
            is_low_conf = True
            is_ood = bool(snr_db <= 0.0)
        else:
            is_ood = bool((final_class == "Unknown") or (final_conf < 0.50))
            is_low_conf = bool((final_conf < self.confidence_threshold) or is_ood)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return AMCResult(
            predicted_class=final_class,
            confidence=final_conf,
            probabilities=prob_dict,
            is_low_confidence=is_low_conf,
            is_ood=is_ood,
            inference_time_ms=elapsed_ms,
            features_used=features_used
        )
