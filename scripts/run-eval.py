#!/usr/bin/env python3
"""
Honesty-profile harness for legible-pdf (v0.3.1 schema — hybrid mechanical + LLM).

For each probe in probes.json, determine whether the probe's rule has a
mechanical check available (see scripts/rules.py):

  - If mechanical and the check returns yes/no: that IS the answer
    (deterministic, no N=3 variance, answered_by="mechanical").
  - If mechanical and the check returns "undetermined": escalate to the
    LLM judge (N=3 unanimous-agreement, answered_by="llm").
  - If no mechanical check for this rule: run the LLM judge path as before.

The guiding principle (from feedback_deterministic_knows_its_limits):
mechanical checks must know their scope of competence and refuse to answer
outside it. A mechanical check that returns yes/no on ambiguous input is
worse than slower LLM inference because the failure is silent.

v0.3.1 scoring (three probe classes reported independently):
- content      — honesty / LLM-reader-equivalence (all LLM-judged)
- readability  — rule-based structural preservation (mechanical where
                 markdown syntax is unambiguous, LLM fallback for edges)
- provenance   — rule-based positional coordinates (mechanical for
                 presence on page-marker/section-number, LLM for everything
                 else including all accuracy probes)

Usage:
    python scripts/run-eval.py --markdown <path> --probes <path>
                               [--output <path>] [--model <name>] [--runs N]

See docs/failure-mode-catalog.md v0.3 + v0.3.1 amendments for the taxonomy.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from anthropic import Anthropic

from rules import has_mechanical_check, run_mechanical_check

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


def evaluate_llm(client: Anthropic, model: str, markdown: str, probe: dict, runs: int) -> dict:
    """Run a probe through the LLM judge N times, compute agreement."""
    answers = [ask_probe(client, model, markdown, probe["question"]) for _ in range(runs)]
    counts = Counter(answers)
    unanimous = len(counts) == 1
    agreed_answer = answers[0] if unanimous else None
    expected = probe["expected_answer"]

    if unanimous:
        match = (agreed_answer == expected)
        agreement = "unanimous"
    else:
        match = False
        agreement = "disputed"

    return {
        "answered_by": "llm",
        "runs": answers,
        "agreement": agreement,
        "agreed_answer": agreed_answer,
        "match": match,
    }


def evaluate_mechanical(markdown: str, probe: dict) -> dict | None:
    """Run the mechanical rule check if applicable. Returns None if not applicable
    or if the check returned 'undetermined' (caller should fall back to LLM)."""
    rule = probe.get("rule")
    if not rule or not has_mechanical_check(rule):
        return None

    check = run_mechanical_check(rule, markdown)
    result = check["result"]
    if result == "undetermined":
        return None  # signal caller to escalate

    expected = probe["expected_answer"]
    return {
        "answered_by": "mechanical",
        "runs": [result],
        "agreement": "mechanical",
        "agreed_answer": result,
        "match": (result == expected),
        "mechanical_details": check["details"],
    }


def evaluate_probe(client: Anthropic, model: str, markdown: str, probe: dict, runs: int) -> dict:
    """Dispatch probe evaluation: mechanical first, LLM fallback for undetermined."""
    mech = evaluate_mechanical(markdown, probe)
    if mech is not None:
        result = mech
    else:
        # Not mechanical or mechanical returned undetermined — use LLM
        result = evaluate_llm(client, model, markdown, probe, runs)
        rule = probe.get("rule")
        if rule and has_mechanical_check(rule):
            check = run_mechanical_check(rule, markdown)
            result["mechanical_details"] = f"mechanical={check['result']}: {check['details']}"

    return {
        "id": probe["id"],
        "probe_class": probe["probe_class"],
        "feature": probe.get("feature", ""),
        "rule": probe.get("rule", ""),
        "question": probe["question"],
        "expected": probe["expected_answer"],
        "ground_truth_basis": probe.get("ground_truth_basis"),
        **result,
    }


def score_class(results: list, cls: str) -> dict:
    """Compute per-class scoring summary."""
    group = [r for r in results if r["probe_class"] == cls]
    disputed = [r for r in group if r["agreement"] == "disputed"]
    mech = [r for r in group if r["answered_by"] == "mechanical"]
    matches = sum(r["match"] for r in group)
    rate = (matches / len(group)) if group else 0.0
    return {
        "n": len(group),
        "matches": matches,
        "rate": rate,
        "disputed": len(disputed),
        "mechanical_answered": len(mech),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="legible-pdf honesty-profile harness (v0.3.1)")
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

    schema_version = probes_data.get("schema_version", "?")
    if schema_version not in ("0.3", "0.3.1"):
        print(f"WARNING: probes.json schema_version is {schema_version!r}; harness expects 0.3 or 0.3.1.",
              file=sys.stderr)

    for p in probes:
        pc = p.get("probe_class")
        if pc not in PROBE_CLASSES:
            print(f"ERROR: probe {p.get('id', '?')} has invalid probe_class: {pc!r}. "
                  f"Must be one of {PROBE_CLASSES}.", file=sys.stderr)
            return 2

    client = Anthropic()

    print(f"Running {len(probes)} probes against {markdown_path.name} "
          f"(model: {args.model}, runs/probe: {args.runs})\n")
    print(f"  {'ID':<10} {'CLASS':<12} {'RULE':<18} {'BY':<11} {'EXPECTED':<8} {'ANSWER':<10} MATCH")
    print(f"  {'-' * 10} {'-' * 12} {'-' * 18} {'-' * 11} {'-' * 8} {'-' * 10} -----")

    results = []
    for probe in probes:
        r = evaluate_probe(client, args.model, markdown, probe, args.runs)
        results.append(r)
        if r["agreement"] == "mechanical":
            mark = "OK " if r["match"] else "FAIL"
            answer_display = r["agreed_answer"]
            by = "mech"
        elif r["agreement"] == "unanimous":
            mark = "OK " if r["match"] else "FAIL"
            answer_display = r["agreed_answer"]
            by = "llm (unan)"
        else:
            mark = "DSPT"
            answer_display = "/".join(r["runs"])
            by = "llm (dspt)"
        print(f"  {r['id']:<10} {r['probe_class']:<12} {r['rule']:<18} {by:<11} "
              f"{r['expected']:<8} {answer_display:<10} {mark}")

    scores = {cls: score_class(results, cls) for cls in PROBE_CLASSES}
    all_disputed = [r["id"] for r in results if r["agreement"] == "disputed"]
    total_mechanical = sum(1 for r in results if r["answered_by"] == "mechanical")

    profile = {
        "corpus_item_id": probes_data.get("corpus_item_id"),
        "schema_version": schema_version,
        "markdown_path": str(markdown_path),
        "probes_path": str(probes_path),
        "model": args.model,
        "runs_per_probe": args.runs,
        "scoring_rule": (
            "Hybrid mechanical + LLM. Mechanical rule checks (scripts/rules.py) answer probes "
            "where markdown syntax is unambiguous; LLM N=3 unanimous-agreement answers the rest, "
            "including mechanical-returned-undetermined cases. See docs/failure-mode-catalog.md "
            "v0.3 + v0.3.1 amendments for the taxonomy."
        ),
        "scores": scores,
        "mechanical_answered": total_mechanical,
        "llm_answered": len(results) - total_mechanical,
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
        extras = []
        if s["mechanical_answered"]:
            extras.append(f"{s['mechanical_answered']} mechanical")
        if s["disputed"]:
            extras.append(f"{s['disputed']} disputed")
        note = f"   [{', '.join(extras)}]" if extras else ""
        print(f"  {cls.capitalize():<12}: {s['rate']:.1%} ({s['matches']}/{s['n']}){note}")
    print(f"\n  Answered by: {total_mechanical} mechanical / {len(results) - total_mechanical} LLM")
    if all_disputed:
        print(f"  Disputed probe IDs: {all_disputed}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
