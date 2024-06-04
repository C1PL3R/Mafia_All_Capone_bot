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

    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_panel(
                   creator_id BIGINT,
                   group_id BIGINT,
                   doctor VARCHAR DEFAULT 'Лікар',
                   doctor_text VARCHAR DEFAULT 'Цієї гри ти - Лікар!\nРоби все, щоб врятувати якомога більше мирних людей.', 
                   all_capone VARCHAR DEFAULT 'Аль Капоне',
                   all_capone_text VARCHAR DEFAULT 'Цієї гри ти - Аль Капоне!\nРоби все, щоб твоя сім`я отримала перемогу, над цими нікчемними мирними жителями.', 
                   civilian VARCHAR DEFAULT 'Мирний Житель',
                   civilian_text VARCHAR DEFAULT 'Цієї гри ти - Мирний житель!\nРоби все, щоб знищити підступне угрупування Аль Капоне.'
    )""")

    # new_column_name = 'is_premium'
    # new_column_data_type = 'INTEGER'

    # cursor.execute(f"ALTER TABLE users ADD COLUMN {new_column_name} {new_column_data_type} DEFAULT 0")