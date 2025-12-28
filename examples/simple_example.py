"""
Simple Example: Quick start with Agentic AI

A minimal example showing how to use the Agentic AI system.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agentic_ai import AgenticAI


def main():
    # Initialize the Agentic AI system
    agent = AgenticAI()
    
    # Execute a simple task
    print("Executing task: Create a file with 'Hello World'")
    result = agent.execute("Write a file named 'hello.txt' containing 'Hello World'")
    
    # Check result
    if result['success']:
        print("[SUCCESS] Task completed successfully!")
    else:
        print("[FAILED] Task failed")
    
    # Execute another task
    print("\nExecuting task: Read the file we just created")
    result2 = agent.execute("Read the file 'hello.txt'")
    
    if result2['success']:
        print("[SUCCESS] File read successfully!")
        # Access the file content from results
        if result2['final_result']:
            for step in result2['final_result'].get('steps', []):
                if step.get('result', {}).get('content'):
                    print(f"Content: {step['result']['content']}")


if __name__ == "__main__":
    main()

