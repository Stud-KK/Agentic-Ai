"""
Flask Web Application for Agentic AI Task Planner & Executor

Run with: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from agentic_ai import AgenticAI
import json

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Initialize the agent (global instance)
agent = AgenticAI()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/execute', methods=['POST'])
def execute_task():
    """Execute a task via API"""
    try:
        data = request.get_json()
        task = data.get('task', '').strip()
        
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task cannot be empty'
            }), 400
        
        # Execute the task
        result = agent.execute(task)
        
        # Format result for frontend
        formatted_result = {
            'success': result.get('success', False),
            'task': task,
            'iterations': result.get('iterations', 0),
            'final_result': result.get('final_result', {}),
            'execution_context': result.get('execution_context', {}),
            'available_tools': result.get('available_tools', [])
        }
        
        return jsonify(formatted_result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get list of available tools"""
    try:
        tools = agent.get_available_tools()
        return jsonify({
            'success': True,
            'tools': tools
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example tasks"""
    examples = [
        {
            'title': 'File Write',
            'task': "Write a file named 'test.txt' containing 'Hello from Agentic AI!'"
        },
        {
            'title': 'File Read',
            'task': "Read the file 'test.txt'"
        },
        {
            'title': 'Calculation',
            'task': 'Calculate 25 * 4'
        },
        {
            'title': 'Multi-Step Task',
            'task': """1. Calculate 10 * 5
2. Write the result to 'result.txt'
3. Read the file to verify"""
        },
        {
            'title': 'API Call',
            'task': 'Make a GET request to https://jsonplaceholder.typicode.com/posts/1'
        },
        {
            'title': 'Web Search',
            'task': 'Search for information about Python programming'
        },
        {
            'title': 'List Files',
            'task': 'List files in the current directory'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })


if __name__ == '__main__':
    print("\n" + "="*70)
    print("  AGENTIC AI TASK PLANNER & EXECUTOR - Web Interface")
    print("="*70)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


