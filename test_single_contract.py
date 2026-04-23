# test_single_contract.py
import sys
from pathlib import Path
import subprocess

def test_single_contract():
    if len(sys.argv) < 2:
        print("Usage:")
        print("   python test_single_contract.py <contract_path> [--mode hybrid]")
        print("\nExample:")
        print("   python test_single_contract.py tests/Reentrancy.sol --mode hybrid")
        sys.exit(1)

    contract_path = sys.argv[1]
    mode = "hybrid" if "--mode" in sys.argv else "static"

    print("=" * 80)
    print(f"Testing contract: {contract_path}")
    print(f"Mode            : {mode.upper()}")
    print("=" * 80)

    python_exe = sys.executable

    try:
        subprocess.run(
            [python_exe, "main.py", contract_path, "--mode", mode],
            check=True
        )
    except subprocess.CalledProcessError:
        print("Analysis completed with warnings/errors (see above).")
    except Exception as e:
        print(f"Error running analysis: {e}")

if __name__ == "__main__":
    test_single_contract()


##How to use it
# & C:/Users/Asus/AppData/Local/Microsoft/WindowsApps/python3.11.exe "f:/Minor Project/solidity-analyzer/test_single_contract.py" "dataset/business_logic/broken_rewards.sol" --mode hybrid