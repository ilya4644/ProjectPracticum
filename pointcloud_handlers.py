from entities import RequestQuery, ResponseQuery
import pathlib
from pct.utils import rotate_point_cloud_by_axis, swap_point_cloud_file_axes,\
    convert_ply_to_xyz, color_ply_by_height
from pct.ros.io import create_point_cloud_from_bags
import os
from loguru import logger


def get_axis_swap(q: RequestQuery, filename: str):
    try:
        point_cloud = pathlib.Path(q.source_dir[0])
        ax = q.params.get("ax")
        with_ax = q.params.get("with_ax")

        swapped_cloud = swap_point_cloud_file_axes(
            cloud=point_cloud,
            ax=ax,
            with_ax=with_ax,
            in_place=True
        )

        q.output_dir = f"{q.output_dir}/{filename}.ply"
        os.rename(str(swapped_cloud), q.output_dir)
        response = ResponseQuery(q.operation_id, q.operation_type, q.output_dir)
        return response.make_response()
    except ValueError as e:
        logger.error(str(e))


def get_axiswise_rot(q: RequestQuery, filename: str):
    try:
        point_cloud = pathlib.Path(q.source_dir[0])
        ax = q.params.get("ax")
        rad = q.params.get("rad")

        rotated_cloud = rotate_point_cloud_by_axis(
            cloud=point_cloud,
            ax=ax,
            rad=float(rad),
            in_place=True
        )

        q.output_dir = f"{q.output_dir}/{filename}.ply"
        os.rename(str(rotated_cloud), q.output_dir)
        response = ResponseQuery(q.operation_id, q.operation_type, q.output_dir)
        return response.make_response()
    except ValueError as e:
        logger.error(str(e))


def get_conv_ply_xyz(q: RequestQuery, filename: str):
    try:
        ply_cloud = pathlib.Path(q.source_dir[0])
        xyz_cloud = convert_ply_to_xyz(ply_cloud)
        q.output_dir = f"{q.output_dir}/{filename}.xyz"
        os.rename(str(xyz_cloud), q.output_dir)
        response = ResponseQuery(q.operation_id, q.operation_type, q.output_dir)
        return response.make_response()
    except ValueError as e:
        logger.error(str(e))


def get_height_color(q: RequestQuery, filename: str):
    try:
        point_cloud = pathlib.Path(q.source_dir[0])
        height_axis = q.params.get("height_axis")
        colored_cloud = color_ply_by_height(
            cloud=point_cloud,
            height_axis=height_axis,
            in_place=True
        )
        q.output_dir = f"{q.output_dir}/{filename}.ply"
        os.rename(str(colored_cloud), q.output_dir)
        response = ResponseQuery(q.operation_id, q.operation_type, q.output_dir)
        return response.make_response()
    except ValueError as e:
        logger.error(str(e))


async def get_unbag(q: RequestQuery, filename: str):
    try:
        bags = q.source_dir
        bags = [pathlib.Path(bag) for bag in bags]
        output_dir = q.output_dir
        point_cloud = create_point_cloud_from_bags(
            bags=bags,
            in_dir=pathlib.Path(output_dir),
            with_name=filename
        )
        q.output_dir = str(point_cloud)
        response = ResponseQuery(q.operation_id, q.operation_type, q.output_dir)
        return response.make_response()
    except ValueError as e:
        logger.error(str(e))
