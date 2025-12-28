"""
Executor Module

Executes planned steps using available tools with error handling and retry logic.
"""

from typing import List, Dict, Any, Optional
from .planner import PlanStep
from .tools import ToolRegistry


class Executor:
    """
    Executes plan steps using the tool registry.
    
    Features:
    - Tool selection and execution
    - Dependency resolution
    - Error handling and retry logic
    - Result aggregation
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.execution_history: List[Dict[str, Any]] = []
    
    def execute_step(self, step: PlanStep, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a single plan step.
        
        Args:
            step: The plan step to execute
            context: Optional context from previous executions
        
        Returns:
            Execution result dictionary
        """
        context = context or {}
        step.status = "in_progress"
        
        try:
            # Resolve parameters using context
            resolved_params = self._resolve_parameters(step.parameters, context)
            
            # Execute the tool
            result = self.tool_registry.execute_tool(step.tool, **resolved_params)
            
            # Update step status
            if result.get("success", False):
                step.status = "completed"
            else:
                step.status = "failed"
            
            step.result = result
            
            # Record execution
            execution_record = {
                "step_id": step.step_id,
                "tool": step.tool,
                "parameters": resolved_params,
                "result": result,
                "status": step.status
            }
            self.execution_history.append(execution_record)
            
            return result
        
        except Exception as e:
            step.status = "failed"
            error_result = {
                "success": False,
                "error": str(e),
                "step_id": step.step_id
            }
            step.result = error_result
            
            execution_record = {
                "step_id": step.step_id,
                "tool": step.tool,
                "parameters": step.parameters,
                "result": error_result,
                "status": "failed"
            }
            self.execution_history.append(execution_record)
            
            return error_result
    
    def execute_plan(self, steps: List[PlanStep], max_retries: int = 2) -> Dict[str, Any]:
        """
        Execute a complete plan respecting dependencies.
        
        Args:
            steps: List of plan steps to execute
            max_retries: Maximum number of retries for failed steps
        
        Returns:
            Summary of execution results
        """
        execution_order = self._resolve_dependencies(steps)
        context = {}
        results = {}
        
        for step_id in execution_order:
            step = next(s for s in steps if s.step_id == step_id)
            
            # Check dependencies
            if not self._dependencies_satisfied(step, steps):
                step.status = "failed"
                results[step_id] = {
                    "success": False,
                    "error": "Dependencies not satisfied"
                }
                continue
            
            # Execute with retries
            retry_count = 0
            result = None
            
            while retry_count <= max_retries:
                result = self.execute_step(step, context)
                
                if result.get("success", False):
                    break
                
                retry_count += 1
                if retry_count <= max_retries:
                    # Update context for retry
                    context.update(self._extract_context(result))
            
            results[step_id] = result
            
            # Update context with successful results
            if result.get("success", False):
                context.update(self._extract_context(result))
                context[f"step_{step_id}_result"] = result
        
        # Generate summary
        summary = self._generate_summary(steps, results)
        return summary
    
    def _resolve_dependencies(self, steps: List[PlanStep]) -> List[int]:
        """Resolve execution order based on dependencies (topological sort)"""
        # Build dependency graph
        graph = {step.step_id: step.dependencies for step in steps}
        
        # Topological sort
        in_degree = {step_id: 0 for step_id in graph}
        for step_id, deps in graph.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[step_id] += 1
        
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            step_id = queue.pop(0)
            execution_order.append(step_id)
            
            # Update in-degrees
            for other_id, deps in graph.items():
                if step_id in deps:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)
        
        # Add any remaining steps (cycles or orphaned)
        remaining = [s.step_id for s in steps if s.step_id not in execution_order]
        execution_order.extend(remaining)
        
        return execution_order
    
    def _dependencies_satisfied(self, step: PlanStep, all_steps: List[PlanStep]) -> bool:
        """Check if all dependencies are satisfied"""
        if not step.dependencies:
            return True
        
        for dep_id in step.dependencies:
            dep_step = next((s for s in all_steps if s.step_id == dep_id), None)
            if not dep_step or dep_step.status != "completed":
                return False
        
        return True
    
    def _resolve_parameters(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve parameters using context (e.g., from previous step results)"""
        resolved = {}
        
        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Template variable: ${step_1_result.content}
                var_path = value[2:-1]
                resolved[key] = self._get_context_value(var_path, context)
            elif isinstance(value, str) and "{{" in value:
                # Template string: "File: {{step_1_result.file_path}}"
                resolved[key] = self._resolve_template(value, context)
            else:
                resolved[key] = value
        
        return resolved
    
    def _get_context_value(self, path: str, context: Dict[str, Any]) -> Any:
        """Get value from context using dot notation"""
        parts = path.split(".")
        value = context
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        
        return value
    
    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Resolve template string with context variables"""
        result = template
        # Simple template resolution
        import re
        matches = re.findall(r'\{\{([^}]+)\}\}', template)
        for match in matches:
            value = self._get_context_value(match.strip(), context)
            if value is not None:
                result = result.replace(f"{{{{{match}}}}}", str(value))
        return result
    
    def _extract_context(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract useful context from execution result"""
        context = {}
        
        if result.get("success"):
            # Extract key fields based on tool type
            if "content" in result:
                context["content"] = result["content"]
            if "file_path" in result:
                context["file_path"] = result["file_path"]
            if "response" in result:
                context["api_response"] = result["response"]
            if "results" in result:
                context["search_results"] = result["results"]
            if "result" in result:
                context["calculation_result"] = result["result"]
        
        return context
    
    def _generate_summary(self, steps: List[PlanStep], results: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate execution summary"""
        total_steps = len(steps)
        completed = sum(1 for s in steps if s.status == "completed")
        failed = sum(1 for s in steps if s.status == "failed")
        pending = sum(1 for s in steps if s.status == "pending")
        
        return {
            "success": failed == 0,
            "total_steps": total_steps,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "steps": [s.to_dict() for s in steps],
            "results": results,
            "execution_history": self.execution_history
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history.copy()


