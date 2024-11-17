import os
import sys
from datetime import datetime
from time import sleep
from typing import Optional

import psycopg2
import redis
from psycopg2.extensions import connection, cursor
from redis.client import Redis

from settings import settings
from utils import (
    connect_to_postgres,
    connect_to_redis,
    create_logs_dir,
    get_data_from_postgres_for_updater,
    save_message_to_log_file,
    sleep_until_next_full_minute,
)


def update_account_balances_in_keydb() -> None:
    while True:
        datetime_now: datetime = datetime.now()
        sleep_until_next_full_minute(datetime_now.second)
        key_db_connection: Redis = connect_to_redis("redis://keydb")
        try:
            rows: list[tuple] = get_data_from_postgres_for_updater(
                query="SELECT * FROM initial_data;"
            )
            message: Optional[str] = None
            if rows is not None:
                for row in rows:
                    key_db_connection.set("_".join([str(row[0]), row[1]]), str(row[2]))
                    message = f"Done - {datetime.now()}\n"
            else:
                message = "Rows are empty.."
            save_message_to_log_file("updater_logs/log.txt", message)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


if __name__ == "__main__":
    try:
        create_logs_dir(f"{os.getcwd()}/updater_logs")
        update_account_balances_in_keydb()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
