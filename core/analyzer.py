from slither import Slither
from pathlib import Path
import json
from datetime import datetime

# Import all detectors
from detectors.reentrancy import detect_reentrancy


def run_full_analysis(contract_path: str):
    """Parse the contract ONCE and run all detectors"""
    try:
        print(f" Parsing contract: {contract_path}")
        slither = Slither(contract_path)          # ← Parsed only once!

        all_results = []

        # Run every detector and pass the same slither object
        all_results.extend(detect_reentrancy(slither))
        # Add new detectors here: all_results.extend(detect_xxx(slither))


        # Save nice report
        report = {
            "contract": Path(contract_path).name,
            "analyzed_at": datetime.now().isoformat(),
            "total_issues": len(all_results),
            "issues": all_results
        }

        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        output_file = report_dir / f"{Path(contract_path).stem}_report.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Done! {len(all_results)} findings saved to {output_file}")
        return report

    except Exception as e:
        print(f"❌ Error analyzing {contract_path}: {e}")
        return {"error": str(e)}