import time
from json import dumps, loads
from typing import Any

from pika import (
    BasicProperties,
    BlockingConnection,
    ConnectionParameters,
    PlainCredentials,
)
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import AMQPConnectionError
from psycopg2 import OperationalError, connect
from psycopg2.extensions import connection, cursor

from settings import settings


def connect_to_postgres(
    username: str, password: str, host: str, port: str, db_name: str
) -> connection:
    attempt_count = 0
    while attempt_count < 10:
        try:
            db_connection: connection = connect(
                dbname=db_name, user=username, password=password, host=host, port=port
            )
            return db_connection
        except OperationalError:
            attempt_count += 1
            print(f"Reconnecting to PostgreSQL, {attempt_count=}")
            time.sleep(2)
    else:
        print("Couldn't connect to PostgreSQL")
        return


def connect_to_rabbitmq(username: str, password: str, host: str, port: str) -> BlockingChannel:
    attempt_count = 0
    while attempt_count < 10:
        try:
            credentials = PlainCredentials(username, password)
            connection = BlockingConnection(
                ConnectionParameters(host=host, port=port, credentials=credentials)
            )
            return connection.channel()
        except AMQPConnectionError:
            attempt_count += 1
            print(f"Reconnecting to RabbitMQ, {attempt_count=}")
            time.sleep(3)
    else:
        print("Couldn't connect to RabbitMQ")
        return


def save_transaction_to_postgres(account_id: int, transaction_amount: int) -> None:
    db_connection: connection = connect_to_postgres(
        username=settings.postgres_db_user,
        password=settings.postgres_db_password,
        db_name=settings.postgres_db_name,
        host=settings.postgres_db_host,
        port=settings.postgres_db_port,
    )
    db_cursor: cursor = db_connection.cursor()
    db_cursor.execute(
        "INSERT INTO historical_transactions (provider_id, transaction_value) VALUES (%s, %s)",
        (account_id, transaction_amount),
    )
    db_connection.commit()
    print(f"Saved transaction: {account_id}, {transaction_amount}")
    db_connection.close()


def update_provider_balance(providers_id: int, amount: int) -> None:
    db_connection: connection = connect_to_postgres(
        username=settings.postgres_db_user,
        password=settings.postgres_db_password,
        db_name=settings.postgres_db_name,
        host=settings.postgres_db_host,
        port=settings.postgres_db_port,
    )
    db_cursor: cursor = db_connection.cursor()
    update_sql_command: str = """ UPDATE initial_data
            SET initial_value = initial_value + %s
            WHERE id = %s"""
    db_cursor.execute(update_sql_command, (amount, providers_id))
    db_connection.commit()
    print(f"Updated balance for id: {providers_id}, with value: {amount}")
    db_connection.close()


def callback_after_receiving_a_message(
    ch: BlockingChannel, method: Any, properties: BasicProperties, body: bytes
):
    data = loads(body.decode("utf-8"))
    print(f" [x] Received {data}")
    account_id = data["id"]
    transaction_amount = data["value"]
    save_transaction_to_postgres(account_id=account_id, transaction_amount=transaction_amount)
    update_provider_balance(providers_id=account_id, amount=transaction_amount)


def prepare_postgres_database_with_initial_data(
    username: str, password: str, db_name: str, host: str, port: str, sql_queries: list[str]
) -> None:
    db_connection: connection = connect_to_postgres(
        username=username,
        password=password,
        db_name=db_name,
        host=host,
        port=port,
    )
    db_cursor = db_connection.cursor()
    for query in sql_queries:
        db_cursor.execute(query)
    db_connection.commit()
    print("DB init complete, starting to produce txs...")
    db_connection.close()


def publish_message_to_rabbitmq_queue(
    channel: BlockingChannel, queue_name: str, id: int, value: int
):
    message = {"id": id, "value": value}
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=dumps(message),
        properties=BasicProperties(
            delivery_mode=2,  # Make message persistent
        ),
    )
    print(f" [x] Sent {message}")
