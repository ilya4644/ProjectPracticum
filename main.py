import os.path
import sys

import asyncio
from typing import Optional

import send
from handlers import unbag, axiswise_rot, axis_swap, conv_ply_xyz, height_color
from entities import *
import json
import logging
from jsondiff import diff


async def is_valid_relative_file_path(relative_file_path):
    cwd = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(cwd, relative_file_path)
    if not os.path.isfile(file_path):
        raise ValueError(f"The path {file_path} does not exist or is not a file.")


async def unpack_query(data: dict):
    try:
        result_query = Query(operation_id=data['id'],
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
            if not data['files']:
                raise ValueError(f"The 'file' parameter is missing or empty.")
            else:
                result_query.source_dir += [data['file']]
        else:
            sys.exit("Wrong operation type")
        return result_query
    except ValueError as e:
        logging.error(str(e))
        from receive import receive_input_response
        await receive_input_response()


async def exec_handler(q: Query, filename: str):
    match q.operation_type:
        case "unbag":
            return await unbag.start(q, filename)
        case "conv_ply_xyz":
            return await conv_ply_xyz.start(q, filename)
        case "height_color":
            return await height_color.start(q, filename)
        case "axis_swap":
            return await axis_swap.start(q, filename)
        case "axiswise_rot":
            return await axiswise_rot.start(q, filename)


async def get_json_diif(expected_output_response, differences):
    for key, value in differences.items():
        path = key
        if value is not None:
            raise ValueError(f"Expected: '{path}': {expected_output_response[f'{path}']}, Actual: {value}")
        else:
            raise ValueError(f"Expected: '{path}': {expected_output_response[f'{path}']}, but the parameter is missing")


async def main(name_json: Optional[str] = None, context: Optional = None):
    try:
        query_file = open(f"{name_json}.json", "r", encoding="utf-8")
        all_data = json.load(query_file)
        input_request = all_data['Входящий request']
        expected_output_response = dict(all_data["Ожидаемый response"])
        query = await unpack_query(input_request)
        print("Запрос принят: ", query.operation_type)
        if not os.path.isdir(query.output_dir):
            os.makedirs(query.output_dir)
        filename = expected_output_response["file"][len(query.output_dir) + 1:-4]
        await is_valid_relative_file_path(expected_output_response["file"])
        handler_result = await exec_handler(query, filename)
        differences = diff(expected_output_response, handler_result)
        if not differences:
            print("Результат совпал с ожидаемым response: ", handler_result)
            await send.send_output_response(
                output_json=handler_result,
                receive_message_id=context["task_id"]
            )
        else:
            await get_json_diif(expected_output_response, differences)
    except ValueError as e:
        logging.error(str(e))
        from receive import receive_input_response
        await receive_input_response()


if __name__ == "__main__":
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    loop.close()
