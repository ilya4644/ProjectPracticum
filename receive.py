import json
from aio_pika import connect_robust, RobustConnection, IncomingMessage, exceptions
from aio_pika.abc import AbstractChannel, AbstractQueue, DeliveryMode
import asyncio
from log import start_log
from main import main
from dotenv import load_dotenv
import os


async def consume(channel, queue, flag: bool):
    #    message: IncomingMessage
    async for message in queue:
        if flag:
            print(message.delivery_tag)
            await message.basic_ack()
            flag = False
        async with message.process():
            context = {
                "service_name": message.app_id,
                "task_id": message.message_id,
            }
            decoded_message_body = message.body.decode()
            data = json.loads(decoded_message_body)
            name_json: str = data["Входящий request"]["id"]
            with open(f"{name_json}.json", "w+") as file:
                file.write(decoded_message_body)
            await main(name_json, context)


async def receive_input_response(flag: bool = False):
    try:
        load_dotenv()
        connection: RobustConnection = await connect_robust(
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            login=os.getenv("LOGIN"),
            password=os.getenv("PASSWORD")
        )
    except exceptions.CONNECTION_EXCEPTIONS as e:
        await asyncio.sleep(3)
        return await receive_input_response()
    async with connection:
        routing_key: str = "input_request_queue"
        try:
            channel: AbstractChannel = await connection.channel()
            queue: AbstractQueue = await channel.get_queue(routing_key)
        except aiormq.exceptions.ChannelNotFoundEntity:
            channel: AbstractChannel = await connection.channel()
            queue: AbstractQueue = await channel.declare_queue(
                routing_key, durable=True
            )
        await consume(channel=channel, queue=queue, flag=flag)
        while True:
            await asyncio.sleep(3)


if __name__ == "__main__":
    start_log('logging.log')
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(receive_input_response())
    loop.run_forever()
