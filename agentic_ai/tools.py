"""
Tool Registry and Implementations

Provides various tools for the executor to use:
- File operations
- API calls
- Web search
- Calculations
- System commands
"""

import os
import json
import subprocess
import requests
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class Tool(ABC):
    """Base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def __repr__(self):
        return f"Tool(name={self.name}, description={self.description})"


class FileReadTool(Tool):
    """Read content from a file"""
    
    def __init__(self):
        super().__init__(
            name="file_read",
            description="Read content from a file. Parameters: file_path (str)"
        )
    
    def execute(self, file_path: str, **kwargs) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "success": True,
                "content": content,
                "file_path": file_path
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }


class FileWriteTool(Tool):
    """Write content to a file"""
    
    def __init__(self):
        super().__init__(
            name="file_write",
            description="Write content to a file. Parameters: file_path (str), content (str)"
        )
    
    def execute(self, file_path: str, content: str, **kwargs) -> Dict[str, Any]:
        try:
            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }


class FileListTool(Tool):
    """List files in a directory"""
    
    def __init__(self):
        super().__init__(
            name="file_list",
            description="List files in a directory. Parameters: directory (str, optional, default='.')"
        )
    
    def execute(self, directory: str = ".", **kwargs) -> Dict[str, Any]:
        try:
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                files.append({
                    "name": item,
                    "path": item_path,
                    "is_directory": os.path.isdir(item_path),
                    "size": os.path.getsize(item_path) if os.path.isfile(item_path) else None
                })
            return {
                "success": True,
                "directory": directory,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "directory": directory
            }


class APICallTool(Tool):
    """Make HTTP API calls"""
    
    def __init__(self):
        super().__init__(
            name="api_call",
            description="Make HTTP API call. Parameters: url (str), method (str, default='GET'), headers (dict, optional), data (dict, optional)"
        )
    
    def execute(self, url: str, method: str = "GET", headers: Optional[Dict] = None, 
                data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        try:
            method = method.upper()
            headers = headers or {}
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}"
                }
            
            return {
                "success": True,
                "status_code": response.status_code,
                "url": url,
                "method": method,
                "response": response.text[:1000],  # Limit response size
                "headers": dict(response.headers)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }


class WebSearchTool(Tool):
    """Search the web for information"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web. Parameters: query (str). Note: This is a simulated search."
        )
    
    def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        # Simulated web search - in production, this would use a real search API
        # For demonstration, we return structured mock results
        mock_results = [
            {
                "title": f"Result 1 for: {query}",
                "url": f"https://example.com/result1?q={query}",
                "snippet": f"This is a simulated search result for '{query}'. In a real implementation, this would connect to a search API."
            },
            {
                "title": f"Result 2 for: {query}",
                "url": f"https://example.com/result2?q={query}",
                "snippet": f"Another simulated result for '{query}' demonstrating the tool calling capability."
            }
        ]
        
        return {
            "success": True,
            "query": query,
            "results": mock_results,
            "count": len(mock_results),
            "note": "This is a simulated search. In production, integrate with a real search API."
        }


class CalculateTool(Tool):
    """Perform mathematical calculations"""
    
    def __init__(self):
        super().__init__(
            name="calculate",
            description="Perform mathematical calculation. Parameters: expression (str) - e.g., '2 + 2', '10 * 5'"
        )
    
    def execute(self, expression: str, **kwargs) -> Dict[str, Any]:
        try:
            # Safe evaluation - only allow basic math operations
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return {
                    "success": False,
                    "error": "Expression contains invalid characters. Only basic math operations allowed."
                }
            
            result = eval(expression)
            return {
                "success": True,
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }


class SystemCommandTool(Tool):
    """Execute system commands"""
    
    def __init__(self):
        super().__init__(
            name="system_command",
            description="Execute a system command. Parameters: command (str). Use with caution!"
        )
    
    def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        try:
            # Security: Only allow safe commands in demo
            safe_commands = ['ls', 'dir', 'pwd', 'echo', 'date', 'whoami']
            command_parts = command.split()
            if command_parts and command_parts[0] not in safe_commands:
                return {
                    "success": False,
                    "error": f"Command '{command_parts[0]}' not in safe list. Allowed: {safe_commands}"
                }
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }


class JSONParseTool(Tool):
    """Parse and manipulate JSON data"""
    
    def __init__(self):
        super().__init__(
            name="json_parse",
            description="Parse JSON string. Parameters: json_string (str)"
        )
    
    def execute(self, json_string: str, **kwargs) -> Dict[str, Any]:
        try:
            data = json.loads(json_string)
            return {
                "success": True,
                "parsed_data": data,
                "type": type(data).__name__
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "json_string": json_string[:100]  # Truncate for error display
            }


class ToolRegistry:
    """Registry of available tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default tools"""
        default_tools = [
            FileReadTool(),
            FileWriteTool(),
            FileListTool(),
            APICallTool(),
            WebSearchTool(),
            CalculateTool(),
            SystemCommandTool(),
            JSONParseTool()
        ]
        
        for tool in default_tools:
            self.register(tool)
    
    def register(self, tool: Tool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools"""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools.values()
        ]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            }
        
        return tool.execute(**kwargs)

