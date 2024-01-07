import asyncio
import json
import os.path

from aio_pika.abc import AbstractQueue
from pydantic import ValidationError

from entities import RequestQuery, ResponseQuery, RequestUnbagQuery
from pointcloud_handlers import get_axis_swap, get_axiswise_rot, get_conv_ply_xyz, get_height_color, get_unbag
from receive import create_request_queue
from log import logger
from send import send_response_query

handlers = {
    "axis_swap": get_axis_swap,
    "axiswise_rot": get_axiswise_rot,
    "conv_ply_xyz": get_conv_ply_xyz,
    "height_color": get_height_color,
    "unbag": get_unbag
}


async def on_message(message):
    """
    Обработчик сообщений из очереди
    :param message: сообщение из очереди
    :return: None
    """
    async with message.process():
        message_id = message.message_id
        decoded_message_body = message.body.decode()
        data = json.loads(decoded_message_body)
        try:
            result = await processing(data)
            if result:
                send_message = await send_response_query(result[0], message_id)
                if send_message:
                    await message.reject(requeue=True)
            else:
                await message.reject()
        except ValidationError as e:
            logger.error(str(e))
            await message.reject()


async def get_operations(request_query: RequestQuery | RequestUnbagQuery, filename: str) -> ResponseQuery:
    """
    Выполнение операций над облаком точек
    :param request_query: запрос
    :param filename: имя файла
    :return: ответ
    """
    return await loop.run_in_executor(None, handlers.get(request_query.operation_type), request_query, filename)


def correct_request(request_query: RequestQuery | RequestUnbagQuery, waiting_response: ResponseQuery) -> bool:
    """
    Проверка запроса на соответствие ожидаемому ответу
    :param request_query: запрос
    :param waiting_response: ожидаемый ответ
    :return: True, если запрос соответствует ожидаемому ответу, иначе ошибка
    """
    correct_id = request_query.id == waiting_response.id
    correct_type = request_query.operation_type == waiting_response.operation_type
    index_last_slash = waiting_response.file.rfind("/")
    correct_directory = request_query.output_path == waiting_response.file[:index_last_slash]
    if correct_id and correct_type and correct_directory:
        return True
    else:
        raise ValueError("Incorrect query")


async def processing(data: dict) -> bool | tuple[ResponseQuery]:
    """
    Обработка запроса
    :param data: данные запроса
    :return: результат обработки
    """
    request_data = data.get("Входящий request")
    waiting_response = data.get("Ожидаемый response")
    filename = data["Ожидаемый response"]["file"].split("/")[-1]
    if request_data["operation_type"] == "unbag":
        try:
            request_query = RequestUnbagQuery(**request_data)
            waiting_response = ResponseQuery(**waiting_response)
        except ValidationError as e:
            logger.error(str(e))
            return False
        print("Запрос принят: ", request_query.operation_type)
        if not os.path.isdir(request_query.output_path):
            os.makedirs(request_query.output_path)
        task = asyncio.gather(get_operations(request_query, filename))
    else:
        try:
            request_query = RequestQuery(**request_data)
            waiting_response = ResponseQuery(**waiting_response)
        except ValidationError as e:
            logger.error(str(e))
            return False
        print("Запрос принят: ", request_query.operation_type)
        if not os.path.isdir(request_query.output_path):
            os.makedirs(request_query.output_path)
        task = asyncio.gather(get_operations(request_query, filename))
    try:
        correct = False
        try:
            correct = correct_request(request_query, waiting_response)
        except ValueError as e:
            logger.error(str(e))
        if correct:
            result = await task
            print("Результат совпал с ожидаемым response: ", result[0])
            return result
    except Exception as e:
        logger.error(str(e))
        return False


async def main():
    """
    Основная функция
    :return: None
    """
    request_queue: AbstractQueue = await create_request_queue()
    await request_queue.consume(on_message)

if __name__ == '__main__':
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
