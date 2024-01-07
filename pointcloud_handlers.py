import os
import pathlib

from entities import RequestQuery, ResponseQuery, RequestUnbagQuery
from pct.utils import rotate_point_cloud_by_axis, swap_point_cloud_file_axes, \
    convert_ply_to_xyz, color_ply_by_height
from pct.ros.io import create_point_cloud_from_bags
from log import logger


def get_axis_swap(query: RequestQuery, filename: str) -> ResponseQuery:
    """
    Обработчик запроса на перестановку осей
    :param query: запрос
    :param filename: имя файла
    :return: ответ
    """
    try:
        point_cloud = pathlib.Path(query.file)
        ax = query.params.get("ax")
        with_ax = query.params.get("with_ax")

        swapped_cloud = swap_point_cloud_file_axes(
            cloud=point_cloud,
            ax=ax,
            with_ax=with_ax,
            in_place=True
        )

        os.rename(str(swapped_cloud), query.output_path + filename)
        response_data = {
            "id": query.id,
            "operation_type": query.operation_type,
            "file": query.output_path
        }
        response = ResponseQuery(**response_data)
        return response
    except ValueError as e:
        logger.error(str(e))


def get_axiswise_rot(query: RequestQuery, filename: str) -> ResponseQuery:
    """
    Обработчик запроса на поворот облака точек
    :param query: запрос
    :param filename: имя файла
    :return: ответ
    """
    try:
        point_cloud = pathlib.Path(query.file)
        ax = query.params.get("ax")
        rad = query.params.get("rad")

        rotated_cloud = rotate_point_cloud_by_axis(
            cloud=point_cloud,
            ax=ax,
            rad=float(rad),
            in_place=True
        )

        os.rename(str(rotated_cloud), query.output_path + filename)
        response_data = {
            "id": query.id,
            "operation_type": query.operation_type,
            "file": query.output_path
        }
        response = ResponseQuery(**response_data)
        return response
    except ValueError as e:
        logger.error(str(e))


def get_conv_ply_xyz(query: RequestQuery, filename: str) -> ResponseQuery:
    """
    Обработчик запроса на конвертацию из ply в xyz
    :param query: запрос
    :param filename: имя файла
    :return: ответ
    """
    try:
        ply_cloud = pathlib.Path(query.file)
        xyz_cloud = convert_ply_to_xyz(ply_cloud)
        os.rename(str(xyz_cloud), query.output_path + filename)
        response_data = {
            "id": query.id,
            "operation_type": query.operation_type,
            "file": query.output_path
        }
        response = ResponseQuery(**response_data)
        return response
    except ValueError as e:
        logger.error(str(e))


def get_height_color(query: RequestQuery, filename: str) -> ResponseQuery:
    """
    Обработчик запроса на окраску облака точек по высоте
    :param query: запрос
    :param filename: имя файла
    :return: ответ
    """
    try:
        point_cloud = pathlib.Path(query.file)
        height_axis = query.params.get("height_axis")
        color_ply_by_height(
            cloud=point_cloud,
            height_axis=height_axis,
            in_place=True
        )
        os.rename(str(point_cloud), query.output_path + filename)
        response_data = {
            "id": query.id,
            "operation_type": query.operation_type,
            "file": query.output_path
        }
        response = ResponseQuery(**response_data)
        return response
    except ValueError as e:
        logger.error(str(e))


def get_unbag(query: RequestUnbagQuery, filename: str) -> ResponseQuery:
    """
    Обработчик запроса на конвертацию из bag
    :param query: запрос
    :param filename: имя файла
    :return: ответ
    """
    try:
        bag_files = query.files
        output_path = query.output_path
        create_point_cloud_from_bags(
            bags=bag_files,
            in_dir=output_path,
            with_name=filename
        )
        response_data = {
            "id": query.id,
            "operation_type": query.operation_type,
            "file": output_path
        }
        response = ResponseQuery(**response_data)
        return response
    except ValueError as e:
        logger.error(str(e))
