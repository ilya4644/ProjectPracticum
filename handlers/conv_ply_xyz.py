from entities import *
import pathlib
from pct.utils import convert_ply_to_xyz
import os
import logging


def start(q: Query, filename: str):
    try:
        ply_cloud = pathlib.Path(q.source_dir[0])
        xyz_cloud = convert_ply_to_xyz(ply_cloud)

        if xyz_cloud is None:
            raise ValueError("Error occurred during convert_ply_to_xyz.")

        q.output_dir = f"{q.output_dir}/{filename}.xyz"
        os.rename(str(xyz_cloud), q.output_dir)
        return q.make_response()

    except ValueError as e:
        logging.error(str(e))
        return q.make_response()