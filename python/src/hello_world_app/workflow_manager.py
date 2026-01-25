"""
Workflow runtime manager for Dapr workflow lifecycle management.
"""
import logging
import asyncio

logger = logging.getLogger(__name__)


class WorkflowRuntimeManager:
    """
    Manager for the Dapr workflow runtime lifecycle.
    """

    def __init__(self, workflow_runtime):
        self.workflow_runtime = workflow_runtime
        self.is_running = False

    async def start(self):
        """Start the workflow runtime."""
        try:
            logger.info("Starting Dapr workflow runtime")
            self.workflow_runtime.start()

            # Wait a bit for the runtime to initialize
            await asyncio.sleep(2)

            self.is_running = True

            logger.info("Dapr workflow runtime started successfully")

        except Exception as e:
            logger.error(f"Failed to start workflow runtime: {e}")
            raise

    async def stop(self):
        """Stop the workflow runtime."""
        try:
            logger.info("Stopping Dapr workflow runtime")

            self.workflow_runtime.shutdown()
            self.is_running = False

            logger.info("Dapr workflow runtime stopped")

        except Exception as e:
            logger.error(f"Error stopping workflow runtime: {e}")
