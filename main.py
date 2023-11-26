import os.path
import sys
import asyncio
from typing import Optional
import pathlib
import send
from log import start_log
from pointcloud_handlers import get_unbag, get_axis_swap, \
    get_axiswise_rot, get_height_color, get_conv_ply_xyz
from entities import *
import json
from loguru import logger
from jsondiff import diff


async def is_valid_relative_file_path(relative_file_path: str):
    cwd = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(cwd, relative_file_path)
    if not os.path.isfile(file_path):
        raise ValueError(f"The path {file_path} does not exist or is not a file.")


async def check_new_json(data: dict):
    try:
        if (not data["Входящий request"]["id"] == data["Ожидаемый response"]["id"]
                and data["Входящий request"]["id"] is not None):
            raise ValueError(f"Incoming and expected json IDs are different")

        if (not data["Входящий request"]["operation_type"] == data["Ожидаемый response"]["operation_type"]
                and data["Входящий request"]["operation_type"] is not None):
            raise ValueError(f"Incoming and expected json operation_type are different")

        input_path = data['Входящий request']['output_path'][1:].split('/')
        output_path = data['Ожидаемый response']['file'][1:].split('/')
        if input_path != output_path[:len(input_path)]:
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
        logger.error(str(e))
        from receive import receive_input_response
        await receive_input_response()


async def get_json_diff(expected_output_response: dict, differences: dict):
    for key, value in differences.items():
        path = key
        if value is not None:
            raise ValueError(f"Expected: '{path}': {expected_output_response[f'{path}']}, Actual: {value}")
        else:
            raise ValueError(f"Expected: '{path}': {expected_output_response[f'{path}']}, but the parameter is missing")


async def unpack_query(data: dict):
    try:
        result_query = RequestQuery(operation_id=data['id'],
                                    operation_type=data['operation_type'],
                                    source_dir=[],
                                    output_dir=data['output_path'],
                                    params=data['params'])
        if result_query.operation_type == "unbag":
            if not data['files']:
                raise ValueError(f"The 'file' parameter is missing or empty.")
            else:
                result_query.source_dir = list(data['files'])
        elif result_query.operation_type in ("conv_ply_xyz", "height_color", "axis_swap", "axiswise_rot"):
            if not data['file']:
                raise ValueError(f"The 'file' parameter is missing or empty.")
            else:
                result_query.source_dir += [data['file']]
        else:
            sys.exit("Wrong operation type")
        return result_query
    except ValueError as e:
        logger.error(str(e))
        from receive import receive_input_response
        await receive_input_response()


async def exec_handler(q: RequestQuery, filename: str):
    async def execute_task(func):
        return await func(q, filename)

    match q.operation_type:
        case "unbag":
            return await asyncio.create_task(execute_task(get_unbag(q, filename)))
        case "conv_ply_xyz":
            return await asyncio.create_task(execute_task(get_conv_ply_xyz(q, filename)))
        case "height_color":
            return await asyncio.create_task(execute_task(get_height_color(q, filename)))
        case "axis_swap":
            return await asyncio.create_task(execute_task(get_axis_swap(q, filename)))
        case "axiswise_rot":
            return await asyncio.create_task(execute_task(get_axiswise_rot(q, filename)))


async def main(name_json: Optional[str] = None, context: Optional = None):
    try:
        query_file = open(f"{name_json}.json", "r", encoding="utf-8")
        all_data = json.load(query_file)
        await check_new_json(all_data)
        input_request = all_data['Входящий request']
        expected_output_response = dict(all_data["Ожидаемый response"])
        query = await unpack_query(input_request)
        print("Запрос принят: ", query.operation_type)
        if not os.path.isdir(query.output_dir):
            os.makedirs(query.output_dir)
        filename = expected_output_response["file"][len(query.output_dir) + 1:-4]
        handler_result = await exec_handler(query, filename)
        differences = diff(expected_output_response, handler_result)
        if not differences:
            print("Результат совпал с ожидаемым response: ", handler_result)
            await send.send_output_response(
                output_json=handler_result,
                receive_message_id=context["task_id"]
            )
        else:
            await get_json_diff(expected_output_response, differences)
    except ValueError as e:
        logger.error(str(e))
        from receive import receive_input_response
        await receive_input_response()


if __name__ == "__main__":
    start_log('logging.log')
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
