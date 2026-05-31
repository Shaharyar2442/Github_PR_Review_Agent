import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_tools():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    server_params = StdioServerParameters(
        command="python",
        args=["github_mcp/server.py"],
        env=os.environ.copy()
    )

    print("Connecting to MCP Server via stdio...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected! Fetching tools...")
            
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"Tool: {tool.name} - {tool.description}")
            
            print("\nTesting read_file_tool...")
            result = await session.call_tool("read_file_tool", arguments={"file_path": "requirements.txt", "start_line": 1, "end_line": 5})
            print(f"Result:\n{result.content[0].text}")

if __name__ == "__main__":
    if os.name == 'nt':
        import selectors
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_mcp_tools())
