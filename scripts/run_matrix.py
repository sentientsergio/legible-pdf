#!/usr/bin/env python3
"""
Matrix orchestrator for legible-pdf Sprint 4b.

Runs the full (converter × corpus-item) conversion + evaluation matrix,
producing one markdown per (item, converter) and one honesty profile per
(item, converter). Resumable: skips work whose outputs already exist
unless --force is passed.

Layout produced:
    corpus/<item>/output/<converter>/output.md
    corpus/<item>/output/<converter>/honesty_profile.json

Usage:
    python scripts/run_matrix.py [--converters c1,c2,...] [--items i1,i2,...]
                                 [--phase convert|score|both] [--force]
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

CORPUS_ROOT = Path("corpus")
SCRIPTS = Path("scripts")

CONVERTERS = ["pymupdf4llm", "docling", "marker", "mineru"]


def discover_items() -> list[Path]:
    """Return a list of corpus item directories (each must have source.pdf and probes.json)."""
    items = []
    # Top-level wild items (LITM + Sprint-4b additions)
    for d in sorted(CORPUS_ROOT.iterdir()):
        if not d.is_dir() or d.name == "synthesized":
            continue
        if (d / "source.pdf").exists() and (d / "probes.json").exists():
            items.append(d)
        elif (d / "paper.pdf").exists() and (d / "probes.json").exists():
            # LITM uses paper.pdf
            items.append(d)
    # Synthesized items
    syn_root = CORPUS_ROOT / "synthesized"
    if syn_root.is_dir():
        for d in sorted(syn_root.iterdir()):
            if d.is_dir() and (d / "source.pdf").exists() and (d / "probes.json").exists():
                items.append(d)
    return items


def pdf_for(item_dir: Path) -> Path:
    """Some items use source.pdf, LITM uses paper.pdf."""
    for name in ("source.pdf", "paper.pdf"):
        p = item_dir / name
        if p.exists():
            return p
    raise FileNotFoundError(f"no source PDF in {item_dir}")


def output_md(item_dir: Path, converter: str) -> Path:
    return item_dir / "output" / converter / "output.md"


def output_profile(item_dir: Path, converter: str) -> Path:
    return item_dir / "output" / converter / "honesty_profile.json"


def run_convert(item_dir: Path, converter: str, force: bool) -> dict:
    md_path = output_md(item_dir, converter)
    if md_path.exists() and not force:
        return {"item": item_dir.name, "converter": converter, "status": "skipped", "elapsed": 0.0}
    pdf = pdf_for(item_dir)
    t0 = time.time()
    cmd = [
        ".venv/bin/python", str(SCRIPTS / "run_converter.py"),
        "--pdf", str(pdf),
        "--converter", converter,
        "--output", str(md_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    if result.returncode != 0:
        return {
            "item": item_dir.name, "converter": converter,
            "status": "failed", "elapsed": elapsed,
            "stderr": result.stderr[-500:],
        }
    return {"item": item_dir.name, "converter": converter, "status": "converted", "elapsed": elapsed}


def run_score(item_dir: Path, converter: str, force: bool) -> dict:
    md_path = output_md(item_dir, converter)
    profile_path = output_profile(item_dir, converter)
    if profile_path.exists() and not force:
        return {"item": item_dir.name, "converter": converter, "status": "skipped", "elapsed": 0.0}
    if not md_path.exists():
        return {
            "item": item_dir.name, "converter": converter,
            "status": "no-markdown", "elapsed": 0.0,
        }
    probes = item_dir / "probes.json"
    t0 = time.time()
    cmd = [
        ".venv/bin/python", str(SCRIPTS / "run-eval.py"),
        "--markdown", str(md_path),
        "--probes", str(probes),
        "--output", str(profile_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - t0
    if result.returncode != 0:
        return {
            "item": item_dir.name, "converter": converter,
            "status": "failed", "elapsed": elapsed,
            "stderr": result.stderr[-500:],
        }
    return {"item": item_dir.name, "converter": converter, "status": "scored", "elapsed": elapsed}


def main() -> int:
    ap = argparse.ArgumentParser(description="Sprint 4b matrix orchestrator")
    ap.add_argument("--converters", default=",".join(CONVERTERS),
                    help=f"Comma-separated converters (default: all = {','.join(CONVERTERS)})")
    ap.add_argument("--items", default=None,
                    help="Comma-separated item names to run (default: all discovered)")
    ap.add_argument("--phase", choices=("convert", "score", "both"), default="both",
                    help="Phase to run (default: both)")
    ap.add_argument("--force", action="store_true",
                    help="Re-run even if output exists")
    args = ap.parse_args()

    converters = args.converters.split(",")
    all_items = discover_items()
    if args.items:
        wanted = set(args.items.split(","))
        items = [d for d in all_items if d.name in wanted]
    else:
        items = all_items

    print(f"Matrix: {len(converters)} converters × {len(items)} items = {len(converters)*len(items)} cells")
    print(f"Converters: {converters}")
    print(f"Items: {[d.name for d in items]}")
    print()

    if args.phase in ("convert", "both"):
        print("=== CONVERT phase ===", flush=True)
        for converter in converters:
            for item in items:
                r = run_convert(item, converter, args.force)
                marker = {"converted": "✓", "skipped": "·", "failed": "✗"}.get(r["status"], "?")
                print(f"  {marker} {converter:12s} {item.name:35s} {r['status']:12s} {r['elapsed']:6.1f}s", flush=True)
                if r["status"] == "failed":
                    print(f"      stderr: {r.get('stderr', '')[:200]}", flush=True)
        print()

    if args.phase in ("score", "both"):
        print("=== SCORE phase ===", flush=True)
        for converter in converters:
            for item in items:
                r = run_score(item, converter, args.force)
                marker = {"scored": "✓", "skipped": "·", "failed": "✗", "no-markdown": "—"}.get(r["status"], "?")
                print(f"  {marker} {converter:12s} {item.name:35s} {r['status']:12s} {r['elapsed']:6.1f}s", flush=True)
                if r["status"] == "failed":
                    print(f"      stderr: {r.get('stderr', '')[:200]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
