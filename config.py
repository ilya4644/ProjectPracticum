from aio_pika import Connection

connection_config = Connection(
    host="172.17.0.2",
    port=5672,
    login="guest",
    password="guest",
)
