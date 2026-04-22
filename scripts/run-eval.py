#!/usr/bin/env python3
"""
Honesty-profile harness for legible-pdf.

For each probe in probes.json, send the converter's markdown output as context
to an LLM along with the probe question, capture the answer N times, compute
unanimous-agreement, compare to expected, and write a structured honesty profile.

Usage:
    python scripts/run-eval.py --markdown <path> --probes <path>
                               [--output <path>] [--model <name>] [--runs N]

Default model: claude-haiku-4-5-20251001 (fast, cheap, sufficient for yes/no probes).
Default runs: 3 (Sprint 3 unanimous-agreement discipline).

Sprint 3 scoring rule:
- A probe scores as a match only if all N runs are unanimous AND the unanimous
  answer matches expected.
- Disputed probes (runs disagree) are NOT counted toward the rate but are
  reported separately in the profile as a probe-quality signal.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from anthropic import Anthropic

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_RUNS = 3

SYSTEM_PROMPT = (
    "You are answering yes/no questions about a document. "
    "Reply with only 'yes' or 'no' — a single word, lowercase. "
    "Do not provide explanation or hedge. "
    "Base your answer strictly on what the document text shows."
)


def ask_probe(client: Anthropic, model: str, markdown: str, question: str) -> str:
    """Send markdown + question to LLM, return normalized 'yes'|'no'|'ambiguous:<raw>'."""
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


def evaluate_probe(client: Anthropic, model: str, markdown: str, probe: dict, runs: int) -> dict:
    """Run a probe N times, compute agreement, build result record."""
    answers = [ask_probe(client, model, markdown, probe["question"]) for _ in range(runs)]
    counts = Counter(answers)
    unanimous = len(counts) == 1
    agreed_answer = answers[0] if unanimous else None
    expected = probe["expected_answer"]

    if unanimous:
        match = (agreed_answer == expected)
        agreement = "unanimous"
    else:
        match = False  # disputed probes do not count as matches
        agreement = "disputed"

    return {
        "id": probe["id"],
        "kind": probe["kind"],
        "feature": probe["feature"],
        "mode": probe["mode"],
        "question": probe["question"],
        "expected": expected,
        "runs": answers,
        "agreement": agreement,
        "agreed_answer": agreed_answer,
        "match": match,
        "ground_truth_basis": probe.get("ground_truth_basis"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="legible-pdf honesty-profile harness")
    ap.add_argument("--markdown", required=True, help="Path to converter's markdown output")
    ap.add_argument("--probes", required=True, help="Path to probes.json")
    ap.add_argument("--output", default=None, help="Path for honesty profile (default: alongside markdown)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Anthropic model (default: {DEFAULT_MODEL})")
    ap.add_argument("--runs", type=int, default=DEFAULT_RUNS,
                    help=f"Runs per probe for unanimous-agreement scoring (default: {DEFAULT_RUNS})")
    args = ap.parse_args()

    markdown_path = Path(args.markdown)
    probes_path = Path(args.probes)
    if not markdown_path.exists():
        print(f"ERROR: markdown file not found: {markdown_path}", file=sys.stderr)
        return 2
    if not probes_path.exists():
        print(f"ERROR: probes file not found: {probes_path}", file=sys.stderr)
        return 2
    if args.runs < 1:
        print(f"ERROR: --runs must be >= 1 (got {args.runs})", file=sys.stderr)
        return 2

    markdown = markdown_path.read_text()
    probes_data = json.loads(probes_path.read_text())
    probes = probes_data["probes"]

    client = Anthropic()  # uses ANTHROPIC_API_KEY env var

    print(f"Running {len(probes)} probes against {markdown_path.name} "
          f"(model: {args.model}, runs/probe: {args.runs})\n")
    print(f"  {'ID':<8} {'KIND':<14} {'FEATURE':<18} {'EXPECTED':<10} {'AGREEMENT':<11} {'ANSWER':<10} MATCH")
    print(f"  {'-' * 8} {'-' * 14} {'-' * 18} {'-' * 10} {'-' * 11} {'-' * 10} -----")

    results = []
    for probe in probes:
        r = evaluate_probe(client, args.model, markdown, probe, args.runs)
        results.append(r)
        if r["agreement"] == "unanimous":
            mark = "OK " if r["match"] else "FAIL"
            answer_display = r["agreed_answer"]
        else:
            mark = "DSPT"
            answer_display = "/".join(r["runs"])
        print(f"  {r['id']:<8} {r['kind']:<14} {r['feature']:<18} {r['expected']:<10} "
              f"{r['agreement']:<11} {answer_display:<10} {mark}")

    capture = [r for r in results if r["kind"] == "capture"]
    halc = [r for r in results if r["kind"] == "hallucination"]
    disputed = [r for r in results if r["agreement"] == "disputed"]

    def rate(group):
        if not group:
            return 0.0
        return sum(r["match"] for r in group) / len(group)

    capture_rate = rate(capture)
    halc_rate = rate(halc)
    overall = rate(results)

    profile = {
        "corpus_item_id": probes_data.get("corpus_item_id"),
        "schema_version": probes_data.get("schema_version"),
        "markdown_path": str(markdown_path),
        "probes_path": str(probes_path),
        "model": args.model,
        "runs_per_probe": args.runs,
        "scoring_rule": "Unanimous-agreement: a probe matches only if all runs agree AND the agreed answer matches expected. Disputed probes (runs disagree) are not counted as matches and are reported as a probe-quality signal.",
        "summary": {
            "total_probes": len(results),
            "matches": sum(r["match"] for r in results),
            "disputed": len(disputed),
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
        "disputed_probes": [r["id"] for r in disputed],
        "probe_results": results,
    }

    output_path = Path(args.output) if args.output else markdown_path.parent / "honesty_profile.json"
    output_path.write_text(json.dumps(profile, indent=2))

    print(f"\nWrote {output_path}")
    print(f"\nHonesty profile:")
    print(f"  Capture:       {capture_rate:.1%} ({sum(r['match'] for r in capture)}/{len(capture)})")
    print(f"  Hallucination: {halc_rate:.1%} ({sum(r['match'] for r in halc)}/{len(halc)})")
    print(f"  Overall:       {overall:.1%} ({sum(r['match'] for r in results)}/{len(results)})")
    if disputed:
        print(f"  Disputed:      {len(disputed)} probe(s) — runs disagreed: {[r['id'] for r in disputed]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
