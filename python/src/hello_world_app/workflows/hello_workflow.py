"""
Simple hello world Dapr workflow.
"""
import logging
from typing import Generator, Any
import dapr.ext.workflow as wf
from ..config import workflow_runtime
from ..activities import say_hello

logger = logging.getLogger(__name__)


@workflow_runtime.workflow(name='hello_workflow')
def hello_workflow(ctx: wf.DaprWorkflowContext, input_data: dict) -> Generator[Any, Any, dict]:
    """
    A simple workflow that generates a greeting message.

    Args:
        ctx: Dapr workflow context
        input_data: Dictionary containing 'name' field

    Returns:
        Dictionary with greeting results
    """
    logger.info(f"Starting hello workflow with input: {input_data}")

    # Call the greeting activity
    greeting_result = yield ctx.call_activity(
        say_hello,
        input=input_data.get("name")
    )

    logger.info(f"Greeting generated: {greeting_result}")

    # Return the result
    return {
        "workflow_id": ctx.instance_id,
        "result": greeting_result,
        "status": "success"
    }
