#!/usr/bin/env python3
"""
v0.0 smoke harness for legible-pdf.

For each probe in probes.json, send the converter's markdown output as context
to an LLM along with the probe question, capture the answer, compare to expected,
and write a structured honesty profile.

Usage:
    python scripts/run-eval.py --markdown <path> --probes <path> [--output <path>] [--model <name>]

Default model: claude-haiku-4-5-20251001 (fast, cheap, sufficient for yes/no probes).
"""

import argparse
import json
import sys
from pathlib import Path

from anthropic import Anthropic

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = (
    "You are answering yes/no questions about a document. "
    "Reply with only 'yes' or 'no' — a single word, lowercase. "
    "Do not provide explanation or hedge. "
    "Base your answer strictly on what the document text shows."
)


def ask_probe(client: Anthropic, model: str, markdown: str, question: str) -> str:
    """Send markdown + question to LLM, return normalized 'yes'|'no'|'ambiguous'."""
    user_prompt = (
        f"DOCUMENT:\n\n{markdown}\n\n"
        f"---\n\n"
        f"QUESTION: {question}\n\n"
        f"Reply only with 'yes' or 'no'."
    )
    resp = client.messages.create(
        model=model,
        max_tokens=8,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = resp.content[0].text.strip().lower().rstrip(".!,'\"")
    if raw.startswith("yes"):
        return "yes"
    if raw.startswith("no"):
        return "no"
    return f"ambiguous:{raw}"


def main() -> int:
    ap = argparse.ArgumentParser(description="legible-pdf v0.0 smoke harness")
    ap.add_argument("--markdown", required=True, help="Path to converter's markdown output")
    ap.add_argument("--probes", required=True, help="Path to probes.json")
    ap.add_argument("--output", default=None, help="Path for honesty profile (default: alongside markdown)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Anthropic model (default: {DEFAULT_MODEL})")
    args = ap.parse_args()

    markdown_path = Path(args.markdown)
    probes_path = Path(args.probes)
    if not markdown_path.exists():
        print(f"ERROR: markdown file not found: {markdown_path}", file=sys.stderr)
        return 2
    if not probes_path.exists():
        print(f"ERROR: probes file not found: {probes_path}", file=sys.stderr)
        return 2

    markdown = markdown_path.read_text()
    probes_data = json.loads(probes_path.read_text())
    probes = probes_data["probes"]

    client = Anthropic()  # uses ANTHROPIC_API_KEY env var

    print(f"Running {len(probes)} probes against {markdown_path.name} (model: {args.model})\n")
    print(f"  {'ID':<8} {'KIND':<14} {'FEATURE':<14} {'EXPECTED':<10} {'ACTUAL':<14} MATCH")
    print(f"  {'-' * 8} {'-' * 14} {'-' * 14} {'-' * 10} {'-' * 14} -----")

    results = []
    for probe in probes:
        actual = ask_probe(client, args.model, markdown, probe["question"])
        match = (actual == probe["expected_answer"])
        results.append({
            "id": probe["id"],
            "kind": probe["kind"],
            "feature": probe["feature"],
            "mode": probe["mode"],
            "question": probe["question"],
            "expected": probe["expected_answer"],
            "actual": actual,
            "match": match,
            "ground_truth_basis": probe.get("ground_truth_basis"),
        })
        mark = "OK " if match else "FAIL"
        print(f"  {probe['id']:<8} {probe['kind']:<14} {probe['feature']:<14} {probe['expected_answer']:<10} {actual:<14} {mark}")

    capture = [r for r in results if r["kind"] == "capture"]
    halc = [r for r in results if r["kind"] == "hallucination"]
    capture_rate = sum(r["match"] for r in capture) / len(capture) if capture else 0.0
    halc_rate = sum(r["match"] for r in halc) / len(halc) if halc else 0.0
    overall = sum(r["match"] for r in results) / len(results) if results else 0.0

    profile = {
        "corpus_item_id": probes_data.get("corpus_item_id"),
        "schema_version": probes_data.get("schema_version"),
        "markdown_path": str(markdown_path),
        "probes_path": str(probes_path),
        "model": args.model,
        "summary": {
            "total_probes": len(results),
            "matches": sum(r["match"] for r in results),
            "overall_rate": overall,
            "capture": {
                "n": len(capture),
                "matches": sum(r["match"] for r in capture),
                "rate": capture_rate,
            },
            "hallucination": {
                "n": len(halc),
                "matches": sum(r["match"] for r in halc),
                "rate": halc_rate,
            },
        },
        "probe_results": results,
    }

    output_path = Path(args.output) if args.output else markdown_path.parent / "honesty_profile.json"
    output_path.write_text(json.dumps(profile, indent=2))

    print(f"\nWrote {output_path}")
    print(f"\nHonesty profile:")
    print(f"  Capture:       {capture_rate:.1%} ({sum(r['match'] for r in capture)}/{len(capture)})")
    print(f"  Hallucination: {halc_rate:.1%} ({sum(r['match'] for r in halc)}/{len(halc)})")
    print(f"  Overall:       {overall:.1%} ({sum(r['match'] for r in results)}/{len(results)})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
