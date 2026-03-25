from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()

DB_USERNAME = os.getenv("OUTSTAGRAM_USERNAME", "")
DB_PASSWORD = os.getenv("OUTSTAGRAM_PASSWORD", "")
DB_NAME = os.getenv("OUTSTAGRAM_DBNAME", "outsie")
DB_HOST = os.getenv("OUTSTAGRAM_DBHOST", "localhost")
DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?sslmode=require"

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

for table_name in ['examsection']:
    columns = inspector.get_columns(table_name)
    print(f"Columns for {table_name}: {[c['name'] for c in columns]}")
