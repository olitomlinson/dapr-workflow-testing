"""
FastAPI web server for the Hello World app.
"""
import logging
from typing import Dict
from functools import lru_cache

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import dapr.ext.workflow as wf

from .workflows.hello_workflow import hello_workflow

logger = logging.getLogger(__name__)


@lru_cache()
def get_workflow_client() -> wf.DaprWorkflowClient:
    """Get cached DaprWorkflowClient instance for dependency injection."""
    return wf.DaprWorkflowClient()


class GreetingRequest(BaseModel):
    """Request model for greeting endpoint."""
    name: str


class WebServer:
    """
    FastAPI web server for the Hello World app.

    Provides REST API endpoints to trigger Dapr workflows.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Initialize the web server.

        Args:
            host: Server host address
            port: Server port number
        """
        self.host = host
        self.port = port
        self.app = create_app()
        self.server = None

    async def start(self) -> None:
        """Start the FastAPI server."""
        try:
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            self.server = uvicorn.Server(config)
            logger.info(f"Starting web server on {self.host}:{self.port}")
            await self.server.serve()

        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop the FastAPI server."""
        try:
            if self.server:
                logger.info("Stopping web server")
                self.server.should_exit = True

        except Exception as e:
            logger.error(f"Error during web server shutdown: {e}")

    def run(self) -> None:
        """Run the server (blocking)."""
        uvicorn.run(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="Hello World Dapr Workflow API",
        description="Simple FastAPI app with Dapr workflow integration",
        version="0.1.0",
    )

    @app.get("/", response_model=Dict[str, str])
    async def root():
        """Root endpoint providing API information."""
        return {
            "message": "Hello World Dapr Workflow API",
            "version": "0.1.0",
            "status": "running"
        }

    @app.get("/health", response_model=Dict[str, str])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.post("/greet")
    async def greet(
        request: GreetingRequest,
        wf_client: wf.DaprWorkflowClient = Depends(get_workflow_client)
    ):
        """
        Trigger a greeting workflow.

        This endpoint starts a Dapr workflow that generates a greeting message.
        """
        try:
            logger.info(f"Received greeting request for: {request.name}")

            # Generate a unique instance ID
            import uuid
            instance_id = str(uuid.uuid4())

            # Schedule the workflow
            wf_client.schedule_new_workflow(
                workflow=hello_workflow,
                input={"name": request.name},
                instance_id=instance_id
            )

            logger.info(f"Started workflow instance: {instance_id}")

            # Wait for workflow to complete and get result
            state = wf_client.wait_for_workflow_completion(
                instance_id=instance_id,
                timeout_in_seconds=30
            )

            return JSONResponse(
                status_code=200,
                content={
                    "workflow_instance_id": instance_id,
                    "result": state.serialized_output,
                    "status": "completed"
                }
            )

        except Exception as e:
            logger.error(f"Failed to process greeting request: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to process request: {str(e)}"}
            )

    @app.post("/schedule-workflow")
    async def schedule_workflow(
        request: GreetingRequest,
        wf_client: wf.DaprWorkflowClient = Depends(get_workflow_client)
    ):
        """
        Schedule a greeting workflow without waiting for completion.

        This endpoint starts a Dapr workflow and returns immediately with the workflow instance ID.
        The workflow runs asynchronously in the background.
        """
        try:
            logger.info(f"Scheduling workflow for: {request.name}")

            # Generate a unique instance ID
            import uuid
            instance_id = str(uuid.uuid4())

            # Schedule the workflow (fire and forget)
            wf_client.schedule_new_workflow(
                workflow=hello_workflow,
                input={"name": request.name},
                instance_id=instance_id
            )

            logger.info(f"Scheduled workflow instance: {instance_id}")

            return JSONResponse(
                status_code=202,
                content={
                    "workflow_instance_id": instance_id,
                    "status": "scheduled",
                    "message": f"Workflow scheduled successfully for {request.name}"
                }
            )

        except Exception as e:
            logger.error(f"Failed to schedule workflow: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to schedule workflow: {str(e)}"}
            )

    @app.get("/workflow/{instance_id}")
    async def get_workflow_status(
        instance_id: str,
        wf_client: wf.DaprWorkflowClient = Depends(get_workflow_client)
    ):
        """
        Get the status of a running or completed workflow.

        Returns the current state and output (if completed) of a workflow instance.
        """
        try:
            logger.info(f"Checking status for workflow: {instance_id}")

            # Get workflow state
            state = wf_client.get_workflow_state(instance_id=instance_id)

            response_data = {
                "workflow_instance_id": instance_id,
                "runtime_status": state.runtime_status.name if state.runtime_status else "UNKNOWN",
                "created_at": state.created_at.isoformat() if state.created_at else None,
                "last_updated_at": state.last_updated_at.isoformat() if state.last_updated_at else None,
            }

            # Add output if workflow is completed
            if state.runtime_status and state.runtime_status.name == "COMPLETED":
                response_data["output"] = state.serialized_output

            # Add failure details if workflow failed
            if state.runtime_status and state.runtime_status.name == "FAILED":
                response_data["failure_details"] = state.serialized_output

            return JSONResponse(
                status_code=200,
                content=response_data
            )

        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return JSONResponse(
                status_code=404,
                content={"error": f"Workflow not found or error retrieving status: {str(e)}"}
            )

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    return app


if __name__ == "__main__":
    server = WebServer()
    server.run()
