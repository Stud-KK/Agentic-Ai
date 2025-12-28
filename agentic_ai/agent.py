"""
Main Agentic AI Module

Orchestrates the planner-executor loop with autonomous decision making.
"""

from typing import Dict, Any, Optional, List
from .planner import Planner, PlanStep
from .executor import Executor
from .tools import ToolRegistry


class AgenticAI:
    """
    Main Agentic AI system that demonstrates:
    - Planner → Executor loop
    - Autonomous decision making
    - Tool calling
    - Multi-step reasoning
    - Real backend integration
    """
    
    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        """
        Initialize the Agentic AI system.
        
        Args:
            tool_registry: Optional custom tool registry. If None, creates default.
        """
        self.tool_registry = tool_registry or ToolRegistry()
        self.planner = Planner()
        self.executor = Executor(self.tool_registry)
        self.execution_context: Dict[str, Any] = {}
        self.max_iterations = 10  # Prevent infinite loops
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a high-level task using the agentic loop.
        
        The agentic loop:
        1. Plan: Break down task into steps
        2. Execute: Run steps using tools
        3. Evaluate: Check if goal is achieved
        4. Replan: Adjust plan if needed
        5. Repeat until complete or max iterations
        
        Args:
            task: High-level task description
            context: Optional initial context
        
        Returns:
            Execution result with summary and details
        """
        if context:
            self.execution_context.update(context)
        
        iteration = 0
        all_steps: List[PlanStep] = []
        final_result: Optional[Dict[str, Any]] = None
        
        print(f"[TASK] {task}")
        print("=" * 60)
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n[ITERATION {iteration}]")
            print("-" * 60)
            
            # Planning Phase
            print("[PLANNING] Planning phase...")
            steps = self.planner.plan(task, self.execution_context)
            
            if not steps:
                return {
                    "success": False,
                    "error": "Could not create execution plan",
                    "iteration": iteration
                }
            
            print(f"   Created {len(steps)} step(s)")
            for step in steps:
                print(f"   - Step {step.step_id}: {step.description} (tool: {step.tool})")
            
            # Execution Phase
            print("\n[EXECUTION] Execution phase...")
            execution_result = self.executor.execute_plan(steps)
            
            # Update context with execution results
            self._update_context(execution_result)
            
            # Display results
            print(f"   Completed: {execution_result['completed']}/{execution_result['total_steps']}")
            print(f"   Failed: {execution_result['failed']}")
            
            # Check if goal is achieved
            if execution_result['success']:
                print("\n[SUCCESS] Task completed successfully!")
                final_result = execution_result
                break
            
            # Replanning Phase (if needed)
            if execution_result['failed'] > 0:
                print("\n[REPLANNING] Replanning phase...")
                adjusted_steps = self.planner.adjust_plan(steps, execution_result['results'])
                
                if len(adjusted_steps) == len(steps):
                    # No adjustments made, might be stuck
                    print("   No viable alternative plan found")
                    final_result = execution_result
                    break
                
                # Continue with adjusted plan
                steps = adjusted_steps
                print(f"   Adjusted plan: {len(adjusted_steps)} step(s)")
            
            all_steps.extend(steps)
        
        if iteration >= self.max_iterations:
            print(f"\n[WARNING] Maximum iterations ({self.max_iterations}) reached")
        
        print("\n" + "=" * 60)
        
        return {
            "success": final_result['success'] if final_result else False,
            "task": task,
            "iterations": iteration,
            "final_result": final_result,
            "execution_context": self.execution_context,
            "available_tools": self.tool_registry.list_tools()
        }
    
    def _update_context(self, execution_result: Dict[str, Any]):
        """Update execution context with results"""
        if "steps" in execution_result:
            for step_data in execution_result["steps"]:
                if step_data.get("status") == "completed" and step_data.get("result"):
                    result = step_data["result"]
                    step_id = step_data["step_id"]
                    
                    # Store step result in context
                    self.execution_context[f"step_{step_id}_result"] = result
                    
                    # Extract useful data
                    if "content" in result:
                        self.execution_context["last_file_content"] = result["content"]
                    if "file_path" in result:
                        self.execution_context["last_file_path"] = result["file_path"]
                    if "api_response" in result:
                        self.execution_context["last_api_response"] = result.get("response")
                    if "search_results" in result:
                        self.execution_context["last_search_results"] = result.get("results")
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of available tools"""
        return self.tool_registry.list_tools()
    
    def add_tool(self, tool):
        """Add a custom tool to the registry"""
        self.tool_registry.register(tool)
    
    def reset(self):
        """Reset execution context"""
        self.execution_context = {}
        self.executor.execution_history = []

