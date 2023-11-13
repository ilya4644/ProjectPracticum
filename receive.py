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

        input_path = data['Входящий request']['output_path'][1:].split('/')
        output_path = data['Ожидаемый response']['file'][1:].split('/')
        if input_path != output_path[:len(input_path)]:
#        file_name = os.path.basename(data["Входящий request"]["file"])
#        file_path = data["Ожидаемый response"]["file"]
#        if not data["Входящий request"]["output_path"] + f"/{file_name}" == file_path:
            raise ValueError(f"Output_path not contained in file")

        if data['Входящий request']['operation_type'] == 'unbag':
            bags = list(data['Входящий request']['files'])
            bags = [pathlib.Path(bag) for bag in bags]
            for bag in bags:
                await is_valid_relative_file_path(bag)
        else:
            bag = pathlib.Path(data['Входящий request']['file'])
            await is_valid_relative_file_path(bag)

    except ValueError as e:
        logging.error(str(e))
        await receive_input_response(flag=True)


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
            await check_new_json(data=data)
            await main(name_json, context)


async def receive_input_response(flag: bool = False):
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
        try:
            channel: AbstractChannel = await connection.channel()
            queue: AbstractQueue = await channel.get_queue(routing_key)
        except aiormq.exceptions.ChannelNotFoundEntity:
            channel: AbstractChannel = await connection.channel()
            queue: AbstractQueue = await channel.declare_queue(
                    routing_key, durable=True
                    )
        while True:
            await consume(channel=channel, queue=queue, flag=flag)
            await asyncio.sleep(3)


if name == "main":
    start_log('logging.log')
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(receive_input_response())
    loop.run_forever()