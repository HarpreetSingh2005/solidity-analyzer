# run_all_tests.py
import os
import subprocess
import json
import sys
from pathlib import Path
from core.pdf_generator import generate_full_pdf_report

def run_all_tests():
    test_dir = Path("tests")
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    python_exe = sys.executable
    print(f"Using Python: {python_exe}")
    print("="*85)
    print(f"{'CONTRACT':<35} | {'STATIC':<8} | {'ML':<6} | {'TOTAL':<6} | STATUS")
    print("-"*85)

    test_files = sorted(test_dir.glob("*.sol"))
    
    if not test_files:
        print("No test contracts found in tests/ folder.")
        return

    total_issues = 0

    for contract in test_files:
        try:
            report_path = reports_dir / f"{contract.stem}_report.json"
            
            # Run analysis in hybrid mode
            subprocess.run(
                [python_exe, "main.py", str(contract), "--mode", "hybrid"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Count issues
            issues_count = 0
            ml_issues = 0
            static_issues = 0

            if report_path.exists():
                with open(report_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        issues_count = data.get("total_issues", 0)
                        findings = data.get("issues", [])
                        ml_issues = sum(1 for f in findings if "ML" in str(f.get("vulnerability", "")))
                        static_issues = issues_count - ml_issues
                    except:
                        pass

            total_issues += issues_count
            status = "✅ DETECTED" if issues_count > 0 else "CLEAN"

            print(f"{contract.name:<35} | {static_issues:<8} | {ml_issues:<6} | {issues_count:<6} | {status}")

        except Exception as e:
            print(f"{contract.name:<35} | ERROR    | ERROR  | ERROR  | {str(e)[:25]}")

    print("="*85)
    print(f"Total Issues Found: {total_issues} across {len(test_files)} contracts")
    print("="*85)

    # Generate Consolidated PDF Report
    print("\n📄 Generating Consolidated PDF Report...")
    try:
        generate_full_pdf_report()
        print("✅ PDF Report generated successfully!")
    except Exception as e:
        print(f"PDF generation failed: {e}")

if __name__ == "__main__":
    run_all_tests()