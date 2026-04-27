#!/usr/bin/env python3
"""
Aggregate the 4 × 12 matrix of honesty profiles into per-converter
three-track profiles + per-item × per-converter cell tables.

Usage:
    python scripts/aggregate_matrix.py [--output <path>]
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict

CORPUS_ROOT = Path("corpus")
CONVERTERS = ["mineru", "docling", "marker", "pymupdf4llm"]
CLASSES = ["content", "readability", "provenance"]


def discover_items() -> list[Path]:
    items = []
    for d in sorted(CORPUS_ROOT.iterdir()):
        if not d.is_dir() or d.name == "synthesized":
            continue
        if (d / "probes.json").exists():
            items.append(d)
    syn = CORPUS_ROOT / "synthesized"
    if syn.is_dir():
        for d in sorted(syn.iterdir()):
            if d.is_dir() and (d / "probes.json").exists():
                items.append(d)
    return items


def load_profile(item: Path, converter: str) -> dict | None:
    p = item / "output" / converter / "honesty_profile.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate Sprint 4b matrix profiles")
    ap.add_argument("--output", default="docs/sprint-4-aggregated.json", type=Path)
    args = ap.parse_args()

    items = discover_items()
    matrix = {}  # matrix[item_name][converter] = profile.scores
    for item in items:
        matrix[item.name] = {}
        for cv in CONVERTERS:
            prof = load_profile(item, cv)
            if prof is None:
                matrix[item.name][cv] = None
            else:
                matrix[item.name][cv] = {
                    "scores": prof.get("scores", {}),
                    "mechanical_answered": prof.get("mechanical_answered", 0),
                    "llm_answered": prof.get("llm_answered", 0),
                    "disputed": prof.get("disputed_probes", []),
                }

    # Per-converter aggregates: unweighted mean of per-item rates per class
    aggregate = {}
    for cv in CONVERTERS:
        per_class = {}
        for cls in CLASSES:
            rates = []
            n_total, m_total, mech_total, disp_total = 0, 0, 0, 0
            for item_name, by_cv in matrix.items():
                cell = by_cv.get(cv)
                if cell is None:
                    continue
                cls_scores = cell["scores"].get(cls, {})
                n = cls_scores.get("n", 0)
                if n == 0:
                    continue
                rate = cls_scores.get("rate", 0.0)
                rates.append(rate)
                n_total += n
                m_total += cls_scores.get("matches", 0)
                mech_total += cls_scores.get("mechanical_answered", 0)
                disp_total += cls_scores.get("disputed", 0)
            unweighted = sum(rates) / len(rates) if rates else 0.0
            weighted = (m_total / n_total) if n_total else 0.0
            per_class[cls] = {
                "items_with_class": len(rates),
                "n_total": n_total,
                "matches_total": m_total,
                "rate_unweighted_mean": unweighted,
                "rate_weighted": weighted,
                "mechanical_answered_total": mech_total,
                "disputed_total": disp_total,
            }
        aggregate[cv] = per_class

    out = {
        "matrix": matrix,
        "aggregate": aggregate,
        "items": [d.name for d in items],
        "converters": CONVERTERS,
    }
    args.output.write_text(json.dumps(out, indent=2))
    print(f"wrote {args.output}")

    # Pretty-print summary
    print("\n=== Per-converter aggregate (unweighted mean of per-item rates) ===")
    print(f"{'converter':14s} {'content':>16s} {'readability':>16s} {'provenance':>16s}")
    for cv in CONVERTERS:
        cells = aggregate[cv]
        cell_strs = []
        for cls in CLASSES:
            c = cells[cls]
            r = c["rate_unweighted_mean"]
            n = c["n_total"]
            m = c["matches_total"]
            cell_strs.append(f"{m:3d}/{n:3d} ({r:>5.0%})")
        print(f"{cv:14s} {cell_strs[0]:>16s} {cell_strs[1]:>16s} {cell_strs[2]:>16s}")

    print("\n=== Per-item × per-converter (matches/n, rate) by class ===")
    for cls in CLASSES:
        print(f"\n--- {cls.upper()} ---")
        header = f"{'item':35s} " + " ".join(f"{cv:>14s}" for cv in CONVERTERS)
        print(header)
        for item_name in matrix:
            row = f"{item_name:35s} "
            for cv in CONVERTERS:
                cell = matrix[item_name][cv]
                if cell is None:
                    row += f"{'—':>14s} "
                    continue
                cls_scores = cell["scores"].get(cls, {})
                n = cls_scores.get("n", 0)
                if n == 0:
                    row += f"{'—':>14s} "
                else:
                    r = cls_scores.get("rate", 0.0)
                    m = cls_scores.get("matches", 0)
                    row += f"  {m:2d}/{n:<2d} ({r:>4.0%})"
            print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
