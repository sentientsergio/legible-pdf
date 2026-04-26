#!/usr/bin/env python3
"""
Single-converter PDF → markdown runner for legible-pdf Sprint 4b.

Each supported converter has its own implementation (Python API or subprocess),
producing a single output.md at the supplied path. Designed for matrix runs:
one PDF in, one markdown out, no MinerU-style multi-file artifacts.

Usage:
    python scripts/run_converter.py --pdf <path> --converter <name> --output <md_path>

Supported converters: pymupdf4llm, docling, marker, mineru
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


def run_pymupdf4llm(pdf_path: Path) -> str:
    import pymupdf4llm
    return pymupdf4llm.to_markdown(str(pdf_path))


def run_docling(pdf_path: Path) -> str:
    from docling.document_converter import DocumentConverter
    conv = DocumentConverter()
    result = conv.convert(str(pdf_path))
    return result.document.export_to_markdown()


def run_marker(pdf_path: Path) -> str:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    models = create_model_dict()
    mc = PdfConverter(artifact_dict=models)
    rendered = mc(str(pdf_path))
    md, _metadata, _images = text_from_rendered(rendered)
    return md


def run_mineru(pdf_path: Path, output_md: Path) -> None:
    """MinerU writes a multi-file output tree; we run its CLI then copy the
    resulting <stem>.md to the requested output path."""
    output_dir = output_md.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        ".venv/bin/mineru",
        "-p", str(pdf_path),
        "-o", str(output_dir),
        "-b", "pipeline",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"mineru failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}")
    # MinerU writes to <output_dir>/<stem>/auto/<stem>.md
    stem = pdf_path.stem
    produced = output_dir / stem / "auto" / f"{stem}.md"
    if not produced.exists():
        raise RuntimeError(f"mineru did not produce expected file: {produced}")
    shutil.copy2(produced, output_md)


CONVERTERS = {
    "pymupdf4llm": run_pymupdf4llm,
    "docling": run_docling,
    "marker": run_marker,
    "mineru": None,  # handled specially because of its multi-file output
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a single converter on a single PDF")
    ap.add_argument("--pdf", required=True, type=Path, help="Path to source PDF")
    ap.add_argument("--converter", required=True, choices=sorted(CONVERTERS), help="Converter name")
    ap.add_argument("--output", required=True, type=Path, help="Path to write markdown output (output.md)")
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"ERROR: PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    if args.converter == "mineru":
        run_mineru(args.pdf, args.output)
        elapsed = time.time() - t0
        size = args.output.stat().st_size
    else:
        runner = CONVERTERS[args.converter]
        md = runner(args.pdf)
        args.output.write_text(md)
        elapsed = time.time() - t0
        size = len(md)

    print(f"{args.converter}: {elapsed:.1f}s, {size} bytes -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
