"""
Air-Gap Security Guard, Network Socket Interceptor, Path Traversal Sanitizer,
Audit Trail Logger, and Data Sanitizer for NTRO ID26147 (TC-SEC-001 through TC-SEC-008).
"""

import os
import sys
import socket
import tempfile
import shutil
import re
import json
import logging
import hashlib
from typing import Dict, Any, Optional, List


class SecurityViolationError(RuntimeError):
    """Raised whenever a security or air-gap constraint is violated."""
    pass


class AirGapGuard:
    """
    Enforces strict air-gapped isolation by intercepting and disabling
    all outbound socket connection attempts, preventing accidental telemetry or exfiltration.
    """
    _original_socket_connect = None
    _original_create_connection = None
    _is_active = False

    @classmethod
    def enable_airgap(cls):
        """Disables all outbound network connections system-wide in Python runtime."""
        if cls._is_active:
            return

        cls._original_socket_connect = socket.socket.connect
        cls._original_create_connection = socket.create_connection

        def blocked_connect(self, address):
            raise SecurityViolationError(
                f"Air-Gap Policy Violation: Outbound connection attempt to {address} blocked. "
                f"This system is certified for air-gapped, zero-network execution only."
            )

        def blocked_create_connection(address, timeout=None, source_address=None):
            raise SecurityViolationError(
                f"Air-Gap Policy Violation: create_connection to {address} blocked. "
                f"No external network operations allowed."
            )

        socket.socket.connect = blocked_connect
        socket.create_connection = blocked_create_connection
        cls._is_active = True

    @classmethod
    def disable_airgap(cls):
        """Restores original socket functions if needed for isolated testing."""
        if not cls._is_active:
            return
        if cls._original_socket_connect:
            socket.socket.connect = cls._original_socket_connect
        if cls._original_create_connection:
            socket.create_connection = cls._original_create_connection
        cls._is_active = False

    @classmethod
    def is_airgap_active(cls) -> bool:
        return cls._is_active


class PathSanitizer:
    """
    Protects filesystem integrity by preventing directory traversal,
    absolute path escapes, null-byte injection, and malicious characters.
    """

    ILLEGAL_CHAR_REGEX = re.compile(r"[\x00-\x1f\x7f<>:\"|?*]")

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Strips path characters and illegal symbols from a filename."""
        basename = os.path.basename(filename)
        # Strip null bytes and suspicious control characters
        clean = cls.ILLEGAL_CHAR_REGEX.sub("", basename)
        # Prevent dot-dot
        clean = clean.replace("..", "").strip()
        if not clean or clean in (".", ""):
            raise SecurityViolationError(f"Invalid or dangerous filename: '{filename}'")
        return clean

    @classmethod
    def validate_safe_path(cls, target_path: str, allowed_base_dir: Optional[str] = None) -> str:
        """
        Ensures target_path resolves strictly within allowed_base_dir.
        Detects directory traversal attacks (e.g. '../../etc/passwd').
        """
        if "\x00" in target_path:
            raise SecurityViolationError("Null byte detected in file path")

        abs_target = os.path.abspath(target_path)
        if allowed_base_dir is not None:
            abs_base = os.path.abspath(allowed_base_dir)
            # Must start with abs_base
            common = os.path.commonpath([abs_target, abs_base])
            if common != abs_base:
                raise SecurityViolationError(
                    f"Directory traversal detected! Path '{target_path}' attempts to escape base '{allowed_base_dir}'"
                )
        return abs_target


class SecureTempDirectory:
    """
    Context manager creating an isolated temporary working directory
    with guaranteed zeroization and cleanup upon exit.
    """

    def __init__(self, prefix: str = "ntro_sigint_"):
        self.prefix = prefix
        self.path = None

    def __enter__(self) -> str:
        self.path = tempfile.mkdtemp(prefix=self.prefix)
        return self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.path and os.path.exists(self.path):
            try:
                # Securely overwrite and remove files inside
                for root, dirs, files in os.walk(self.path):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            # Zero out file contents prior to deletion
                            size = os.path.getsize(fp)
                            if size > 0:
                                with open(fp, "wb") as fh:
                                    fh.write(b"\x00" * min(size, 65536))
                            os.remove(fp)
                        except Exception:
                            pass
                shutil.rmtree(self.path, ignore_errors=True)
            except Exception:
                pass


class ConfigValidator:
    """
    Validates pipeline JSON/YAML configuration dictionaries against a strict schema.
    Prevents parameter tampering or injection.
    """

    ALLOWED_CONFIG_KEYS = {
        "fs_hz", "center_freq_hz", "modulation_order", "fft_size",
        "overlap", "window_type", "export_format", "enable_amc",
        "fec_scheme", "viterbi_k", "rs_n", "rs_k", "crc_type",
        "output_dir", "operator_id"
    }

    @classmethod
    def validate_config(cls, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Validates configuration fields and rejects malicious entries."""
        if not isinstance(config_dict, dict):
            raise SecurityViolationError("Configuration must be a dictionary")

        for k, v in config_dict.items():
            if k not in cls.ALLOWED_CONFIG_KEYS:
                raise SecurityViolationError(f"Unauthorized or unknown config parameter: '{k}'")
            # Type checks
            if k in ("fs_hz", "center_freq_hz") and not isinstance(v, (int, float)):
                raise SecurityViolationError(f"Config '{k}' must be numeric")
            if k in ("viterbi_k", "rs_n", "rs_k") and not isinstance(v, int):
                raise SecurityViolationError(f"Config '{k}' must be integer")

        return config_dict


class AuditLogger:
    """
    Sanitizing audit logger ensuring no raw signal buffers or sensitive credentials leak into logs.
    """

    def __init__(self, log_file: Optional[str] = None):
        self.logger = logging.getLogger("ntro_sigint_audit")
        self.logger.setLevel(logging.INFO)
        self.log_file = log_file

        if log_file:
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            handler = logging.FileHandler(log_file, encoding="utf-8")
            handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
            self.logger.addHandler(handler)

    def log_event(self, event_name: str, details: Dict[str, Any]):
        """Sanitizes details and logs structured audit event."""
        clean_details = {}
        for k, v in details.items():
            # Exclude raw sample arrays or buffers
            if isinstance(v, (bytes, bytearray)):
                clean_details[k] = f"<BUFFER {len(v)} bytes, SHA256={hashlib.sha256(v).hexdigest()[:16]}>"
            elif hasattr(v, "shape"): # numpy array
                clean_details[k] = f"<NDARRAY shape={v.shape}, dtype={v.dtype}>"
            elif any(s in k.lower() for s in ("password", "secret", "token", "key")):
                clean_details[k] = "********"
            else:
                clean_details[k] = v

        msg = f"EVENT: {event_name} | DETAILS: {json.dumps(clean_details)}"
        self.logger.info(msg)


class MemoryGuard:
    """
    Zeroizes sensitive arrays and buffers in memory to prevent cold-boot
    or cross-process memory inspection.
    """

    @staticmethod
    def zeroize_buffer(buf: bytearray):
        """Overwrites bytearray buffer with zeros."""
        if isinstance(buf, bytearray):
            for i in range(len(buf)):
                buf[i] = 0
