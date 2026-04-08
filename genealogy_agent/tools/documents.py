from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(slots=True)
class ExtractedDocumentText:
    document_id: str
    text: str
    language: str
    confidence: float


class HandwrittenPdfReader(Protocol):
    def extract_text(self, pdf_bytes: bytes, language_hint: str | None = None) -> ExtractedDocumentText:
        ...


class ConfigurablePdfReader:
    """Pluggable PDF reader wrapper for custom OCR/HTR providers."""

    def __init__(self, extractor) -> None:
        self.extractor = extractor

    def extract_text(self, pdf_bytes: bytes, language_hint: str | None = None) -> ExtractedDocumentText:
        text, language, confidence = self.extractor(pdf_bytes, language_hint)
        return ExtractedDocumentText(
            document_id="pdf:in-memory",
            text=text,
            language=language,
            confidence=confidence,
        )


class KrakenPdfReader:
    """Built-in open-source handwritten OCR/HTR using Kraken CLI.

    Requirements:
    - `kraken` executable available in PATH (install via `pip install kraken`).
    - A Kraken model path for the target language/script.
    """

    def __init__(self, model_path: str, language: str = "und") -> None:
        self.model_path = model_path
        self.language = language

    def extract_text(self, pdf_bytes: bytes, language_hint: str | None = None) -> ExtractedDocumentText:
        kraken_bin = shutil.which("kraken")
        if not kraken_bin:
            raise RuntimeError("Kraken is not installed. Install with: pip install kraken")

        with tempfile.TemporaryDirectory(prefix="genealogy_ocr_") as tmp:
            tmp_path = Path(tmp)
            input_pdf = tmp_path / "input.pdf"
            output_txt = tmp_path / "output.txt"
            input_pdf.write_bytes(pdf_bytes)

            # Kraken accepts image/PDF and writes OCR text to output file.
            cmd = [
                kraken_bin,
                "-i",
                str(input_pdf),
                str(output_txt),
                "binarize",
                "segment",
                "ocr",
                "-m",
                self.model_path,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                raise RuntimeError(f"Kraken OCR failed: {proc.stderr.strip()}")

            text = output_txt.read_text(encoding="utf-8", errors="ignore")

        return ExtractedDocumentText(
            document_id="pdf:kraken",
            text=text,
            language=language_hint or self.language,
            confidence=0.75,
        )
