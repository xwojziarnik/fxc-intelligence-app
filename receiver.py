import os
import sys
from threading import Thread

from pika.adapters.blocking_connection import BlockingChannel

from settings import settings
from updater import updater_main
from utils import callback_after_receiving_a_message, connect_to_rabbitmq


def receiver_main() -> None:
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
        print("First thread is starting...")
        first_thread: Thread = Thread(target=receiver_main)
        first_thread.start()

        print("Second thread is starting...")
        second_thread: Thread = Thread(target=updater_main)
        second_thread.start()
    except (Exception, KeyboardInterrupt):
        print("Interrupted")
        first_thread.join()
        second_thread.join()
