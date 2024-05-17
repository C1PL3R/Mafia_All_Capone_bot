import psycopg2
from .config_db import *

with psycopg2.connect(dbname=db_name, user=username, host=host, password=password) as conn:
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                   id BIGINT, 
                   tg_name VARCHAR, 
                   link VARCHAR,
                   role TEXT,
                   killed INT DEFAULT 0,
                   cured INT DEFAULT 0,
                   money INT DEFAULT 0
    )""")

    # new_column_name = 'is_premium'
    # new_column_data_type = 'INTEGER'

    # cursor.execute(f"ALTER TABLE users ADD COLUMN {new_column_name} {new_column_data_type} DEFAULT 0")