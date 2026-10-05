"""Post-freeze tool-contract evaluation, not an LLM benchmark."""

import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from transport.client import call_tools


def response_error(response):
    return response.get("is_error", response.get("isError", False))


# A replay must use the same cases and documents as the original evaluation, so
# their hashes are checked against the recorded freeze. Code is not fingerprinted:
# git records it, and a code change that alters behaviour shows up in the score.
FROZEN_INPUTS = ("data/corpus/documents.json", "evidence/ai/final-tool-cases.json")


def verify_tool_freeze(root):
    freeze = root / "evidence/ai/system-freeze.json"
    frozen = json.loads(freeze.read_text())
    for name in FROZEN_INPUTS:
        path = root / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if frozen.get(name) != digest:
            raise ValueError(f"tool freeze mismatch: {name}")
    return hashlib.sha256(freeze.read_bytes()).hexdigest()


async def evaluate(root):
    freeze_sha = verify_tool_freeze(root)
    cases = json.loads((root / "evidence/ai/final-tool-cases.json").read_text())
    outputs = []
    for offset in range(0, len(cases), 6):
        batch = cases[offset : offset + 6]
        response = await call_tools([c["request"] for c in batch])
        for c, actual in zip(batch, response["calls"], strict=True):
            r = actual["response"]
            structured = r.get("structured_content", r.get("structuredContent"))
            # MCP SDK wraps some structured dict returns under result.
            if structured is None:
                content = r.get("content", [])
                try:
                    structured = json.loads(
                        next(b["text"] for b in content if b.get("type") == "text")
                    )
                except (ValueError, StopIteration):
                    structured = {}
            if "result" in structured:
                structured = structured["result"]
            expected = c["expected"]
            if expected.get("error"):
                passed = response_error(r) is True
            else:
                passed = not response_error(r)
                for key, value in expected.items():
                    if key == "document_id":
                        passed = passed and value in [
                            d["id"] for d in structured.get("documents", [])
                        ]
                    elif key == "empty_documents":
                        passed = passed and structured.get("documents") == []
                    elif key == "quality_crashes":
                        passed = (
                            passed
                            and structured.get("quality", {}).get("analysis_crashes") == value
                        )
                    else:
                        passed = passed and structured.get(key) == value
            outputs.append(
                {
                    "id": c["id"],
                    "category": c["category"],
                    "passed": bool(passed),
                    "request": c["request"],
                    "expected": expected,
                    "response": r,
                }
            )
    report = {
        "evaluation_kind": "regression replay of already-seen cases; not a new held-out evaluation",
        "system_freeze_sha256": freeze_sha,
        "recorded_utc": datetime.now(UTC).isoformat(),
        "scope": "Tool contracts over real MCP transport. No live LLM, agent-selection or generated-answer reliability claim.",
        "cases": len(outputs),
        "passed": sum(c["passed"] for c in outputs),
        "results": outputs,
    }
    # Append a unique replay record; neither historical score file is a write target.
    directory = root / "evidence/ai/regressions"
    directory.mkdir(exist_ok=True)
    path = directory / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8] + ".json"
    )
    with path.open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
    print(f"Regression artifact: {path}")
    print({k: v for k, v in report.items() if k != "results"})
    return report


if __name__ == "__main__":
    asyncio.run(evaluate(Path(__file__).resolve().parents[2]))
