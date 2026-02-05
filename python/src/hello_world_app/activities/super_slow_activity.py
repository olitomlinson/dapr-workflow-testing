"""
Activity that simulates a slow/long-running operation.
"""
import logging
import asyncio
from datetime import datetime
from ..config import workflow_runtime

logger = logging.getLogger(__name__)


@workflow_runtime.activity(name='super_slow_activity')
def super_slow_activity(ctx, input_data: str) -> str:
    """
    Activity that simulates a slow operation with a 60-second delay.

    Args:
        ctx: Activity context
        input_data: Message string to process

    Returns:
        String with the message and timestamps for activation and completion
    """
    activated_time = datetime.utcnow().strftime("%H:%M:%S")
    message = f"{input_data} activated={activated_time}"

    logger.info(message)

    # Simulate slow operation (60 seconds)
    import time
    time.sleep(60)

    finished_time = datetime.utcnow().strftime("%H:%M:%S")
    message += f" finished={finished_time}"

    logger.info(message)

    return message
