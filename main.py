# main.py
import argparse
import sys
from pathlib import Path
from core.analyzer import run_full_analysis

def print_banner():
    print("="*72)
    print("        SESA — Solidity Explainable Static Analyzer")
    print("="*72)

def display_report(report):
    if "error" in report:
        print(f"\n[ERROR] {report['error']}")
        return

    issues = report.get("issues", [])
    print(f"\n[+] Analysis for: {report['contract']}")
    print(f"[+] Total Vulnerabilities: {len(issues)}\n" + "-"*72)

    if not issues:
        print("No critical issues found.")
        return

    sev_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
    sorted_issues = sorted(issues, key=lambda x: (sev_order.get(x.get('severity', 'Low'), 5), x.get('line', 0)))

    for idx, issue in enumerate(sorted_issues, 1):
        loc = f"{issue['contract']}.{issue['function']}() : L{issue['line']}"
        if issue['function'] == "(state variable)":
            loc = f"{issue['contract']} (state variable) : L{issue['line']}"
            
        print(f"[{idx}] [{issue.get('severity', 'UNKNOWN').upper()}] {issue['vulnerability']}")
        print(f"    Location : {loc}")
        print(f"    Reason   : {issue['explanation']}")
        print(f"    Fix      : {issue['suggested_fix']}\n" + "-"*72)

if __name__ == "__main__":
    print_banner()
    parser = argparse.ArgumentParser(description="SESA CLI — Solidity Explainable Static Analyzer")
    parser.add_argument("contract", help="Path to Solidity contract")
    parser.add_argument("--mode", choices=["static", "hybrid"], default="static", help="Analysis mode: 'static' (Slither only) or 'hybrid' (Static + ML)")
    args = parser.parse_args()

    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"[ERROR] File not found: {args.contract}")
        sys.exit(1)

    run_ml = (args.mode == "hybrid")
    report = run_full_analysis(args.contract, run_ml=run_ml)
    display_report(report)
