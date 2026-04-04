from slither import Slither
from pathlib import Path

def explore_slither(contract_path: str):
    print(f"🔍 Loading contract: {contract_path}\n")
    
    slither = Slither(contract_path)

    print("="*90)
    print("1. CONTRACTS OVERVIEW")
    print("="*90)
    for contract in slither.contracts:
        print(f"Contract: {contract.name}")
        print(f"   State Variables : {[v.name for v in contract.state_variables]}")
        print(f"   Functions       : {len(contract.functions)}")
        print("-" * 70)

    print("\n" + "="*90)
    print("2. FUNCTIONS + CFG NODES + SOURCE MAPPING (Fixed Version)")
    print("="*90)

    for contract in slither.contracts:
        for function in contract.functions:
            func_type = "Constructor" if function.is_constructor else \
                       "Fallback" if function.is_fallback else \
                       function.visibility.upper()

            print(f"\n→ {func_type} Function: {function.name}()")
            print(f"   Modifiers          : {[m.name for m in function.modifiers]}")
            print(f"   State vars READ    : {[v.name for v in function.state_variables_read]}")
            print(f"   State vars WRITTEN : {[v.name for v in function.state_variables_written]}")
            print(f"   External calls     : {len(function.external_calls_as_expressions)}")
            print(f"   Number of CFG Nodes: {len(function.nodes)}")

            # Safe way to get line numbers (newer Slither)
            for i, node in enumerate(function.nodes[:7]):   # Show first 7 nodes
                src = node.source_mapping
                start_line = getattr(src, 'start_line', None) or getattr(src, 'lines', [None])[0] if src else "N/A"
                end_line   = getattr(src, 'end_line', None) or getattr(src, 'lines', [None])[-1] if src else "N/A"

                print(f"     [{i:2d}] Node Type: {str(node.type):<25} | Lines: {start_line}-{end_line}")

                if node.irs:
                    print(f"          SlithIR ({len(node.irs)} operations):")
                    for ir in node.irs[:3]:
                        print(f"            → {ir}")
                print("     " + "-"*75)

            if len(function.nodes) > 7:
                print(f"     ... and {len(function.nodes)-7} more nodes")

    print("\n" + "="*90)
    print("3. DETAILED SOURCE MAPPING EXAMPLE")
    print("="*90)
    example_found = False
    for contract in slither.contracts:
        for function in contract.functions:
            if function.nodes:
                node = function.nodes[0]
                src = node.source_mapping
                
                start_line = getattr(src, 'start_line', None)
                if start_line is None and hasattr(src, 'lines'):
                    start_line = src.lines[0] if src.lines else "N/A"
                
                print(f"Example from → {contract.name}.{function.name}()")
                print(f"   Node Type      : {node.type}")
                print(f"   Start Line     : {start_line}")
                print(f"   Code Snippet   :")
                print(f"     {str(node)[:280]}...")
                example_found = True
                break
        if example_found:
            break

    print("\n✅ Exploration completed successfully!")
    print("You now know how to safely access:")
    print("   • node.source_mapping")
    print("   • function.nodes")
    print("   • node.irs (SlithIR)")

# ====================== RUN ======================
if __name__ == "__main__":
    test_file = "test_contract.sol"   # Make sure this file exists in your folder
    
    if not Path(test_file).exists():
        print(f"❌ File '{test_file}' not found in current directory.")
        print("\nPlease create a file named 'test_contract.sol' with this content:\n")
        print("""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Test {
    uint public balance;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function withdraw() public {
        require(balance > 0);
        payable(msg.sender).transfer(balance);  // external call
        balance = 0;                            // state update after call
    }
}
""")
    else:
        explore_slither(test_file)