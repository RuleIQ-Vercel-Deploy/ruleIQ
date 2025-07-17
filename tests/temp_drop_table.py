import configparser
from sqlalchemy import create_engine, text

# Read the database URL from alembic.ini
config = configparser.ConfigParser()
config.read('alembic.ini')
db_url = config.get('alembic', 'sqlalchemy.url')

print(f"Connecting to database: {db_url}")

try:
    engine = create_engine(db_url)
    with engine.connect() as connection:
        print("Connection successful. Dropping table...")
        connection.execute(text('DROP TABLE IF EXISTS alembic_version;'))
        connection.commit()
        print("Table 'alembic_version' dropped successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
