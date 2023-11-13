from entities import *
import pathlib
from pct.ros.io import create_point_cloud_from_bags
import logging


async def start(q: Query, filename: str):
    try:
        bags = q.source_dir
        bags = [pathlib.Path(bag) for bag in bags]
        output_dir = q.output_dir

        point_cloud = create_point_cloud_from_bags(
            bags=bags,
            in_dir=pathlib.Path(output_dir),
            with_name=filename
        )

        if point_cloud is None:
            raise ValueError("Error occurred during create_point_cloud_from_bags.")

        q.output_dir = str(point_cloud)
        return await q.make_response()

    except ValueError as e:
        logging.error(str(e))
        return q.make_response()