# backend/converter_app/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .mcp_connector import convert_with_mcp  # your MCP integration (mock mode supported)
from .utils import run_code

@csrf_exempt
def convert_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    source_code = payload.get("source_code", "")
    source_lang = payload.get("source_lang", "")
    target_lang = payload.get("target_lang", "")

    if not source_code or not source_lang or not target_lang:
        return JsonResponse({"error": "Missing fields"}, status=400)

    # call your MCP connector; it should return dict with 'converted_code'
    mcp_res = convert_with_mcp(source_code, source_lang, target_lang)
    if not mcp_res or mcp_res.get("status") == "error":
        return JsonResponse({"error": mcp_res.get("message", "MCP error")}, status=500)

    return JsonResponse({
        "converted_code": mcp_res.get("converted_code", ""),
        "notes": mcp_res.get("notes", "")
    })


@csrf_exempt
def run_source_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    source_code = data.get("source_code", "")
    source_lang = data.get("source_lang", "")
    stdin = data.get("stdin", "")

    if not source_code or not source_lang:
        return JsonResponse({"error": "Missing code or language"}, status=400)

    out = run_code(source_lang, source_code, stdin=stdin, timeout=10)
    return JsonResponse({"output": out})


@csrf_exempt
def run_converted_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    converted_code = data.get("converted_code", "")
    converted_lang = data.get("converted_lang", "")
    stdin = data.get("stdin", "")

    if not converted_code or not converted_lang:
        return JsonResponse({"error": "Missing code or language"}, status=400)

    out = run_code(converted_lang, converted_code, stdin=stdin, timeout=10)
    return JsonResponse({"output": out})
