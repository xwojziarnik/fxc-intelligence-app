import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import psycopg2
import redis
from psycopg2.extensions import connection, cursor

from settings import settings
from utils import connect_to_postgres


def update_account_balances_in_keydb() -> None:
    Path(f"{os.getcwd()}/updater_logs").mkdir(parents=True, exist_ok=True)
    while True:
        datetime_now: datetime = datetime.now()
        seconds_to_wait: int = 60 - datetime_now.second
        print(f"Sleeping for {seconds_to_wait}...")
        sleep(seconds_to_wait)
        print("Woke up!")
        key_db = redis.from_url("redis://keydb")
        print("Connected to redis")
        try:
            db_connection: connection = connect_to_postgres(
                username=settings.postgres_db_user,
                password=settings.postgres_db_password,
                db_name=settings.postgres_db_name,
                host=settings.postgres_db_host,
                port=settings.postgres_db_port,
            )
            db_cursor: cursor = db_connection.cursor()
            db_cursor.execute("SELECT * FROM initial_data;")
            rows = db_cursor.fetchall()
            print(f"\n\n{rows}\n\n")
            message = None
            if rows is not None:
                for row in rows:
                    key_db.set("_".join([str(row[0]), row[1]]), str(row[2]))
                    message = f"Done - {datetime.now()}\n"
            else:
                message = "Rows are empty.."
            with open("updater_logs/log.txt", "a") as file:
                file.write(message)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


if __name__ == "__main__":
    try:
        update_account_balances_in_keydb()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
