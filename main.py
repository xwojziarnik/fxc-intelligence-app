"""
Oi, hello, fellow developer!
Of course you can use everything provided in this script to your advantage!
"""

import random
import time

from pika.adapters.blocking_connection import BlockingChannel

from settings import settings
from utils import (
    connect_to_rabbitmq,
    prepare_postgres_database_with_initial_data,
    publish_message_to_rabbitmq_queue,
)


def main() -> None:
    ORG_COUNT: int = 2
    print("Running DB init")

    sql_queries: list[str] = [
        """
            CREATE TABLE IF NOT EXISTS initial_data (
                id SERIAL PRIMARY KEY,
                provider_name VARCHAR(255) NOT NULL,
                initial_value NUMERIC NOT NULL
            );
        """,
        """
            CREATE TABLE IF NOT EXISTS historical_transactions (
                id SERIAL PRIMARY KEY,
                provider_id INTEGER REFERENCES initial_data(id),
                transaction_value NUMERIC NOT NULL
            );
        """,
        """
            INSERT INTO initial_data (provider_name, initial_value) VALUES
            ('Visa', 1000),
            ('Mastercard', 2000)
            ON CONFLICT DO NOTHING;
        """,
        """
            INSERT INTO historical_transactions (provider_id, transaction_value) VALUES
            (1, 100),
            (1, 200),
            (2, -200)
            ON CONFLICT DO NOTHING;
        """,
    ]

    # Prepare Postgres database
    prepare_postgres_database_with_initial_data(
        username=settings.postgres_db_user,
        password=settings.postgres_db_password,
        db_name=settings.postgres_db_name,
        host=settings.postgres_db_host,
        port=settings.postgres_db_port,
        sql_queries=sql_queries,
    )

    # Establish a connection to RabbitMQ
    channel: BlockingChannel = connect_to_rabbitmq(
        username=settings.rabbitmq_user,
        password=settings.rabbitmq_password,
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
    )

    # Declare the queue
    channel.queue_declare(queue=settings.rabbitmq_queue_name, durable=True)

    while True:
        publish_message_to_rabbitmq_queue(
            channel=channel,
            queue_name=settings.rabbitmq_queue_name,
            id=random.randint(1, ORG_COUNT),
            value=random.randint(-1000, 1000),
        )
        time.sleep(random.randint(10, 40))


if __name__ == "__main__":
    main()
