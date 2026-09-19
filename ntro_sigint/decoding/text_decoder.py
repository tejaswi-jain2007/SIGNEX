"""
NTRO SIGINT Text & Intelligence Message Decoder.
Recovers plain English text messages, telemetry fields, and mission payloads
from demodulated bitstreams and synchronized frames.

Supports:
- 8-phase bit shift auto-alignment (offsets 0..7)
- 180-degree / 90-degree phase ambiguity polarity reversal (normal & inverted)
- Word segmentation and English readability scoring
- Frame payload text extraction
- Key-Value telemetry parsing (TARGET, COORDS, BEACON, MSG, STATUS, FREQ, etc.)
"""

import re
import string
from typing import Dict, Any, List, Tuple, Optional
import numpy as np


COMMON_ENGLISH_WORDS = {
    # Pronouns & basic words
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
    "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up",
    "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time",
    "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think",
    "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even",
    "new", "want", "because", "any", "these", "give", "day", "most", "us", "is", "am", "are", "was",
    "were", "been", "has", "had", "did", "does", "done", "got", "get", "going", "went", "gone",
    # Emergency, Distress & Military / Intelligence vocabulary
    "need", "help", "sos", "mayday", "save", "emergency", "stop", "request", "urgent", "danger",
    "alert", "please", "lost", "found", "fire", "assist", "alive", "survivor", "medical", "evac",
    "rescue", "code", "red", "blue", "green", "black", "white", "yellow", "orange", "gold",
    "hello", "world", "base", "command", "location", "position", "coordinates", "satellite", "signal",
    "contact", "confirm", "roger", "over", "out", "attack", "defense", "safe", "warning", "caution",
    "info", "report", "transmission", "target", "ntro", "sigint", "coord", "alpha", "bravo",
    "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima",
    "mike", "november", "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform", "victor",
    "whiskey", "xray", "yankee", "zulu", "status", "lock", "frequency", "mission", "carrier",
    "recon", "sensor", "packet", "telemetry", "secure", "radio", "intel", "clear", "active",
    "latitude", "longitude", "node", "beacon", "test", "ready", "data", "pass", "fail", "nominal",
    "altitude", "temp", "temperature", "voltage", "power", "battery", "gps", "speed", "heading",
    "unit", "crew", "squad", "team", "hq", "sector", "zone", "border", "airspace", "radar", "jamming",
    "immediate", "backup", "grid", "strike", "convoy", "patrol", "agent", "channel", "protocol",
    "cipher", "key", "stream", "send", "receiving", "incoming", "outgoing", "threat", "objective",
    "station", "operator", "source", "dest", "destination", "ack", "nack", "ping", "pong", "error",
    "system", "intelligence", "signex", "sightex", "aircraft", "flight", "drone", "vehicle", "ship",
    "base", "ground", "tower", "radio", "contact", "support", "identified", "hostile", "friendly"
}


