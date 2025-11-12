# ~/code-converter/backend/converter_app/mcp_connector.py
import os
import json
import time
import re
from groq import Groq

# Optional mock testing mode
MOCK_MCP = os.getenv("MOCK_MCP", "0") == "1"

# Groq client setup
GROQ_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

# Choose your default Groq model
# (Recommended: llama-3.1-70b or mixtral-8x7b)
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def _call_llm_system(messages, timeout=30):
    """Call Groq chat model or return mock output."""
    if MOCK_MCP or not GROQ_KEY:
        time.sleep(0.2)
        return {"mock": True, "text": "MOCK: LLM placeholder"}

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.0,
            max_tokens=1024,
        )
        return {"mock": False, "text": response.choices[0].message.content.strip()}
    except Exception as e:
        return {"mock": True, "text": f"// Groq API error: {e}"}


def convert_with_mcp(source_code: str, source_lang: str, target_lang: str):
    """Convert source code between languages using Groq LLM."""
    if MOCK_MCP:
        return {
            "converted_code": f"// Mock: {source_lang} -> {target_lang} conversion",
            "confidence": 0.7,
            "notes": "mock conversion"
        }

    messages = [
        {"role": "system", "content": (
            "You are a professional code translator. "
            "Convert the user's code from one language to another "
            "preserving logic, structure, and variable names. "
            "Return only the converted code."
        )},
        {"role": "user", "content": (
            f"Convert this {source_lang} code into {target_lang}. "
            f"Ensure logical equivalence and runnable syntax.\n\n"
            f"```{source_lang}\n{source_code}\n```"
        )}
    ]

    out = _call_llm_system(messages)
    text = out["text"]

    cleaned = re.sub(r"^```[a-zA-Z]*\n", "", text.strip())   # remove ```go or ```python at start
    cleaned = re.sub(r"```$", "", cleaned).strip()            # remove ending ```
    
    return {"converted_code": cleaned, "confidence": None, "notes": "converted via Groq/OpenAI"}


def validate_logic_with_mcp(original_code, converted_code, original_lang, converted_lang):
    """Validate if original and converted code are logically equivalent."""
    if MOCK_MCP:
        ok = "print" in original_code or "println" in converted_code
        return {
            "logic_consistent": bool(ok),
            "original_output": "mock output",
            "converted_output": "mock output",
            "notes": "mock validation"
        }

    messages = [
        {"role": "system", "content": (
            "You are a strict code comparison AI. "
            "Analyze two code snippets and check if they perform the same logic."
        )},
        {"role": "user", "content": (
            f"Compare the following two snippets and return a JSON response with keys: "
            f"logic_consistent (true/false), notes.\n\n"
            f"Original ({original_lang}):\n```{original_lang}\n{original_code}\n```\n\n"
            f"Converted ({converted_lang}):\n```{converted_lang}\n{converted_code}\n```"
        )}
    ]

    out = _call_llm_system(messages)
    text = out["text"]

    try:
        parsed = json.loads(text)
        return parsed
    except Exception:
        return {
            "logic_consistent": "true" in text.lower(),
            "original_output": "execution simulated",
            "converted_output": "execution simulated",
            "notes": text[:512],
        }


def refine_with_feedback(converted_code: str, feedback: str, source_lang: str, target_lang: str):
    """Refine converted code based on user feedback."""
    if MOCK_MCP:
        return {"converted_code": converted_code + "\n// Refined (mock feedback)", "notes": "mock refine"}

    messages = [
        {"role": "system", "content": "You are a precise code editor that refines code based on user feedback."},
        {"role": "user", "content": (
            f"Here is the {target_lang} code that needs refining based on feedback.\n\n"
            f"```{target_lang}\n{converted_code}\n```\n\n"
            f"User feedback:\n{feedback}\n\n"
            "Return the full corrected code."
        )}
    ]

    out = _call_llm_system(messages)
    return {"converted_code": out["text"].strip(), "notes": "refined via Groq LLM"}
