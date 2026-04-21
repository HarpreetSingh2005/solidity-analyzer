# main.py
import sys
from core.analyzer import run_full_analysis
from pathlib import Path
import argparse

def print_banner():
    print("="*60)
    print("      SOLIDITY EXPLAINABLE STATIC ANALYZER (SESA)")
    print("="*60)

def display_report(report):
    if "error" in report:
        print(f"\n[!] Error: {report['error']}")
        return

    issues = report.get("issues", [])
    print(f"\n[+] Analysis for: {report['contract']}")
    print(f"[+] Total Vulnerabilities Found: {len(issues)}")
    print("-" * 60)

    if not issues:
        print("\n[!] No critical issues found! Your contract looks solid.")
    else:
        # Group by severity for better readability
        severity_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
        sorted_issues = sorted(issues, key=lambda x: severity_order.get(x['severity'], 5))

        print(f"{'#':<3} | {'SEVERITY':<10} | {'VULNERABILITY':<25} | {'LOCATION'}")
        print("-" * 80)

        for idx, issue in enumerate(sorted_issues, 1):
            sev = issue['severity'].upper()
            vuln = issue['vulnerability']
            loc = f"{issue['function']}() : L{issue['line']}"
            
            # Highlight AI findings
            prefix = "AI-RISK" if issue.get('is_ml_finding') else "STATIC"
            
            print(f"{idx:<3} | {sev:<10} | {prefix:<7} {vuln[:20]:<20} | {loc}")
            print(f"    Reasoning: {issue['explanation'][:100]}...")
            if issue.get('is_ml_finding') and 'confidence' in issue:
                print(f"    AI Confidence: {issue['confidence']:.2%}")
            print(f"    Fix: {issue['suggested_fix']}")
            print("-" * 80)

if __name__ == "__main__":
    print_banner()
    
    parser = argparse.ArgumentParser(description="Solidity Explainable Static Analyzer (SESA)")
    parser.add_argument("contract", nargs="?", default="tests/SelfDestruct.sol", help="Path to the Solidity contract")
    parser.add_argument("--ml", action="store_true", default=True, help="Enable ML analysis (default: True)")
    parser.add_argument("--no-ml", action="store_false", dest="ml", help="Disable ML analysis")
    
    args = parser.parse_args()
    contract_to_analyze = args.contract

    if not Path(contract_to_analyze).exists():
        print(f"\n[!] Error: Test file '{contract_to_analyze}' not found.")
        sys.exit(1)

    print(f"[MODE] Running {'Hybrid (Static + AI)' if args.ml else 'Static Only'} Analysis...")
    report = run_full_analysis(contract_to_analyze, run_ml=args.ml)
    display_report(report)
    
    print("\n[+] Full JSON report saved in 'reports/' folder.")
    print("="*60)