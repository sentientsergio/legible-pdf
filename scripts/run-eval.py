#!/usr/bin/env python3
"""
Honesty-profile harness for legible-pdf (v0.3 schema).

For each probe in probes.json, send the converter's markdown output as context
to an LLM along with the probe question, capture the answer N times, compute
unanimous-agreement, compare to expected, and write a structured honesty profile.

Usage:
    python scripts/run-eval.py --markdown <path> --probes <path>
                               [--output <path>] [--model <name>] [--runs N]

Default model: claude-haiku-4-5-20251001 (fast, cheap, sufficient for yes/no probes).
Default runs: 3 (Sprint 3 unanimous-agreement discipline).

v0.3 scoring (three probe classes reported independently):
- content      — honesty / LLM-reader-equivalence
- readability  — rule-based structural preservation (for humans previewing markdown)
- provenance   — rule-based positional coordinates (for LLM-analysts citing sources)

A probe scores as a match only if all N runs are unanimous AND the unanimous
answer matches expected. Disputed probes (runs disagree) are NOT counted toward
the rate but are reported separately as a probe-quality signal.

See docs/failure-mode-catalog.md v0.3 amendments for the taxonomy.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from anthropic import Anthropic

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_RUNS = 3

PROBE_CLASSES = ("content", "readability", "provenance")

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
        "probe_class": probe["probe_class"],
        "feature": probe.get("feature", ""),
        "rule": probe.get("rule", ""),
        "question": probe["question"],
        "expected": expected,
        "runs": answers,
        "agreement": agreement,
        "agreed_answer": agreed_answer,
        "match": match,
        "ground_truth_basis": probe.get("ground_truth_basis"),
    }


def score_class(results: list, cls: str) -> dict:
    """Compute per-class scoring summary."""
    group = [r for r in results if r["probe_class"] == cls]
    disputed = [r for r in group if r["agreement"] == "disputed"]
    matches = sum(r["match"] for r in group)
    rate = (matches / len(group)) if group else 0.0
    return {
        "n": len(group),
        "matches": matches,
        "rate": rate,
        "disputed": len(disputed),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="legible-pdf honesty-profile harness (v0.3 schema)")
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

    # Sanity-check schema version
    schema_version = probes_data.get("schema_version", "?")
    if schema_version != "0.3":
        print(f"WARNING: probes.json schema_version is {schema_version!r}, harness expects 0.3. "
              f"Run will proceed but may fail if probe shape has changed.", file=sys.stderr)

    # Validate every probe has a known probe_class
    for p in probes:
        pc = p.get("probe_class")
        if pc not in PROBE_CLASSES:
            print(f"ERROR: probe {p.get('id', '?')} has invalid probe_class: {pc!r}. "
                  f"Must be one of {PROBE_CLASSES}.", file=sys.stderr)
            return 2

    client = Anthropic()  # uses ANTHROPIC_API_KEY env var

    print(f"Running {len(probes)} probes against {markdown_path.name} "
          f"(model: {args.model}, runs/probe: {args.runs})\n")
    print(f"  {'ID':<10} {'CLASS':<12} {'FEATURE':<18} {'RULE':<18} {'EXPECTED':<8} {'AGREEMENT':<11} {'ANSWER':<10} MATCH")
    print(f"  {'-' * 10} {'-' * 12} {'-' * 18} {'-' * 18} {'-' * 8} {'-' * 11} {'-' * 10} -----")

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
        print(f"  {r['id']:<10} {r['probe_class']:<12} {r['feature']:<18} {r['rule']:<18} "
              f"{r['expected']:<8} {r['agreement']:<11} {answer_display:<10} {mark}")

    scores = {cls: score_class(results, cls) for cls in PROBE_CLASSES}
    all_disputed = [r["id"] for r in results if r["agreement"] == "disputed"]

    profile = {
        "corpus_item_id": probes_data.get("corpus_item_id"),
        "schema_version": schema_version,
        "markdown_path": str(markdown_path),
        "probes_path": str(probes_path),
        "model": args.model,
        "runs_per_probe": args.runs,
        "scoring_rule": (
            "Unanimous-agreement: a probe matches only if all runs agree AND the agreed "
            "answer matches expected. Three probe classes (content / readability / provenance) "
            "scored independently; no composite. See docs/failure-mode-catalog.md v0.3 amendments."
        ),
        "scores": scores,
        "disputed_probes": all_disputed,
        "probe_results": results,
    }

    output_path = Path(args.output) if args.output else markdown_path.parent / "honesty_profile.json"
    output_path.write_text(json.dumps(profile, indent=2))

    print(f"\nWrote {output_path}")
    print(f"\nHonesty profile:")
    for cls in PROBE_CLASSES:
        s = scores[cls]
        if s["n"] == 0:
            print(f"  {cls.capitalize():<12}: (no probes)")
            continue
        disputed_note = f"   [{s['disputed']} disputed]" if s["disputed"] else ""
        print(f"  {cls.capitalize():<12}: {s['rate']:.1%} ({s['matches']}/{s['n']}){disputed_note}")
    if all_disputed:
        print(f"\nDisputed probe IDs: {all_disputed}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
