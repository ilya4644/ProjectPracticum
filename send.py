import asyncio

from aio_pika import connect_robust, exceptions, Message
from aio_pika.abc import AbstractConnection, AbstractChannel
from dotenv import dotenv_values

from entities import ResponseQuery
from log import logger


config = dotenv_values('.env')


async def create_message(response_query: ResponseQuery, message_id: str) -> Message:
    """
    Создание сообщения
    :param response_query: ответ на запрос
    :param message_id: идентификатор сообщения
    :return: сообщение
    """
    return Message(
        body=response_query.model_dump_json().encode('utf-8'),
        content_type="application/json",
        content_encoding="utf-8",
        message_id=message_id,
        delivery_mode=2
    )


async def send_response_query(response_query: ResponseQuery, message_id: str) -> bool:
    """
    Отправка ответа на запрос
    :param response_query: ответ на запрос
    :param message_id: идентификатор сообщения
    :return: True, если сообщение не отправлено, иначе False
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
        return await send_response_query(response_query, message_id)
    async with connection:
        routing_key: str = config.get("RABBITMQ_RESPONSE_QUEUE")
        channel: AbstractChannel = await connection.channel()
        message: Message = await create_message(response_query, message_id)
        try:
            await channel.default_exchange.publish(
                message,
                routing_key=routing_key
            )
            return False
        except exceptions.ChannelNotFoundEntity:
            await channel.declare_queue(
                routing_key, durable=True
            )
            await channel.default_exchange.publish(
                message,
                routing_key=routing_key
            )
            return False
        except Exception as e:
            logger.error(str(e))
            return True
