# MCP demo

A standalone [MCP](https://modelcontextprotocol.io) server that exposes the
job-fit engine to external AI clients (Claude Desktop, Cursor, etc.).

## Why this lives in `examples/` and not in the core

MCP solves one problem: letting an AI client *you don't control* call your tools.
That's useful — but the product itself has its own API, so MCP isn't on the
critical path. Keeping it as a separate demo makes that boundary explicit: the
core doesn't depend on it, and it can be removed without touching anything else.

It's here because writing an MCP server is worth showing — just not worth
pretending it's load-bearing when it isn't.

## Tools

- `search_job_offers(keywords, limit)` — search French job offers
- `assess_offer_fit(offer_id, keywords)` — single-pass fit assessment
- `assess_offer_fit_validated(offer_id, keywords)` — fit assessment via the
  self-critique agent (slower, catches hallucinated skills/gaps)

## Run it

```bash
uv run python examples/mcp-demo/server.py
```

Serves over streamable-http on port 8000. Point any MCP client at it.

## Known limitation

`assess_offer_fit` re-fetches offers by keyword to find one by id, which is
fragile (the offer may not be in the first batch). A cleaner design would fetch
the offer directly by id — noted, not yet done.
