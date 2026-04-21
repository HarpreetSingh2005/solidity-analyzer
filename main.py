# main.py
"""
SESA — Solidity Explainable Static Analyzer
CLI entry point.

Usage:
    python main.py <contract.sol>                 # Hybrid (Static + AI)
    python main.py <contract.sol> --no-ml         # Static only
    python main.py <contract.sol> --pdf           # Generate PDF report
    python main.py <contract.sol> --no-ml --pdf   # Static + PDF
"""

import argparse
import sys
from pathlib import Path

from core.analyzer import run_full_analysis


# ── Constants ─────────────────────────────────────────────────────────────────

SEVERITY_ORDER: dict[str, int] = {
    "Critical": 1,
    "High"    : 2,
    "Medium"  : 3,
    "Low"     : 4,
}

SEVERITY_LABEL: dict[str, str] = {
    "Critical": "CRITICAL",
    "High"    : "HIGH    ",
    "Medium"  : "MEDIUM  ",
    "Low"     : "LOW     ",
}

DIVIDER      = "=" * 72
THIN_DIVIDER = "-" * 72


# ── Banner ────────────────────────────────────────────────────────────────────

def print_banner() -> None:
    print(DIVIDER)
    print("        SESA — Solidity Explainable Static Analyzer")
    print("        Hybrid Static + AI Vulnerability Detector")
    print(DIVIDER)


# ── Report Display ────────────────────────────────────────────────────────────

def display_report(report: dict) -> None:
    """Pretty-print the analysis report to stdout."""

    if "error" in report:
        print(f"\n[ERROR] {report['error']}")
        return

    issues = report.get("issues", [])
    print(f"\n  Contract  : {report['contract']}")
    print(f"  Analyzed  : {report['analyzed_at']}")
    print(f"  Findings  : {len(issues)}")
    print(THIN_DIVIDER)

    if not issues:
        print("\n  No issues found — contract looks clean.")
        return

    # Sort by severity (Critical → High → Medium → Low), then by line number
    sorted_issues = sorted(
        issues,
        key=lambda x: (SEVERITY_ORDER.get(x.get("severity", "Low"), 5),
                       x.get("line", 0) if isinstance(x.get("line", 0), int) else 0),
    )

    for idx, issue in enumerate(sorted_issues, 1):
        sev      = issue.get("severity", "Unknown")
        sev_tag  = SEVERITY_LABEL.get(sev, sev.upper().ljust(8))
        vuln     = issue.get("vulnerability", "Unknown")
        contract = issue.get("contract", "?")
        func     = issue.get("function", "?")
        line     = issue.get("line", "?")
        expl     = issue.get("explanation", "")
        fix      = issue.get("suggested_fix", "")
        is_ml    = issue.get("is_ml_finding", False)
        source   = "AI-FLAG" if is_ml else "STATIC "

        # Location string — handle "(state variable)" gracefully
        if func and func != "(state variable)":
            location = f"{contract}.{func}() : L{line}"
        else:
            location = f"{contract} (state variable) : L{line}"

        print(f"\n  [{idx:>2}] [{sev_tag}] [{source}]  {vuln}")
        print(f"       Location : {location}")

        # Wrap explanation at ~65 chars for readability
        expl_lines = _wrap(expl, 65)
        print(f"       Reason   : {expl_lines[0]}")
        for extra in expl_lines[1:]:
            print(f"                  {extra}")

        fix_lines = _wrap(fix, 65)
        print(f"       Fix      : {fix_lines[0]}")
        for extra in fix_lines[1:]:
            print(f"                  {extra}")

        if is_ml and "confidence" in issue:
            print(f"       AI Conf  : {issue['confidence']:.1%}")

        print(f"  {THIN_DIVIDER}")


def _wrap(text: str, width: int) -> list[str]:
    """Naive word-wrap returning a list of lines."""
    if not text:
        return ["(none)"]
    words  = text.split()
    lines  : list[str] = []
    current: list[str] = []
    length = 0
    for word in words:
        if length + len(word) + 1 > width and current:
            lines.append(" ".join(current))
            current = [word]
            length  = len(word)
        else:
            current.append(word)
            length += len(word) + 1
    if current:
        lines.append(" ".join(current))
    return lines or ["(none)"]


# ── Argument Parsing ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sesa",
        description="SESA — Solidity Explainable Static Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py tests/Reentrancy.sol\n"
            "  python main.py tests/Reentrancy.sol --no-ml\n"
            "  python main.py tests/Reentrancy.sol --pdf\n"
        ),
    )
    parser.add_argument(
        "contract",
        nargs="?",
        default="tests/SelfDestruct.sol",
        help="Path to the Solidity contract (default: tests/SelfDestruct.sol)",
    )
    parser.add_argument(
        "--ml",
        action="store_true",
        default=True,
        help="Enable ML analysis (default: True)",
    )
    parser.add_argument(
        "--no-ml",
        action="store_false",
        dest="ml",
        help="Disable ML analysis (faster, static only)",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        default=False,
        help="Generate a PDF report after analysis",
    )
    return parser


# ── Entry Point ───────────────────────────────────────────────────────────────

def main() -> None:
    print_banner()

    parser = build_parser()
    args   = parser.parse_args()

    contract_path = args.contract
    if not Path(contract_path).exists():
        print(f"\n[ERROR] Contract file not found: '{contract_path}'")
        sys.exit(1)

    mode = "Hybrid (Static + AI)" if args.ml else "Static Only"
    print(f"\n  Mode      : {mode}")
    print(f"  Target    : {contract_path}\n")

    report = run_full_analysis(contract_path, run_ml=args.ml)
    display_report(report)

    print(f"\n  Full JSON report saved in 'reports/' directory.")

    # ── Optional PDF export ───────────────────────────────────────────────────
    if args.pdf and "error" not in report:
        try:
            from core.pdf_generator import generate_pdf
            pdf_path = generate_pdf(report)
            print(f"  PDF report  saved to '{pdf_path}'.")
        except ImportError:
            print("[WARN] pdf_generator not found — install fpdf2 to enable PDF export.")
        except Exception as exc:
            print(f"[WARN] PDF generation failed: {exc}")

    print(DIVIDER)


if __name__ == "__main__":
    main()