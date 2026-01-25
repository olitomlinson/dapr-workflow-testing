"""
Hello World App with Dapr Workflows

A simple FastAPI application with Dapr workflow integration.
"""

__version__ = "0.1.0"

from .web_server import WebServer, create_app

__all__ = ["WebServer", "create_app"]
