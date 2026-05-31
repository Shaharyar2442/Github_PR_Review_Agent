import os
from typing import List
from langchain_core.tools import StructuredTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def get_server_params():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return StdioServerParameters(
        command="python",
        args=[os.path.join(repo_root, "github_mcp", "server.py")],
        env=os.environ.copy()
    )

async def _call_mcp_tool(session: ClientSession, tool_name: str, **kwargs):
    result = await session.call_tool(tool_name, arguments=kwargs)
    if result and result.content:
        return result.content[0].text
    return "No output"

async def create_langchain_tools(session: ClientSession) -> List[StructuredTool]:
    """Dynamically fetches MCP tools and converts them to LangChain StructuredTools."""
    tools_response = await session.list_tools()
    langchain_tools = []
    
    for tool in tools_response.tools:
        # Create a closure to capture the tool name and session
        # We need a proper synchronous/asynchronous wrapper for LangChain
        # LangChain StructuredTool requires a function signature. We will use a generic wrapper.
        
        # We define a factory function to bind the local variables
        def make_func(name=tool.name):
            async def async_tool_wrapper(**kwargs):
                return await _call_mcp_tool(session, name, **kwargs)
            return async_tool_wrapper

        # For schema, we extract it from the MCP tool inputSchema
        from pydantic import create_model
        
        fields = {}
        properties = tool.inputSchema.get("properties", {})
        required = tool.inputSchema.get("required", [])
        
        for prop_name, prop_info in properties.items():
            prop_type = str
            if prop_info.get("type") == "integer":
                prop_type = int
            elif prop_info.get("type") == "number":
                prop_type = float
            elif prop_info.get("type") == "boolean":
                prop_type = bool
            
            if prop_name in required:
                fields[prop_name] = (prop_type, ...)
            else:
                fields[prop_name] = (prop_type, None)
                
        # Create a dynamic Pydantic model for the tool arguments
        schema_model = create_model(f"{tool.name}Schema", **fields)
        
        lc_tool = StructuredTool.from_function(
            func=None,
            coroutine=make_func(tool.name),
            name=tool.name,
            description=tool.description or f"Executes the {tool.name} tool.",
            args_schema=schema_model
        )
        langchain_tools.append(lc_tool)
        
    return langchain_tools
