import asyncio
import json
from typing import Optional
#import config

from aio_pika import connect_robust, RobustConnection, Message
from aio_pika.abc import AbstractChannel, DeliveryMode


async def create_message(
        output_json: bytes,
        message_id: Optional[str] = None,
        receive_message_id: Optional[str] = None
):
    return Message(
        body=output_json,
        content_type="application/json",
        content_encoding="utf-8",
        message_id=message_id or None,
        delivery_mode=DeliveryMode.PERSISTENT,
reply_to=receive_message_id or None
)


async def send_output_response(
        output_json: Optional[dict[str, str]] = None,
        receive_message_id: Optional[str] = None
):
    connection: RobustConnection = await connect_robust(
        host="172.17.0.2",
        port=5672,
        login="guest",
        password="guest",
    )

    async with connection:
        routing_key: str = "output_response_queue"
        channel: AbstractChannel = await connection.channel()
        message: Message = await create_message(
            output_json=json.dumps(output_json, indent=2).encode('utf-8'),
            receive_message_id=receive_message_id
        )
        await channel.default_exchange.publish(
            message,
            routing_key=routing_key
        )


if __name__ == "__main__":
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    loop.run_until_complete(send_output_response())
    loop.close()