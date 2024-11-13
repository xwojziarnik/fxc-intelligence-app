import psycopg2


def postgres_connection(dsn: str):
    return psycopg2.connect(dsn=dsn)
