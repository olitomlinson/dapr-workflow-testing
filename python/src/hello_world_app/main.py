#!/usr/bin/env python3
"""
Main entry point for running the Hello World app with Dapr workflows.

This script demonstrates how to run both the FastAPI web server and Dapr workflow
runtime together in a coordinated manner.
"""
import asyncio
import logging
import os
import signal
import sys

from .web_server import WebServer
from .config import workflow_runtime_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class HelloWorldApp:
    """
    Main application class that coordinates the web server and workflow runtime.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.web_server = WebServer(host=host, port=port)
        self.shutdown_event = asyncio.Event()

    async def start(self):
        """Start all services."""
        try:
            logger.info("Starting Hello World App with Dapr Workflows")

            # Log Dapr environment variables
            logger.info(f"Dapr HTTP Port: {os.getenv('DAPR_HTTP_PORT', 'Not set')}")
            logger.info(f"Dapr GRPC Port: {os.getenv('DAPR_GRPC_PORT', 'Not set')}")

            # Start workflow runtime
            logger.info("Starting Dapr workflow runtime...")
            await workflow_runtime_manager.start()
            logger.info("Dapr workflow runtime started")

            # Start web server
            logger.info("Starting web server...")
            server_task = asyncio.create_task(self._run_server())

            # Wait for shutdown signal
            await self.shutdown_event.wait()

            # Cancel server task
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

        except Exception as e:
            logger.error(f"Error starting services: {e}")
            raise
        finally:
            await self.stop()

    async def _run_server(self):
        """Run the web server in a separate task."""
        import uvicorn

        config = uvicorn.Config(
            app=self.web_server.app,
            host=self.web_server.host,
            port=self.web_server.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def stop(self):
        """Stop all services."""
        try:
            logger.info("Shutting down services...")

            # Stop workflow runtime
            await workflow_runtime_manager.stop()

            logger.info("All services stopped")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_event.set()


async def main():
    """Main entry point with host/port arguments."""
    import argparse

    parser = argparse.ArgumentParser(description="Hello World Dapr Workflow App")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

    args = parser.parse_args()
    app = HelloWorldApp(host=args.host, port=args.port)

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        app.signal_handler(signum, frame)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
