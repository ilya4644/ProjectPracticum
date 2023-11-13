from entities import *
import pathlib
from pct.utils import swap_point_cloud_file_axes
import os
import logging


def start(q: Query, filename: str):
    try:
        point_cloud = pathlib.Path(q.source_dir[0])

        ax = q.params.get("ax")
        with_ax = q.params.get("with_ax")

        if not ax:
            raise ValueError("The 'ax' parameter is missing or empty.")
        if not with_ax:
            raise ValueError("The 'with_ax' parameter is missing or empty.")

        swapped_cloud = swap_point_cloud_file_axes(
            cloud=point_cloud,
            ax=ax,
            with_ax=with_ax,
            in_place=True
        )
        if swapped_cloud is None:
            raise ValueError("Error occurred during swap_point_cloud_file_axes.")

        q.output_dir = f"{q.output_dir}/{filename}.ply"
        os.rename(str(swapped_cloud), q.output_dir)
        return q.make_response()

    except ValueError as e:
        logging.error(str(e))

