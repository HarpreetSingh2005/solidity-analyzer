# run_all_tests.py
import os
import subprocess
from pathlib import Path
from core.pdf_generator import generate_full_pdf_report

def run_tests():
    test_dir = Path("tests")
    import sys
    python_exe = sys.executable

    print(f"Using Python: {python_exe}")
    print("="*60)
    print(f"{'CONTRACT':<30} | {'ISSUES':<10} | {'STATUS'}")
    print("-" * 60)

    test_files = list(test_dir.glob("*.sol"))
    if not test_files:
        print("No test contracts found in tests/ folder.")
        return

    for contract in test_files:
        try:
            # Clear previous report if it exists
            report_file = Path("reports") / f"{contract.stem}_report.json"
            if report_file.exists():
                os.remove(report_file)

            # Run main.py as a subprocess
            subprocess.run(
                [python_exe, "main.py", str(contract)],
                capture_output=True,
                text=True,
                errors='replace'
            )
            
            # Read the findings from the JSON report
            issues_count = "0"
            if report_file.exists():
                import json
                with open(report_file, "r") as f:
                    report_data = json.load(f)
                    issues_count = str(report_data.get("total_issues", 0))
            
            status = "PASS" if int(issues_count) > 0 else "ZERO FINDINGS"
            print(f"{contract.name:<30} | {issues_count:<10} | {status}")
            
        except Exception as e:
            print(f"{contract.name:<30} | ERROR      | {str(e)[:20]}...")

    print("="*60)
    print("Test run complete. Check 'reports/' for detailed JSON results.")
    
    # Generate consolidated PDF report
    print("\nGenerating Consolidated PDF Report...")
    generate_full_pdf_report()

if __name__ == "__main__":
    run_tests()
