import asyncio

from aio_pika import connect_robust, exceptions
from aio_pika.abc import AbstractChannel, AbstractQueue, AbstractConnection
from dotenv import dotenv_values

from log import logger

config = dotenv_values('.env')


async def create_request_queue() -> AbstractQueue:
    """
    Создание очереди запросов
    :return: очередь запросов
    """
    try:
        connection: AbstractConnection = await connect_robust(
            host=config.get("RABBITMQ_HOST"),
            port=int(config.get("RABBITMQ_PORT")),
            login=config.get("RABBITMQ_LOGIN"),
            password=config.get("RABBITMQ_PASSWORD"),
        )
    except exceptions.CONNECTION_EXCEPTIONS as e:
        logger.error(str(e))
        await asyncio.sleep(3)
        return await create_request_queue()

    routing_key: str = config.get("RABBITMQ_REQUEST_QUEUE")
    try:
        channel: AbstractChannel = await connection.channel()
        queue: AbstractQueue = await channel.get_queue(
            routing_key
        )
    except exceptions.ChannelNotFoundEntity:
        channel: AbstractChannel = await connection.channel()
        queue: AbstractQueue = await channel.declare_queue(
            routing_key, durable=True
        )

    return queue
