# Hello World Dapr Workflow App

A simple FastAPI application with Dapr workflow integration, demonstrating how to run both a web server and workflow runtime together as separate processes.

## Architecture

This application demonstrates the coordination of:
1. **FastAPI Web Server**: Handles HTTP requests and triggers workflows
2. **Dapr Workflow Runtime**: Runs as a separate process to execute workflows

The architecture is inspired by production patterns where the web server and workflow runtime run independently but coordinate through Dapr.

## Project Structure

```
python/
├── src/
│   └── hello_world_app/
│       ├── __init__.py
│       ├── main.py              # Main entry point that coordinates both processes
│       ├── web_server.py        # FastAPI server
│       ├── config.py            # Global workflow runtime configuration
│       ├── workflow_manager.py  # Workflow runtime lifecycle manager
│       ├── workflows/
│       │   ├── __init__.py
│       │   └── hello_workflow.py  # Simple hello world workflow
│       └── activities/
│           ├── __init__.py
│           └── greeting_activity.py  # Activity for generating greetings
├── pyproject.toml
├── requirements.txt
├── run_local.sh              # Script to run with Dapr CLI
└── README.md
```

## Prerequisites

- Python 3.10 or higher
- Dapr CLI (will be installed automatically by run_local.sh)

## Setup

1. Create and activate a virtual environment:
```bash
cd python
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install the application:
```bash
pip install -e .
```

## Running the Application

### Option 1: Using the run script (Recommended)

The easiest way to run the application is using the provided script:

```bash
./run_local.sh
```

This script will:
- Install Dapr CLI if not present
- Initialize Dapr runtime
- Create and activate a virtual environment
- Install dependencies
- Start the application with Dapr

### Option 2: Manual start with Dapr

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD/src:$PYTHONPATH"
dapr run \
    --app-id hello-world-app \
    --app-port 8000 \
    --dapr-http-port 3500 \
    --dapr-grpc-port 50001 \
    --log-level info \
    -- python -m hello_world_app.main
```

### Option 3: Using Docker

Build the Docker image:

```bash
docker build -t hello-world-app:latest .
```

Run with Dapr using Docker:

```bash
# Run the container with Dapr sidecar
dapr run \
    --app-id hello-world-app \
    --app-port 8000 \
    --dapr-http-port 3500 \
    --dapr-grpc-port 50001 \
    --log-level info \
    -- docker run -p 8000:8000 --rm hello-world-app:latest
```

Or run the container directly (without Dapr, for testing):

```bash
docker run -p 8000:8000 --rm hello-world-app:latest
```

## Testing the Application

Once running, the API will be available at http://localhost:8000

### Available Endpoints

1. **Root endpoint**:
```bash
curl http://localhost:8000/
```

2. **Health check**:
```bash
curl http://localhost:8000/health
```

3. **Trigger a greeting workflow**:
```bash
curl -X POST http://localhost:8000/greet \
  -H "Content-Type: application/json" \
  -d '{"name": "World"}'
```

This will start a Dapr workflow that:
- Calls a greeting activity
- Generates a personalized message
- Returns the result with workflow details

### API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## How It Works

1. **Bootstrapping**: The main.py coordinates starting both the workflow runtime and web server
2. **Workflow Runtime**: Starts first and registers workflows/activities
3. **Web Server**: Starts after the workflow runtime is ready
4. **Request Flow**:
   - HTTP request comes to FastAPI endpoint
   - Endpoint uses DaprWorkflowClient to schedule a workflow
   - Workflow runtime executes the workflow and activities
   - Result is returned to the client

## Key Components

- **main.py**: Entry point that coordinates the lifecycle of both services
- **web_server.py**: FastAPI application with workflow integration
- **config.py**: Global workflow runtime instance (singleton pattern)
- **workflow_manager.py**: Manages workflow runtime lifecycle
- **workflows/hello_workflow.py**: Simple workflow that calls an activity
- **activities/greeting_activity.py**: Activity that generates greetings

## Stopping the Application

Press `Ctrl+C` to gracefully shutdown both the web server and workflow runtime.
