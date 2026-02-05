"""
Fan-out workflow that executes multiple activities in parallel.
"""
import logging
from typing import Generator, Any
from datetime import datetime
import dapr.ext.workflow as wf
from ..config import workflow_runtime
from ..activities import super_slow_activity

logger = logging.getLogger(__name__)


@workflow_runtime.workflow(name='fan_out_workflow')
def fan_out_workflow(ctx: wf.DaprWorkflowContext, input_data: dict) -> Generator[Any, Any, list]:
    """
    A workflow that demonstrates the fan-out pattern by executing multiple
    activities in parallel.

    Args:
        ctx: Dapr workflow context
        input_data: Dictionary containing 'iterations' field

    Returns:
        List of results from all parallel activities
    """
    iterations = input_data.get("iterations", 5)
    logger.info(f"Starting fan-out workflow with {iterations} iterations")

    # Create a list to hold all the activity tasks (fan-out)
    fan_out_tasks = []

    # Schedule all activities in parallel
    for i in range(iterations):
        scheduled_time = datetime.utcnow().strftime("%H:%M:%S")
        message = f"{ctx.instance_id} - super_slow_activity (1) #{i} - scheduled={scheduled_time}"

        # Call activity and add to the task list
        task = ctx.call_activity(
            super_slow_activity,
            input=message
        )
        fan_out_tasks.append(task)

    # Wait for all activities to complete (fan-in)
    logger.info(f"Waiting for {len(fan_out_tasks)} activities to complete")
    results = []
    for task in fan_out_tasks:
        result = yield task
        results.append(result)

    logger.info(f"All {len(results)} activities completed")

    return results
