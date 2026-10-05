"""Real subprocess MCP transport; fixed allowlist, argument limits and total deadline."""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

ALLOWED = {"aggregate_stats", "inspect_area", "quality_provenance", "search_documents"}


async def call_tools(calls):
    if not 1 <= len(calls) <= 6:
        raise ValueError("one to six calls required")
    for c in calls:
        if c.get("name") not in ALLOWED:
            raise ValueError("tool not allowed")
        if len(json.dumps(c.get("arguments", {}))) > 2000:
            raise ValueError("arguments too large")
    root = Path(__file__).resolve().parents[2]
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "transport.server"],
        env={"PYTHONPATH": str(root / "src"), "PATH": os.environ.get("PATH", "")},
    )
    started = time.monotonic()
    output = []
    async with (
        asyncio.timeout(60),
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        names = {t.name for t in (await session.list_tools()).tools}
        if names != ALLOWED:
            raise ValueError("unexpected server tool surface")
        for c in calls:
            r = await session.call_tool(c["name"], c.get("arguments", {}))
            output.append({"request": c, "response": r.model_dump(mode="json")})
    return {
        "transport": "real MCP stdio",
        "elapsed_seconds": time.monotonic() - started,
        "calls": output,
    }


if __name__ == "__main__":
    calls = (
        json.loads(sys.argv[1])
        if len(sys.argv) > 1
        else [
            {"name": "aggregate_stats", "arguments": {"start_year": 2024, "end_year": 2024}},
            {"name": "quality_provenance", "arguments": {}},
        ]
    )
    print(json.dumps(asyncio.run(call_tools(calls)), indent=2))
