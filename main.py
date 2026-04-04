from core.analyzer import run_full_analysis

if __name__ == "__main__":
    contract = "tests/contract_1.sol"          # change this to any .sol file
    report = run_full_analysis(contract)
    
    # Pretty print summary
    print("\n=== SUMMARY ===")
    for issue in report.get("issues", []):
        print(f" {issue['vulnerability']} in {issue['function']}() at line {issue['line']}")
        print(f"   → {issue['explanation']}")
        print(f"     Fix: {issue['suggested_fix']}\n")