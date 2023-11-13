from entities import *
import pathlib
from pct.utils import rotate_point_cloud_by_axis
import os
import logging


def start(q: Query, filename: str):
    try:
        point_cloud = pathlib.Path(q.source_dir[0])

        ax = q.params.get("ax")
        rad = q.params.get("rad")

        if not ax:
            raise ValueError("The 'ax' parameter is missing or empty.")
        if not rad:
            raise ValueError("The 'rad' parameter is missing or empty.")

        rotated_cloud = rotate_point_cloud_by_axis(
            cloud=point_cloud,
            ax=ax,
            rad=float(rad),
            in_place=True
        )

        if rotated_cloud is None:
            raise ValueError("Error occurred during rotate_point_cloud_by_axis.")

        q.output_dir = f"{q.output_dir}/{filename}.ply"
        os.rename(str(rotated_cloud), q.output_dir)
        return q.make_response()

    except ValueError as e:
        logging.error(str(e))
        return q.make_response()