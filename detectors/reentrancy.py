import json
def detect(ast):
    findings = []
    def contains_call(expr):
        """Recursively check if expression contains .call/.send/.transfer"""
        if not isinstance(expr, dict):
            return False

        # Case: MemberAccess like msg.sender.call
        if expr.get("nodeType") == "MemberAccess":
            if expr.get("memberName") in ["call", "send", "transfer"]:
                return True

        # Traverse deeper
        for key in expr:
            if contains_call(expr[key]):
                return True
        return False

    def analyze_function(function_node):
        statements = function_node.get("body", {}).get("statements", [])
        if not statements:
            return
        external_call_index = -1
        state_update_index = []

        for i, stmt in enumerate(statements):

            expr = None

            # Extract expression based on statement type
            if stmt.get("nodeType") == "ExpressionStatement":
                expr = stmt.get("expression", {})

            elif stmt.get("nodeType") == "VariableDeclarationStatement":
                expr = stmt.get("initialValue", {})

            # If no expression found → skip
            if not expr:
                continue

            # 🔥 Detect external call
            if contains_call(expr):
                if external_call_index == -1:
                    external_call_index = i
                    print("External call found at index", i)

            # 🔥 Detect state update (assignment)
            if expr.get("nodeType") == "Assignment":
                state_update_index.append(i)
                print("State update found at index", i)

        # 🚨 Vulnerability condition
        vulnerable = False
        for update_idx in state_update_index:
            # Flag if an external call exists BEFORE any state update [cite: 83, 101]
            if external_call_index != -1 and external_call_index < update_idx:
                vulnerable = True
                break
        if vulnerable:
            findings.append({
                "vulnerability": "Reentrancy",
                "detected": True,
                "description": "External call occurs before state update.",
                "prevention": "Update state before making external calls."
            })

    # Traverse AST to find functions
    def traverse(node):
        if isinstance(node, dict):

            if node.get("nodeType") == "FunctionDefinition":
                print("Function Found:", node.get("name"))
                analyze_function(node)


            for key in node:
                traverse(node[key])

        elif isinstance(node, list):
            for item in node:
                traverse(item)

    traverse(ast)

    if not findings:
        findings.append({
            "vulnerability": "Reentrancy",
            "detected": False,
            "message": "No risky pattern found."
        })

    return findings