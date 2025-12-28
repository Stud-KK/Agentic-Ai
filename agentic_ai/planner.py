"""
Planner Module

Breaks down complex tasks into executable steps with multi-step reasoning.
"""

from typing import List, Dict, Any, Optional
import re


class PlanStep:
    """Represents a single step in an execution plan"""
    
    def __init__(self, step_id: int, description: str, tool: str, 
                 parameters: Dict[str, Any], dependencies: List[int] = None):
        self.step_id = step_id
        self.description = description
        self.tool = tool
        self.parameters = parameters
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, in_progress, completed, failed
        self.result: Optional[Dict[str, Any]] = None
    
    def __repr__(self):
        return f"PlanStep(id={self.step_id}, tool={self.tool}, status={self.status})"
    
    def to_dict(self):
        return {
            "step_id": self.step_id,
            "description": self.description,
            "tool": self.tool,
            "parameters": self.parameters,
            "dependencies": self.dependencies,
            "status": self.status,
            "result": self.result
        }


class Planner:
    """
    Plans task execution by breaking down complex tasks into steps.
    
    Uses pattern matching and heuristics to identify:
    - File operations (read, write, list)
    - API calls
    - Web searches
    - Calculations
    - Multi-step workflows
    """
    
    def __init__(self):
        self.available_tools = [
            "file_read", "file_write", "file_list",
            "api_call", "web_search", "calculate",
            "system_command", "json_parse"
        ]
    
    def plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[PlanStep]:
        """
        Create an execution plan from a task description.
        
        Args:
            task: High-level task description
            context: Optional context from previous executions
        
        Returns:
            List of PlanStep objects in execution order
        """
        context = context or {}
        steps = []
        step_id = 0
        
        # Normalize task
        task_lower = task.lower()
        
        # Pattern-based planning
        # This simulates LLM-based reasoning for task decomposition
        
        # File write operations (check first to avoid false matches)
        if self._matches_pattern(task, ["write", "save", "create file", "store"]) and not self._matches_pattern(task, ["read"]):
            file_path = self._extract_file_path(task) or self._infer_file_path(task)
            content_hint = self._extract_content_hint(task) or self._extract_content_from_task(task)
            steps.append(PlanStep(
                step_id=step_id,
                description=f"Write to file: {file_path}",
                tool="file_write",
                parameters={"file_path": file_path, "content": content_hint or ""},
                dependencies=[s.step_id for s in steps if s.tool in ["file_read", "calculate", "api_call"]]
            ))
            step_id += 1
        
        # File read operations (check explicitly for read)
        if self._matches_pattern(task, ["read", "load"]) and not self._matches_pattern(task, ["write", "save"]):
            file_path = self._extract_file_path(task)
            if file_path:
                steps.append(PlanStep(
                    step_id=step_id,
                    description=f"Read file: {file_path}",
                    tool="file_read",
                    parameters={"file_path": file_path}
                ))
                step_id += 1
        
        if self._matches_pattern(task, ["list", "directory", "folder", "files"]):
            directory = self._extract_directory(task) or "."
            steps.append(PlanStep(
                step_id=step_id,
                description=f"List files in: {directory}",
                tool="file_list",
                parameters={"directory": directory}
            ))
            step_id += 1
        
        # API operations
        if self._matches_pattern(task, ["api", "http", "request", "call", "fetch", "get data"]):
            url = self._extract_url(task) or self._infer_api_endpoint(task)
            method = self._extract_http_method(task) or "GET"
            steps.append(PlanStep(
                step_id=step_id,
                description=f"Make API call: {method} {url}",
                tool="api_call",
                parameters={"url": url, "method": method}
            ))
            step_id += 1
        
        # Web search
        if self._matches_pattern(task, ["search", "find", "lookup", "information about"]):
            query = self._extract_search_query(task)
            steps.append(PlanStep(
                step_id=step_id,
                description=f"Search for: {query}",
                tool="web_search",
                parameters={"query": query}
            ))
            step_id += 1
        
        # Calculations
        if self._matches_pattern(task, ["calculate", "compute", "math", "add", "multiply"]):
            expression = self._extract_expression(task)
            if expression:
                steps.append(PlanStep(
                    step_id=step_id,
                    description=f"Calculate: {expression}",
                    tool="calculate",
                    parameters={"expression": expression}
                ))
                step_id += 1
        
        # Multi-step task decomposition
        if self._is_multi_step_task(task):
            steps = self._decompose_multi_step(task, steps, step_id)
        
        # If no specific patterns matched, create a generic plan
        if not steps:
            steps = self._create_generic_plan(task, step_id)
        
        return steps
    
    def _matches_pattern(self, task: str, patterns: List[str]) -> bool:
        """Check if task matches any of the given patterns"""
        task_lower = task.lower()
        return any(pattern.lower() in task_lower for pattern in patterns)
    
    def _extract_file_path(self, task: str) -> Optional[str]:
        """Extract file path from task description"""
        # Look for quoted paths or paths with extensions
        patterns = [
            r'"([^"]+\.\w+)"',  # Quoted path with extension
            r"'([^']+\.\w+)'",  # Single-quoted path
            r'(\S+\.(txt|json|csv|py|md|html|xml))',  # Unquoted path with extension
        ]
        for pattern in patterns:
            match = re.search(pattern, task)
            if match:
                return match.group(1)
        return None
    
    def _extract_directory(self, task: str) -> Optional[str]:
        """Extract directory path from task"""
        patterns = [
            r'in\s+["\']([^"\']+)["\']',
            r'directory\s+["\']([^"\']+)["\']',
            r'folder\s+["\']([^"\']+)["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _infer_file_path(self, task: str) -> str:
        """Infer a file path from task context"""
        if "report" in task.lower():
            return "report.txt"
        elif "data" in task.lower():
            return "data.json"
        elif "summary" in task.lower():
            return "summary.md"
        else:
            return "output.txt"
    
    def _extract_content_hint(self, task: str) -> Optional[str]:
        """Extract content hint from task"""
        # Look for content after keywords like "containing", "with content"
        patterns = [
            r'containing\s+["\']([^"\']+)["\']',
            r'with\s+content\s+["\']([^"\']+)["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_content_from_task(self, task: str) -> Optional[str]:
        """Extract content from task description more broadly"""
        # Look for quoted content
        patterns = [
            r'containing\s+["\']([^"\']+)["\']',
            r'with\s+["\']([^"\']+)["\']',
            r'["\']([^"\']+)["\']',  # Any quoted string
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                content = match.group(1)
                # Skip if it looks like a file path
                if not ('.' in content and len(content.split()) == 1):
                    return content
        return None
    
    def _extract_url(self, task: str) -> Optional[str]:
        """Extract URL from task"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        match = re.search(url_pattern, task)
        return match.group(0) if match else None
    
    def _infer_api_endpoint(self, task: str) -> str:
        """Infer API endpoint from task context"""
        if "weather" in task.lower():
            return "https://api.openweathermap.org/data/2.5/weather"
        elif "user" in task.lower():
            return "https://jsonplaceholder.typicode.com/users/1"
        else:
            return "https://jsonplaceholder.typicode.com/posts/1"
    
    def _extract_http_method(self, task: str) -> Optional[str]:
        """Extract HTTP method from task"""
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        task_upper = task.upper()
        for method in methods:
            if method in task_upper:
                return method
        return None
    
    def _extract_search_query(self, task: str) -> str:
        """Extract search query from task"""
        # Remove common prefixes
        query = task
        prefixes = ["search for", "find", "lookup", "information about", "search"]
        for prefix in prefixes:
            if task.lower().startswith(prefix):
                query = task[len(prefix):].strip()
                break
        
        # Remove quotes if present
        query = query.strip('"\'')
        return query if query else task
    
    def _extract_expression(self, task: str) -> Optional[str]:
        """Extract mathematical expression from task"""
        # Look for expressions like "2 + 2", "10 * 5", etc.
        patterns = [
            r'(\d+\s*[+\-*/]\s*\d+)',
            r'calculate\s+([0-9+\-*/.()\s]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, task)
            if match:
                return match.group(1).strip()
        return None
    
    def _is_multi_step_task(self, task: str) -> bool:
        """Check if task contains multiple steps"""
        # Look for numbered lists, "then", "and", "after"
        multi_step_indicators = [
            r'\d+\.',  # Numbered list
            r'then\s+',
            r'and\s+then',
            r'after\s+that',
            r'next\s+',
        ]
        return any(re.search(pattern, task, re.IGNORECASE) for pattern in multi_step_indicators)
    
    def _decompose_multi_step(self, task: str, existing_steps: List[PlanStep], 
                              start_id: int) -> List[PlanStep]:
        """Decompose a multi-step task"""
        steps = existing_steps.copy()
        step_id = start_id
        
        # Split by numbered list or keywords
        if re.search(r'\d+\.', task):
            # Numbered list format
            parts = re.split(r'\d+\.\s*', task)[1:]  # Skip first empty part
            for i, part in enumerate(parts):
                sub_steps = self.plan(part.strip(), {})
                for sub_step in sub_steps:
                    sub_step.step_id = step_id
                    sub_step.dependencies = [s.step_id for s in steps if s.step_id < step_id]
                    steps.append(sub_step)
                    step_id += 1
        else:
            # Keyword-based splitting
            keywords = ["then", "and then", "after that", "next"]
            parts = re.split(r'|'.join(keywords), task, flags=re.IGNORECASE)
            for part in parts:
                sub_steps = self.plan(part.strip(), {})
                for sub_step in sub_steps:
                    sub_step.step_id = step_id
                    sub_step.dependencies = [s.step_id for s in steps if s.step_id < step_id]
                    steps.append(sub_step)
                    step_id += 1
        
        return steps
    
    def _create_generic_plan(self, task: str, start_id: int) -> List[PlanStep]:
        """Create a generic plan when no specific patterns match"""
        # Try to infer the most likely action
        if "file" in task.lower():
            return [PlanStep(
                step_id=start_id,
                description=f"Process task: {task}",
                tool="file_list",
                parameters={"directory": "."}
            )]
        elif any(word in task.lower() for word in ["data", "information", "get"]):
            return [PlanStep(
                step_id=start_id,
                description=f"Process task: {task}",
                tool="web_search",
                parameters={"query": task}
            )]
        else:
            return [PlanStep(
                step_id=start_id,
                description=f"Process task: {task}",
                tool="system_command",
                parameters={"command": f"echo '{task}'"}
            )]
    
    def adjust_plan(self, steps: List[PlanStep], execution_results: Dict[int, Dict[str, Any]]) -> List[PlanStep]:
        """Adjust plan based on execution results (replanning capability)"""
        # Identify failed steps
        failed_steps = [s for s in steps if s.status == "failed"]
        
        if not failed_steps:
            return steps
        
        # Create retry steps or alternative approaches
        adjusted_steps = steps.copy()
        for failed_step in failed_steps:
            # Try alternative tool or approach
            if failed_step.tool == "api_call":
                # Maybe try web search as alternative
                alt_step = PlanStep(
                    step_id=len(adjusted_steps),
                    description=f"Alternative approach for: {failed_step.description}",
                    tool="web_search",
                    parameters={"query": failed_step.description}
                )
                adjusted_steps.append(alt_step)
        
        return adjusted_steps