class TextPayloadDecoder:
    """
    Intelligent Bitstream-to-English Message Decoder for SIGINT Workstations.
    """

    @staticmethod
    def bits_to_bytes(bits: np.ndarray) -> bytes:
        """Packs a 1D binary bit array into bytes."""
        n_pad = (8 - (len(bits) % 8)) % 8
        if n_pad > 0:
            padded = np.pad(bits, (0, n_pad), mode="constant")
        else:
            padded = bits
        return np.packbits(padded.astype(np.uint8)).tobytes()

    @staticmethod
    def extract_repeating_unit(phrase: str) -> str:
        """Finds if a phrase is a repeating sentence like 'I NEED HELP I NEED HELP...'."""
        words = phrase.split()
        if len(words) <= 1:
            return phrase
        # Check subphrase lengths from 1 word up to len/2
        for l in range(1, min(30, len(words) // 2 + 1)):
            unit_words = words[:l]
            unit_str = " ".join(unit_words)
            match_count = 0
            for i, w in enumerate(words):
                if w.upper() == unit_words[i % l].upper():
                    match_count += 1
                else:
                    break
            # If at least 2 full cycles match and covers almost the entire stream
            if match_count >= 2 * l and match_count >= len(words) - 2:
                return unit_str
        return phrase

    @classmethod
    def score_text_readability(cls, raw_bytes: bytes) -> Tuple[float, str, List[str]]:
        """
        Evaluates the readability of a byte array as English text.
        Returns (score, clean_text, extracted_words).
        """
        if not raw_bytes:
            return 0.0, "", []

        # Printable ASCII test
        printable_count = 0
        total_len = len(raw_bytes)
        clean_chars = []

        for b in raw_bytes:
            if 32 <= b <= 126 or b in (9, 10, 13):  # Standard printable + whitespace
                clean_chars.append(chr(b))
                printable_count += 1
            else:
                clean_chars.append(" ")

        clean_text = "".join(clean_chars)
        printable_ratio = printable_count / max(1, total_len)

        # Extract words (length >= 1 to capture 'I' and 'A')
        raw_words = re.findall(r"\b[A-Za-z0-9_-]+\b", clean_text)
        if not raw_words:
            return printable_ratio * 20.0, clean_text, []

        words = [w for w in raw_words if len(w) > 1 or w.lower() in ("i", "a")]
        if not words:
            return printable_ratio * 20.0, clean_text, []

        english_matches = sum(1 for w in words if w.lower() in COMMON_ENGLISH_WORDS)
        word_ratio = english_matches / max(1, len(words))

        # Check for average word length sanity (2 to 10 chars is typical natural language)
        avg_len = sum(len(w) for w in words) / max(1, len(words))
        len_penalty = 1.0 if (2.0 <= avg_len <= 10.0) else 0.5

        # Combined readability score: 0.0 to 100.0
        score = ((printable_ratio * 50.0) + (word_ratio * 50.0)) * len_penalty
        if english_matches >= 2:
            score += 25.0  # Coherent sentence bonus
        return float(min(100.0, score)), clean_text, words

    @classmethod
    def decode_bitstream(
        cls,
        bits: np.ndarray,
        frame_payloads: Optional[List[bytes]] = None
    ) -> Dict[str, Any]:
        """
        Executes multi-alignment analysis and frame dissection to recover the
        hidden English message from demodulated bits.
        """
        if bits is None or len(bits) == 0:
            return {
                "has_message": False,
                "primary_message": "NO SIGNAL BITS AVAILABLE",
                "clean_text_stream": "",
                "extracted_strings": [],
                "confidence_pct": 0.0,
                "best_alignment": "None",
                "telemetry_tags": {},
                "summary": "No bitstream data present for message decoding."
            }

        candidates = []

        # 1. Check Frame Payloads (if Barker/sync frames were extracted)
        if frame_payloads:
            for idx, p_bytes in enumerate(frame_payloads[:10]):
                if len(p_bytes) >= 2:
                    score, text, words = cls.score_text_readability(p_bytes)
                    candidates.append({
                        "source": f"Synchronized Frame #{idx+1}",
                        "score": score + 25.0,  # Bonus for structured frame sync
                        "raw_bytes": p_bytes,
                        "clean_text": text.strip(),
                        "words": words,
                        "alignment": "Frame Sync"
                    })

        # 2. Check sync-word offsets directly (Barker-13: 1111100110101)
        barker13 = np.array([1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1], dtype=np.uint8)
        for polarity_name, bit_stream in [("Normal", bits), ("Inverted", 1 - bits)]:
            # Correlation search for Barker-13
            corr = np.correlate(bit_stream.astype(int) * 2 - 1, barker13.astype(int) * 2 - 1, mode="valid")
            peak_indices = np.where(corr >= 11)[0]
            for p_idx in peak_indices[:5]:
                # Payload starts after 13-bit sync word (and optional 3-bit padding to byte boundary)
                for sync_offset in [13, 16]:
                    start_pos = p_idx + sync_offset
                    if start_pos < len(bit_stream):
                        p_bits = bit_stream[start_pos:]
                        p_bytes = cls.bits_to_bytes(p_bits)
                        score, text, words = cls.score_text_readability(p_bytes)
                        candidates.append({
                            "source": f"Barker-13 Sync at bit {p_idx} ({polarity_name})",
                            "score": score + 20.0,
                            "raw_bytes": p_bytes,
                            "clean_text": text.strip(),
                            "words": words,
                            "alignment": f"Sync @ {p_idx}b | {polarity_name}"
                        })

        # 3. Multi-alignment bit-shift search across 8 bit offsets & 2 polarities
        for polarity_name, bit_stream in [("Normal", bits), ("Inverted", 1 - bits)]:
            for shift in range(8):
                if len(bit_stream) <= shift:
                    continue
                shifted_bits = bit_stream[shift:]
                byte_data = cls.bits_to_bytes(shifted_bits)
                score, text, words = cls.score_text_readability(byte_data)

                candidates.append({
                    "source": f"Bitstream Shift {shift} ({polarity_name})",
                    "score": score,
                    "raw_bytes": byte_data,
                    "clean_text": text.strip(),
                    "words": words,
                    "alignment": f"Shift {shift}b | {polarity_name}"
                })

        # Sort candidates by readability score descending
        candidates.sort(key=lambda c: c["score"], reverse=True)
        best = candidates[0] if candidates else None

        if not best:
            return {
                "has_message": False,
                "primary_message": "UNABLE TO DECODE TEXT",
                "clean_text_stream": "",
                "extracted_strings": [],
                "confidence_pct": 0.0,
                "best_alignment": "None",
                "telemetry_tags": {},
                "summary": "Demodulated bits could not be resolved to printable text."
            }

        # Clean up text stream
        raw_text = best["clean_text"]
        # Remove consecutive spaces and garbage runs
        cleaned_text = re.sub(r"\s+", " ", raw_text).strip()

        # Extract continuous human readable phrases
        meaningful_phrases = re.findall(r"[A-Za-z0-9][A-Za-z0-9\s.,:;!?/#_\-]{2,}[A-Za-z0-9]?", cleaned_text)
        
        # Filter for high quality phrases with recognized English words
        clean_phrases = []
        for p in meaningful_phrases:
            p_words = [w for w in re.findall(r"\b[A-Za-z0-9_-]+\b", p) if len(w) > 1 or w.lower() in ("i", "a")]
            eng_matches = sum(1 for w in p_words if w.lower() in COMMON_ENGLISH_WORDS)
            if eng_matches >= 1:
                # Strip leading/trailing non-alphanumeric punctuation
                p_clean = re.sub(r"^[^A-Za-z0-9]+", "", p).strip()
                tokens = p_clean.split()
                # Find last valid token
                last_valid_idx = len(tokens)
                for idx_t in range(len(tokens) - 1, -1, -1):
                    t_clean = re.sub(r"[^A-Za-z0-9]", "", tokens[idx_t])
                    if (len(t_clean) >= 1 and t_clean.lower() in ("i", "a")) or (len(t_clean) >= 2 and (t_clean.lower() in COMMON_ENGLISH_WORDS or t_clean.isupper() or any(c.isdigit() for c in t_clean))):
                        last_valid_idx = idx_t + 1
                        break
                trimmed = " ".join(tokens[:last_valid_idx])
                if trimmed and len(trimmed) >= 2:
                    single_unit = cls.extract_repeating_unit(trimmed)
                    clean_phrases.append(single_unit)

        # Extract Telemetry Key-Value tags (e.g. TARGET=..., COORD=..., MSG=..., LAT=..., LON=...)
        telemetry_tags = {}
        tag_matches = re.findall(r"([A-Za-z_]{2,15})\s*[:=]\s*([A-Za-z0-9_.\-]+)", cleaned_text)
        for k, v in tag_matches:
            k_clean = k.strip().upper()
            v_clean = v.strip()
            if len(k_clean) >= 2 and len(v_clean) >= 1:
                telemetry_tags[k_clean] = v_clean

        # Determine primary message string
        if clean_phrases:
            primary_msg = clean_phrases[0]
            confidence_pct = min(98.5, max(65.0, best["score"] * 2.2))
        elif meaningful_phrases:
            primary_msg = " // ".join(meaningful_phrases[:3])
            confidence_pct = min(85.0, max(30.0, best["score"] * 1.5))
        elif cleaned_text:
            primary_msg = cleaned_text[:200]
            confidence_pct = min(40.0, best["score"])
        else:
            primary_msg = "RAW BINARY STREAM (No plaintext ASCII header detected)"
            confidence_pct = 5.0

        # Build summary
        summary = (
            f"Decoded {len(best['words'])} words with {confidence_pct:.1f}% ASCII confidence "
            f"via {best['alignment']}."
        )

        return {
            "has_message": bool(confidence_pct > 25.0 and len(meaningful_phrases) > 0),
            "primary_message": primary_msg,
            "clean_text_stream": cleaned_text[:500],
            "extracted_strings": (clean_phrases if clean_phrases else meaningful_phrases)[:10],
            "confidence_pct": round(confidence_pct, 1),
            "best_alignment": best["alignment"],
            "telemetry_tags": telemetry_tags,
            "summary": summary,
            "total_words_found": len(best["words"])
        }
