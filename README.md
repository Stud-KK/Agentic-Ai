# Agentic AI Task Planner & Executor

🧠 **Demonstrates Agentic AI capabilities with LLM integration**

This project showcases a complete Agentic AI system that demonstrates:
- **Agentic AI (planner → executor loop)**: Autonomous task planning and execution
- **Autonomous decision making**: Self-directed problem solving
- **Tool calling**: Dynamic tool selection and execution
- **Multi-step reasoning**: Complex task decomposition
- **Real backend integration**: File operations, API calls, web interactions

## Architecture

```
┌─────────────┐
│   Planner   │  ← Breaks down complex tasks into executable steps
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Executor   │  ← Executes steps using available tools
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Tools    │  ← File ops, APIs, web search, calculations, etc.
└─────────────┘
```

## Features

### 🎯 Planner Module
- Task decomposition and planning
- Multi-step reasoning
- Dynamic plan adjustment based on results

### ⚙️ Executor Module
- Tool selection and execution
- Error handling and retry logic
- Result aggregation

### 🛠️ Available Tools
- **File Operations**: Read, write, list files
- **API Integration**: REST API calls
- **Web Search**: Information retrieval
- **Calculations**: Mathematical operations
- **System Commands**: Execute shell commands
- **Data Processing**: JSON manipulation, data transformation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 🌐 Web Interface (Recommended)

**Easiest way to use the system!**

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the web application:
   ```bash
   python app.py
   ```
   Or double-click `start_web.bat` (Windows)

3. Open your browser:
   Go to **http://localhost:5000**

4. Enter tasks and see results in real-time!

### 💻 Command Line

```python
from agentic_ai import AgenticAI

agent = AgenticAI()

# Execute a complex task
result = agent.execute("Create a report analyzing the weather data and save it to a file")
print(result)
```

### Advanced Example

```python
from agentic_ai import AgenticAI

agent = AgenticAI()

# Multi-step task with dependencies
task = """
1. Search for the latest AI research papers
2. Extract key findings
3. Create a summary document
4. Send the summary via API
"""

result = agent.execute(task)
```

## Project Structure

```
.
├── agentic_ai/
│   ├── __init__.py
│   ├── planner.py          # Task planning and decomposition
│   ├── executor.py         # Step execution and tool calling
│   ├── tools.py            # Tool registry and implementations
│   └── agent.py            # Main agentic loop orchestrator
├── examples/
│   └── demo.py             # Example usage
├── requirements.txt
└── README.md
```

## How It Works

1. **Planning Phase**: The planner receives a high-level task and breaks it down into executable steps
2. **Execution Phase**: The executor selects appropriate tools and executes each step
3. **Feedback Loop**: Results from execution inform subsequent planning decisions
4. **Iteration**: The system continues until the task is complete or cannot proceed further

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## License

MIT License

