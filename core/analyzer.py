# core/analyzer.py
from slither import Slither
from pathlib import Path
import json
from datetime import datetime

# Import all detectors
from detectors.reentrancy import detect_reentrancy
from detectors.access_control import detect_access_control
from detectors.tx_origin import detect_tx_origin_phishing
from detectors.self_destruct import detect_self_destruct
from detectors.unchecked_external_calls import detect_unchecked_external_calls
from detectors.shadowed_variable import detect_shadowed_variables

def run_full_analysis(contract_path: str):
    """
    Parses the contract ONCE using Slither and runs all security detectors.
    This architecture ensures maintainability and efficiency.
    """
    try:
        if not Path(contract_path).exists():
            return {"error": f"File not found: {contract_path}"}

        print(f"[SCAN] Parsing contract: {contract_path}")
        # Initialize Slither only once
        slither = Slither(contract_path, disable_color=True)

        all_results = []

        # Run Phase 1: Call each detector and pass the slither object
        print("[ANALYSIS] Running Vulnerability Detectors...")
        
        all_results.extend(detect_reentrancy(slither))
        all_results.extend(detect_access_control(slither))
        all_results.extend(detect_tx_origin_phishing(slither))
        all_results.extend(detect_self_destruct(slither))
        all_results.extend(detect_unchecked_external_calls(slither))
        all_results.extend(detect_shadowed_variables(slither))

        # Prepare the report
        report = {
            "contract": Path(contract_path).name,
            "analyzed_at": datetime.now().isoformat(),
            "total_issues": len(all_results),
            "issues": all_results
        }

        # Ensure reports directory exists
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        output_file = report_dir / f"{Path(contract_path).stem}_report.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        print(f"[SUCCESS] Analysis complete! {len(all_results)} findings saved to {output_file}")
        return report

    except Exception as e:
        print(f"[ERROR] Error analyzing {contract_path}: {e}")
        return {"error": str(e)}