"""
FastAPI web server for the Hello World app.
"""
import logging
from typing import Dict
from functools import lru_cache

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
import dapr.ext.workflow as wf

from .workflows.hello_workflow import hello_workflow
from .workflows.fan_out_workflow import fan_out_workflow

logger = logging.getLogger(__name__)


@lru_cache()
def get_workflow_client() -> wf.DaprWorkflowClient:
    """Get cached DaprWorkflowClient instance for dependency injection."""
    return wf.DaprWorkflowClient()


class GreetingRequest(BaseModel):
    """Request model for greeting endpoint."""
    name: str


class StartWorkflowRequest(BaseModel):
    """Request model for starting a workflow."""
    model_config = ConfigDict(populate_by_name=True)

    Id: str | None = Field(default=None, alias='id')
    FailOnTimeout: bool = Field(default=False, alias='failOnTimeout')
    Sleep: int = Field(default=0, alias='sleep')
    AbortHint: str | None = Field(default=None, alias='abortHint')


class StartWorkflowResponse(BaseModel):
    """Response model for workflow scheduling."""
    Id: str
    status: str | None = None


class WorkflowPayload(BaseModel):
    """Payload for fan-out workflow."""
    RandomData: str
    Iterations: int = 1
    Data: list | None = None


class CloudEventData(BaseModel):
    """CloudEvent wrapper for pub/sub messages."""
    data: StartWorkflowRequest
    id: str | None = None
    specversion: str | None = None
    type: str | None = None
    source: str | None = None


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

    @app.get("/dapr/subscribe")
    async def dapr_subscribe():
        """
        Dapr pub/sub subscription endpoint.

        This endpoint is called by Dapr to discover pub/sub subscriptions.
        """
        subscriptions = [
            {
                "pubsubname": "kafka-pubsub",
                "topic": "fanout-workflow-python",
                "route": "/fanout-workflow"
            }
        ]
        logger.info(f"Returning Dapr subscriptions: {subscriptions}")
        return subscriptions

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

    @app.get("/status-batch")
    async def status_batch(
        run_id: str,
        count: int,
        show_running: bool = False,
        wf_client: wf.DaprWorkflowClient = Depends(get_workflow_client)
    ):
        """
        Get batch status of multiple workflow instances.

        Checks the status of workflow instances with IDs in the format {index}-{run_id}
        and returns a summary of their states.
        """
        try:
            # Initialize counters
            failed = 0
            complete = 0
            running = 0
            pending = 0
            terminated = 0
            suspended = 0
            unknown = 0
            running_instances = {}

            # Check status of each workflow instance
            for i in range(count):
                instance_id = f"{i}-{run_id}"

                try:
                    state = wf_client.get_workflow_state(instance_id=instance_id)

                    # Count by status
                    if state.runtime_status:
                        status_name = state.runtime_status.name
                        if status_name == "COMPLETED":
                            complete += 1
                        elif status_name == "RUNNING":
                            running += 1
                            if show_running:
                                running_instances[instance_id] = {
                                    "runtime_status": status_name,
                                    "created_at": state.created_at.isoformat() if state.created_at else None,
                                    "last_updated_at": state.last_updated_at.isoformat() if state.last_updated_at else None,
                                }
                        elif status_name == "FAILED":
                            failed += 1
                        elif status_name == "PENDING":
                            pending += 1
                        elif status_name == "TERMINATED":
                            terminated += 1
                        elif status_name == "SUSPENDED":
                            suspended += 1
                        else:
                            unknown += 1
                    else:
                        unknown += 1

                except Exception as e:
                    logger.warning(f"Could not get status for workflow {instance_id}: {str(e)}")
                    unknown += 1

            # Build response summary
            summary = (
                f"Completed : {complete}, Failed : {failed}, Running : {running}, "
                f"Pending : {pending}, Terminated : {terminated}, Suspended : {suspended}, "
                f"Unknown : {unknown}\n"
            )

            # Add running instances details if requested
            if show_running and running_instances:
                import json
                summary += "\n"
                for instance_id, state in running_instances.items():
                    summary += f"{instance_id}\n"
                    summary += f"{json.dumps(state, indent=2)}\n"

            return summary

        except Exception as e:
            logger.error(f"Failed to get batch status: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to get batch status: {str(e)}"}
            )

    @app.post("/fanout-workflow")
    async def fanout_workflow_handler(
        request: Request,
        wf_client: wf.DaprWorkflowClient = Depends(get_workflow_client)
    ):
        """
        Dapr pub/sub subscriber for fan-out workflow events.

        Subscribes to: kafka-pubsub / fanout-workflow-python
        """
        try:
            # Log the raw request body to debug CloudEvent structure
            raw_body = await request.body()
            logger.info(f"Raw request body: {raw_body.decode('utf-8')}")

            # Parse the CloudEvent
            body_json = await request.json()
            logger.info(f"Parsed JSON body: {body_json}")

            # Extract the data field (which contains our StartWorkflowRequest)
            event_data = body_json.get("data", {})
            logger.info(f"Event data: {event_data}")

            # Parse into our model
            workflow_request = StartWorkflowRequest(**event_data)
            logger.info(f"Parsed workflow request - Id: {workflow_request.Id}, Sleep: {workflow_request.Sleep}, AbortHint: {workflow_request.AbortHint}")

            # Handle error simulation (Sleep == 666)
            if workflow_request.Sleep == 666:
                raise Exception("666")

            # Handle delay simulation
            if workflow_request.Sleep > 0:
                logger.info(f"Sleeping for {workflow_request.Sleep} ms...")
                import asyncio
                await asyncio.sleep(workflow_request.Sleep / 1000.0)
                logger.info("Awake!")

            # Handle abort hint
            if workflow_request.AbortHint:
                return StartWorkflowResponse(
                    Id="",
                    status=workflow_request.AbortHint
                )

            # Generate workflow ID and payload
            import uuid
            workflow_id = workflow_request.Id or str(uuid.uuid4())[:8]
            logger.info(f"Using workflow_id: {workflow_id}")
            random_data = str(uuid.uuid4()).lower()

            workflow_payload = {
                "RandomData": random_data,
                "iterations": 100
            }

            logger.info(f"Starting fan-out workflow {workflow_id} with {workflow_payload['iterations']} iterations")

            # Schedule the workflow
            try:
                result = wf_client.schedule_new_workflow(
                    workflow=fan_out_workflow,
                    input=workflow_payload,
                    instance_id=workflow_id
                )

                return StartWorkflowResponse(
                    Id=result or workflow_id,
                    status=None
                )

            except Exception as ex:
                error_msg = str(ex).lower()
                if "already" in error_msg or "active workflow" in error_msg:
                    logger.error(f"Workflow already running: {workflow_id}")
                    return StartWorkflowResponse(
                        Id=f"{workflow_id} error",
                        status=None
                    )
                raise

        except Exception as e:
            logger.error(f"Error processing fanout-workflow event: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
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
