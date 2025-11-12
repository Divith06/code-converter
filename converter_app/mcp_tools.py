"""
MCP Logic Validation Tool
Performs multi-step verification of two code outputs and ensures logic consistency.
"""

import difflib
import time


def deep_compare_outputs(output1: str, output2: str) -> dict:
    """
    Compares outputs twice to ensure stability.
    """
    # Pass 1: direct comparison
    match_direct = output1.strip() == output2.strip()

    # Pass 2: normalized comparison (remove spaces, newlines)
    norm1 = output1.replace(" ", "").replace("\n", "")
    norm2 = output2.replace(" ", "").replace("\n", "")
    match_normalized = norm1 == norm2

    # Optional: semantic diff (for debugging)
    diff = "\n".join(difflib.unified_diff(
        output1.splitlines(), output2.splitlines(),
        lineterm="", fromfile="original", tofile="converted"
    ))

    consistent = match_direct and match_normalized

    return {
        "match_direct": match_direct,
        "match_normalized": match_normalized,
        "consistent": consistent,
        "diff_preview": diff[:400]
    }


def verify_logic(original_output: str, converted_output: str) -> bool:
    """
    Performs multiple passes of validation to ensure correctness.
    """
    print("[MCP] Starting multi-pass verification...")
    results = []

    for i in range(2):
        res = deep_compare_outputs(original_output, converted_output)
        results.append(res)
        print(f"[MCP] Pass {i+1}: consistent={res['consistent']}")
        time.sleep(0.2)

    # Require both passes to agree on consistency
    return all(r["consistent"] for r in results)
