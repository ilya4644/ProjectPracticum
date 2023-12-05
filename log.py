import sys
from loguru import logger


def start_log(log_file_path='logfile.log'):
    logger.remove()
    logger.add(log_file_path, level="INFO",
               format="<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>{"
                      "level}</level> <cyan>| {name}</cyan> | <level>{message}</level>")
    logger.add(sys.stderr, level="ERROR",
               format="<red>[{time:YYYY-MM-DD HH:mm:ss}] ERROR | {name} | ERROR | {"
                      "message}</red>", filter=lambda record: record["level"].name ==
                                                              "ERROR")
