# main.py
import sys
from core.analyzer import run_full_analysis
from pathlib import Path

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

        for idx, issue in enumerate(sorted_issues, 1):
            severity_str = f"[{issue['severity'].upper()}]"
            print(f"{idx}. {severity_str} {issue['vulnerability']}")
            print(f"   Location: {issue['contract']} | {issue['function']}() | Line: {issue['line']}")
            print(f"   Explanation: {issue['explanation']}")
            print(f"   Suggested Fix: {issue['suggested_fix']}")
            print("-" * 60)

if __name__ == "__main__":
    print_banner()
    
    # Allow command line argument for contract path
    if len(sys.argv) > 1:
        contract_to_analyze = sys.argv[1]
    else:
        # Default test file if none provided
        contract_to_analyze = "tests/SelfDestruct.sol" 
        
    if not Path(contract_to_analyze).exists():
        print(f"\n[!] Error: Test file '{contract_to_analyze}' not found.")
        print("    Please provide a valid path or create the test folder.")
        sys.exit(1)

    report = run_full_analysis(contract_to_analyze)
    display_report(report)
    
    print("\n[+] Full JSON report saved in 'reports/' folder.")
    print("="*60)