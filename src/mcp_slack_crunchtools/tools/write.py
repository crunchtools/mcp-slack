"""Slack messaging tools — send and cancel scheduled messages."""

import os
import time
from typing import Any

from ..client import get_client
from ..models import validate_channel_id


def _get_delay_seconds() -> int:
    """Parse SLACK_ADD_MESSAGE_DELAY into seconds. Default: 3m (180s). Zero disables scheduling."""
    raw = os.environ.get("SLACK_ADD_MESSAGE_DELAY", "3m").strip()
    if raw in ("0", "0s", "none", "false", ""):
        return 0
    if raw.endswith("m"):
        return int(raw[:-1]) * 60
    if raw.endswith("h"):
        return int(raw[:-1]) * 3600
    if raw.endswith("s"):
        return int(raw[:-1])
    return int(raw)


async def send_message(
    channel_id: str,
    text: str,
    thread_ts: str | None = None,
) -> dict[str, Any]:
    """Schedule or immediately post a Slack message.

    When SLACK_ADD_MESSAGE_DELAY > 0 (default 3m), uses chat.scheduleMessage
    and returns a scheduled_message_id for cancellation. When delay is 0,
    uses chat.postMessage and returns the message timestamp.
    """
    channel_id = validate_channel_id(channel_id)
    client = get_client()
    delay = _get_delay_seconds()

    if delay > 0:
        post_at = int(time.time()) + delay
        params: dict[str, Any] = {
            "channel": channel_id,
            "text": text,
            "post_at": str(post_at),
        }
        if thread_ts is not None:
            params["thread_ts"] = thread_ts
        response = await client.api_call("chat.scheduleMessage", params)
        return {
            "scheduled": True,
            "scheduled_message_id": response.get("scheduled_message_id"),
            "channel": response.get("channel"),
            "post_at": post_at,
            "delay_seconds": delay,
        }

    params = {"channel": channel_id, "text": text}
    if thread_ts is not None:
        params["thread_ts"] = thread_ts
    response = await client.api_call("chat.postMessage", params)
    return {
        "scheduled": False,
        "ts": response.get("ts"),
        "channel": response.get("channel"),
    }


async def cancel_scheduled_message(
    channel_id: str,
    scheduled_message_id: str,
) -> dict[str, Any]:
    """Cancel a scheduled Slack message before it sends."""
    channel_id = validate_channel_id(channel_id)
    client = get_client()
    await client.api_call(
        "chat.deleteScheduledMessage",
        {"channel": channel_id, "scheduled_message_id": scheduled_message_id},
    )
    return {"cancelled": True, "scheduled_message_id": scheduled_message_id}
