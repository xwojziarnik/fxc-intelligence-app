import os
import sys

from pika.adapters.blocking_connection import BlockingChannel

from settings import settings
from utils import callback_after_receiving_a_message, connect_to_rabbitmq


def main() -> None:
    channel: BlockingChannel = connect_to_rabbitmq(
        settings.rabbitmq_user,
        settings.rabbitmq_password,
        settings.rabbitmq_host,
        settings.rabbitmq_port,
    )
    channel.queue_declare(queue=settings.rabbitmq_queue_name, durable=True)
    channel.basic_consume(
        queue=settings.rabbitmq_queue_name,
        auto_ack=True,
        on_message_callback=callback_after_receiving_a_message,
    )
    print(" [*] Receiver is waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
