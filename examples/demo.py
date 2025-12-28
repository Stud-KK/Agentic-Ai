"""
Demo Script: Agentic AI Task Planner & Executor

Demonstrates the capabilities of the Agentic AI system with various examples.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentic_ai import AgenticAI


def demo_basic_file_operations():
    """Demo 1: Basic file operations"""
    print("\n" + "="*70)
    print("DEMO 1: Basic File Operations")
    print("="*70)
    
    agent = AgenticAI()
    
    # Task: Create a file with content
    result = agent.execute("Write a file named 'demo_output.txt' containing 'Hello from Agentic AI!'")
    
    print("\n📊 Execution Summary:")
    print(f"Success: {result['success']}")
    print(f"Iterations: {result['iterations']}")
    
    # Task: Read the file back
    result2 = agent.execute("Read the file 'demo_output.txt'")
    
    print("\n📊 Execution Summary:")
    print(f"Success: {result2['success']}")
    if result2['final_result'] and result2['final_result'].get('steps'):
        for step in result2['final_result']['steps']:
            if step.get('status') == 'completed' and step.get('result', {}).get('content'):
                print(f"File content: {step['result']['content']}")


def demo_multi_step_task():
    """Demo 2: Multi-step task with dependencies"""
    print("\n" + "="*70)
    print("DEMO 2: Multi-Step Task")
    print("="*70)
    
    agent = AgenticAI()
    
    # Multi-step task
    task = """
    1. Calculate 25 * 4
    2. Then write the result to a file called 'calculation_result.txt'
    3. Then read the file to verify
    """
    
    result = agent.execute(task)
    
    print("\n📊 Execution Summary:")
    print(f"Success: {result['success']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Total steps executed: {result['final_result']['total_steps'] if result['final_result'] else 0}")


def demo_api_integration():
    """Demo 3: API integration"""
    print("\n" + "="*70)
    print("DEMO 3: API Integration")
    print("="*70)
    
    agent = AgenticAI()
    
    # Task: Make an API call
    result = agent.execute("Make a GET request to https://jsonplaceholder.typicode.com/posts/1")
    
    print("\n📊 Execution Summary:")
    print(f"Success: {result['success']}")
    if result['final_result'] and result['final_result'].get('steps'):
        for step in result['final_result']['steps']:
            if step.get('status') == 'completed' and step.get('result', {}).get('response'):
                response = step['result']['response']
                print(f"API Response (first 200 chars): {response[:200]}...")


def demo_web_search():
    """Demo 4: Web search simulation"""
    print("\n" + "="*70)
    print("DEMO 4: Web Search")
    print("="*70)
    
    agent = AgenticAI()
    
    # Task: Search for information
    result = agent.execute("Search for information about artificial intelligence")
    
    print("\n📊 Execution Summary:")
    print(f"Success: {result['success']}")
    if result['final_result'] and result['final_result'].get('steps'):
        for step in result['final_result']['steps']:
            if step.get('status') == 'completed' and step.get('result', {}).get('results'):
                results = step['result']['results']
                print(f"Found {len(results)} search results")
                for i, res in enumerate(results[:2], 1):
                    print(f"  {i}. {res.get('title', 'N/A')}")


def demo_complex_workflow():
    """Demo 5: Complex workflow"""
    print("\n" + "="*70)
    print("DEMO 5: Complex Workflow")
    print("="*70)
    
    agent = AgenticAI()
    
    # Complex task combining multiple operations
    task = """
    Create a report by:
    1. Searching for 'Python programming'
    2. Calculating 100 * 3.14
    3. Writing a summary file 'report.txt' with the calculation result
    """
    
    result = agent.execute(task)
    
    print("\n📊 Execution Summary:")
    print(f"Success: {result['success']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Steps completed: {result['final_result']['completed'] if result['final_result'] else 0}/{result['final_result']['total_steps'] if result['final_result'] else 0}")


def demo_available_tools():
    """Demo 6: Show available tools"""
    print("\n" + "="*70)
    print("DEMO 6: Available Tools")
    print("="*70)
    
    agent = AgenticAI()
    tools = agent.get_available_tools()
    
    print(f"\n[TOOLS] Available Tools ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool['name']}")
        print(f"     {tool['description']}")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("AGENTIC AI TASK PLANNER & EXECUTOR - DEMONSTRATION")
    print("="*70)
    print("\nThis demo showcases:")
    print("  • Agentic AI (planner → executor loop)")
    print("  • Autonomous decision making")
    print("  • Tool calling")
    print("  • Multi-step reasoning")
    print("  • Real backend integration")
    
    try:
        demo_available_tools()
        demo_basic_file_operations()
        demo_multi_step_task()
        demo_api_integration()
        demo_web_search()
        demo_complex_workflow()
        
        print("\n" + "="*70)
        print("[SUCCESS] All demos completed!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

