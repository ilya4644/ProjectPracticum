import json
import os
import pathlib

from main import main, is_valid_relative_file_path
# import config

from aio_pika import connect_robust, RobustConnection, IncomingMessage, exceptions
from aio_pika.abc import AbstractChannel, AbstractQueue, DeliveryMode
import asyncio
from log import start_log
import logging


async def check_new_json(data):
    try:
        if not data["Входящий request"]["id"] == data["Ожидаемый response"]["id"]:
            raise ValueError(f"Incoming and expected json IDs are different")

        if not data["Входящий request"]["operation_type"] == data["Ожидаемый response"]["operation_type"]:
            raise ValueError(f"Incoming and expected json operation_type are different")

        file_name = os.path.basename(data["Входящий request"]["file"])
        file_path = data["Ожидаемый response"]["file"]
        if not data["Входящий request"]["output_path"] + f"/{file_name}" == file_path:
            raise ValueError(f"Output_path not contained in file")

        bags = list(data['Входящий request']['files'])
        bags = [pathlib.Path(bag[1::]) for bag in bags]
        for bag in bags:
            await is_valid_relative_file_path(bag)

    except ValueError as e:
        logging.error(str(e))
        await receive_input_response()


async def consume(queue):
    message: IncomingMessage
    async for message in queue:
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
            await check_new_json(data=data)
            await main(name_json, context)


async def receive_input_response():
    try:
        connection: RobustConnection = await connect_robust(
            host="172.17.0.2",
            port=5672,
            login="guest",
            password="guest",
        )
    except exceptions.CONNECTION_EXCEPTIONS as e:
        await asyncio.sleep(3)
        return await receive_input_response()
    async with connection:
        routing_key: str = "input_request_queue"
        channel: AbstractChannel = await connection.channel()
        queue: AbstractQueue = await channel.declare_queue(
            routing_key, durable=True
        )
        while True:
            try:
                await consume(queue=queue)
            except exceptions.CONNECTION_EXCEPTIONS as e:
                return await receive_input_response()
            except Exception as e:
                print(e.args[0])


if __name__ == "__main__":
    start_log('logging.log')
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(receive_input_response())
    loop.run_forever()
