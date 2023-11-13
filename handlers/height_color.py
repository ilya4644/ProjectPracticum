from entities import *
import pathlib
from pct.utils import color_ply_by_height
import os
import logging


def start(q: Query, filename: str):
    try:
        point_cloud = pathlib.Path(q.source_dir[0])

        height_axis = q.params.get("height_axis")

        if not height_axis:
            raise ValueError("The 'height_axis' parameter is missing or empty.")

        colored_cloud = color_ply_by_height(
            cloud=point_cloud,
            height_axis=height_axis,
            in_place=True
        )

        if colored_cloud is None:
            raise ValueError("Error occurred during color_ply_by_height.")

        q.output_dir = f"{q.output_dir}/{filename}.ply"
        os.rename(str(colored_cloud), q.output_dir)
        return q.make_response()

    except ValueError as e:
        logging.error(str(e))
        return q.make_response()
