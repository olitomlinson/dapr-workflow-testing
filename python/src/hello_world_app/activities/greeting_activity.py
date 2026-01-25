"""
Activity for generating greeting messages.
"""
import logging
from datetime import datetime
from dataclasses import dataclass
from ..config import workflow_runtime

logger = logging.getLogger(__name__)


@dataclass
class GreetingRequest:
    """Request object for greeting activities."""
    name: str
    title: str


@dataclass
class GreetingResponse:
    """Response object for greeting activities."""
    greeting: str
    name: str
    timestmap: str 


@workflow_runtime.activity(name='say_hello')
def say_hello(ctx, input_data: str) -> str:
    """
    Activity that generates a personalized greeting.

    Args:
        ctx: Activity context
        input_data: Dictionary with 'name' field

    Returns:
        Dictionary with greeting message and timestamp
    """
    """name = input_data.get("name", "World")"""
    """timestamp = datetime.now().isoformat()"""

    name = input_data

    logger.info(f"Generating greeting for: {name}")

    greeting = f"Hello, {name}! Welcome to Dapr Workflows."

    return greeting


@workflow_runtime.activity(name='say_hello_2')
def say_hello_2(ctx, input_data: str) -> dict:
    """
    Activity that generates a personalized greeting.

    Args:
        ctx: Activity context
        input_data: Dictionary with 'name' field

    Returns:
        Dictionary with greeting message and timestamp
    """
    timestamp = datetime.now().isoformat()

    name = input_data

    logger.info(f"Generating greeting for: {name}")

    greeting = f"Hello, {name}! Welcome to Dapr Workflows."

    return {
        "greeting" : greeting,
        "name" : name,
        "timestmap" : timestamp
        }


@workflow_runtime.activity(name='say_hello_3')
def say_hello_3(_ctx, input_data: dict) -> GreetingResponse:
    """
    Activity that generates a personalized greeting with title.

    Args:
        _ctx: Activity context
        input_data: Dictionary with 'name' and 'title' fields

    Returns:
        GreetingResponse object with greeting message and timestamp
    """
    # Manually construct GreetingRequest from dict
    request = GreetingRequest(
        name=input_data.get("name", ""),
        title=input_data.get("title", "")
    )

    timestamp = datetime.now().isoformat()

    logger.info(f"Generating greeting for: {request.title} {request.name}")

    greeting = f"Hello, {request.title} {request.name}! Welcome to Dapr Workflows."

    return GreetingResponse(
        greeting=greeting,
        name=f"{request.title} {request.name}",
        timestmap=timestamp
    )
