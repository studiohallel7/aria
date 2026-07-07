"""
LLM Tools - Unified tool interface for the autonomous agent.
Integrates all tools and provides a consistent API for the LLM.
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
import json

from .filesystem import FilesystemTools, get_filesystem_tools
from .shell import ShellTools, get_shell_tools
from .web import WebTools, get_web_tools


@dataclass
class ToolDefinition:
    """Definition of a tool available to the LLM."""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


class LLMTools:
    """Unified tool interface for the autonomous agent."""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self._initialize_tools()
    
    def _initialize_tools(self) -> None:
        """Initialize all available tools."""
        # Get tool instances
        self.fs_tools = get_filesystem_tools()
        self.shell_tools = get_shell_tools()
        self.web_tools = get_web_tools()
        
        # Register filesystem tools
        self.register_tool(
            name="read_file",
            description="Read the contents of a file from the workspace",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file relative to workspace"
                    }
                },
                "required": ["path"]
            },
            function=self.fs_tools.read_file
        )
        
        self.register_tool(
            name="write_file",
            description="Write content to a file in the workspace",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file relative to workspace"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            },
            function=self.fs_tools.write_file
        )
        
        self.register_tool(
            name="list_directory",
            description="List contents of a directory",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory relative to workspace (default: '.')"
                    }
                },
                "required": []
            },
            function=self.fs_tools.list_directory
        )
        
        self.register_tool(
            name="search_files",
            description="Search for files matching a pattern",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to match (e.g., '*.py')"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Search recursively (default: false)"
                    }
                },
                "required": ["pattern"]
            },
            function=self.fs_tools.search_files
        )
        
        # Register shell tools
        self.register_tool(
            name="execute_command",
            description="Execute a shell command safely (limited to safe commands)",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory for the command"
                    }
                },
                "required": ["command"]
            },
            function=self.shell_tools.execute
        )
        
        # Register web tools
        self.register_tool(
            name="fetch_webpage",
            description="Fetch and extract text content from a webpage",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the webpage to fetch"
                    }
                },
                "required": ["url"]
            },
            function=self.web_tools.fetch_page
        )
        
        self.register_tool(
            name="search_web",
            description="Search the web using DuckDuckGo (free, no API key). Returns titles, URLs and snippets.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)"
                    }
                },
                "required": ["query"]
            },
            function=self.web_tools.search
        )
        
        self.register_tool(
            name="search_news",
            description="Search for recent news articles using Google News RSS",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "News search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of news results (default: 3)"
                    }
                },
                "required": ["query"]
            },
            function=self.web_tools.search_news
        )
        
        self.register_tool(
            name="get_weather",
            description="Get current weather information for a location using wttr.in (free)",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City or location name"
                    }
                },
                "required": ["location"]
            },
            function=self.web_tools.get_weather
        )
    
    def register_tool(self, name: str, description: str, 
                     parameters: Dict[str, Any], function: Callable) -> None:
        """Register a new tool."""
        self.tools[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            function=function
        )
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get all tool definitions in OpenAI function format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            }
            for tool in self.tools.values()
        ]
    
    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name with given arguments."""
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        
        tool = self.tools[name]
        
        try:
            # Execute the tool function with arguments
            result = tool.function(**arguments)
            return result
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def parse_and_execute(self, tool_call: Dict[str, Any]) -> Any:
        """Parse a tool call from LLM response and execute it."""
        try:
            # Handle different tool call formats
            if 'function' in tool_call:
                # OpenAI format
                name = tool_call['function']['name']
                args_str = tool_call['function']['arguments']
                arguments = json.loads(args_str) if isinstance(args_str, str) else args_str
            else:
                # Direct format
                name = tool_call.get('name', '')
                arguments = tool_call.get('arguments', {})
            
            return self.execute_tool(name, arguments)
            
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON arguments: {str(e)}"}
        except Exception as e:
            return {"error": f"Tool call failed: {str(e)}"}
    
    def get_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        tool = self.tools.get(name)
        if not tool:
            return None
        
        return {
            'name': tool.name,
            'description': tool.description,
            'parameters': tool.parameters,
        }


# Global instance
_llm_tools: Optional[LLMTools] = None


def get_llm_tools() -> LLMTools:
    """Get or create the global LLM tools instance."""
    global _llm_tools
    if _llm_tools is None:
        _llm_tools = LLMTools()
    return _llm_tools


def reset_llm_tools() -> None:
    """Reset the global LLM tools instance (for testing)."""
    global _llm_tools
    _llm_tools = None