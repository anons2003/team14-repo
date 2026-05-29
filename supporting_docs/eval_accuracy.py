"""
BudgetBot — Precision/Recall Calculator
========================================
Runs the AI classifier on labeled test transactions and produces:
  1. Per-category precision, recall, F1
  2. Overall accuracy
  3. Confusion matrix
  4. List of misclassified transactions

Usage:
    python supporting_docs/eval_accuracy.py [--backend local|bedrock]

Output saved to: supporting_docs/accuracy_report.txt
"""
import csv
import sys
import os
from collections import defaultdict
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.adapters.ai import LocalAI

# --------------- Config ---------------
TEST_SET = Path(__file__).resolve().parent / "test_transactions.csv"
OUTPUT   = Path(__file__).resolve().parent / "accuracy_report.txt"


def load_test_set(filepath: Path) -> list[dict]:
    with open(filepath, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def run_classifier(rows: list[dict], ai) -> list[dict]:
    results = []
    for row in rows:
        pred = ai.categorize(
            description=row["description"],
            amount=float(row["amount"]),
            date=row["date"],
        )
        results.append({
            **row,
            "predicted": pred["category"],
            "confidence": pred["confidence"],
            "correct": pred["category"] == row["human_label"],
        })
    return results


def calc_metrics(results: list[dict]) -> dict:
    all_cats = sorted(set(r["human_label"] for r in results) | set(r["predicted"] for r in results))
    metrics = {}

    for cat in all_cats:
        tp = sum(1 for r in results if r["predicted"] == cat and r["human_label"] == cat)
        fp = sum(1 for r in results if r["predicted"] == cat and r["human_label"] != cat)
        fn = sum(1 for r in results if r["predicted"] != cat and r["human_label"] == cat)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        metrics[cat] = {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}

    return metrics


def confusion_matrix(results: list[dict]) -> str:
    all_cats = sorted(set(r["human_label"] for r in results) | set(r["predicted"] for r in results))
    matrix = defaultdict(lambda: defaultdict(int))
    for r in results:
        matrix[r["human_label"]][r["predicted"]] += 1

    # Header
    max_len = max(len(c) for c in all_cats)
    header = f"{'Actual \\\\ Predicted':<{max_len+2}}" + "".join(f"{c:>{max_len+1}}" for c in all_cats)
    lines = [header, "-" * len(header)]

    for actual in all_cats:
        row = f"{actual:<{max_len+2}}"
        for pred in all_cats:
            count = matrix[actual][pred]
            cell = str(count) if count > 0 else "."
            row += f"{cell:>{max_len+1}}"
        lines.append(row)

    return "\n".join(lines)


def format_report(results: list[dict], metrics: dict) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("BUDGETBOT — AI ACCURACY REPORT")
    lines.append("=" * 72)
    lines.append(f"Test set: {len(results)} transactions")
    total_correct = sum(1 for r in results if r["correct"])
    lines.append(f"Overall accuracy: {total_correct}/{len(results)} = {total_correct/len(results):.1%}")
    lines.append("")

    # Per-category table
    lines.append(f"{'Category':<16} {'TP':>3} {'FP':>3} {'FN':>3} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    lines.append("-" * 72)
    for cat in sorted(metrics.keys()):
        m = metrics[cat]
        lines.append(
            f"{cat:<16} {m['tp']:>3} {m['fp']:>3} {m['fn']:>3} "
            f"{m['precision']:>10.3f} {m['recall']:>10.3f} {m['f1']:>10.3f}"
        )

    # Macro averages
    cats_with_data = [m for m in metrics.values() if m["tp"] + m["fn"] > 0]
    if cats_with_data:
        macro_p = sum(m["precision"] for m in cats_with_data) / len(cats_with_data)
        macro_r = sum(m["recall"] for m in cats_with_data) / len(cats_with_data)
        macro_f1 = sum(m["f1"] for m in cats_with_data) / len(cats_with_data)
        lines.append("-" * 72)
        lines.append(f"{'MACRO AVG':<16} {'':>3} {'':>3} {'':>3} {macro_p:>10.3f} {macro_r:>10.3f} {macro_f1:>10.3f}")

    lines.append("")
    lines.append("CONFUSION MATRIX")
    lines.append("-" * 72)
    lines.append(confusion_matrix(results))

    # Misclassifications
    errors = [r for r in results if not r["correct"]]
    lines.append("")
    lines.append(f"MISCLASSIFIED TRANSACTIONS ({len(errors)} errors)")
    lines.append("-" * 72)
    if errors:
        for r in errors:
            lines.append(
                f"  {r['description']:<35} "
                f"AI={r['predicted']:<15} Human={r['human_label']:<15} "
                f"conf={r['confidence']}"
            )
    else:
        lines.append("  (none — perfect accuracy!)")

    return "\n".join(lines)


def main():
    print(f"Loading test set: {TEST_SET}")
    rows = load_test_set(TEST_SET)
    print(f"  {len(rows)} transactions loaded")

    ai = LocalAI()
    print("Running LocalAI classifier...")
    results = run_classifier(rows, ai)

    metrics = calc_metrics(results)
    report = format_report(results, metrics)

    print()
    print(report)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"\nReport saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
