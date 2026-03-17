import json
from utils.ast_parser import get_ast
import os


# import detectors
from detectors import reentrancy
# later you add more

def analyze(source_code):
    ast = get_ast(source_code)
    results = []

    results.extend(reentrancy.detect(ast))

    return results
    ## To print AST
    # print("\n--- FUNCTION AST ---")
    # print(json.dumps(ast, indent=2))

    # Run each detector


if __name__ == "__main__":
    folder_path = "./test-contracts"
    
print("\n=== SMART CONTRACT ANALYSIS REPORT ===\n")

for filename in os.listdir(folder_path):
    if filename.endswith(".sol"):

        file_path = os.path.join(folder_path, filename)

        print(f"\n📄 Analyzing: {filename}")
        print("-----------------------------------")

        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        try:
            results = analyze(code)
        except Exception as e:
            print(f"❌ Compilation failed: {e}")
            print("------------------------")
            continue

        for res in results:
            print(f"Vulnerability: {res['vulnerability']}")

            if res.get("detected"):
                print("Status: ❌ Detected")
                print("Description:", res["description"])
                print("Prevention:", res["prevention"])
            else:
                print("Status: ✅ Safe")
                print(res["message"])

            print("\n------------------------")