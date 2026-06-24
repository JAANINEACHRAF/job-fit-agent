"""Tests for the MCP server: tools are registered with correct metadata."""
from job_fit_agent.mcp.server import mcp

EXPECTED_TOOLS = {
    "search_job_offers",
    "assess_offer_fit",
    "assess_offer_fit_validated",
}


async def test_all_tools_registered():
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert names == EXPECTED_TOOLS


async def test_tools_have_descriptions():
    tools = await mcp.list_tools()
    for tool in tools:
        assert tool.description, f"{tool.name} is missing a description"


async def test_search_tool_has_keywords_param():
    tools = await mcp.list_tools()
    search = next(t for t in tools if t.name == "search_job_offers")
    # inputSchema is a JSON-schema dict; check the expected parameter exists
    assert "keywords" in search.inputSchema["properties"]
