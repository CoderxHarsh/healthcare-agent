import psycopg2
import os 
from dotenv import load_dotenv

load_dotenv()
username = os.getenv('PGUSER')
password = os.getenv('PGPASSWORD')
database = os.getenv('PGDATABASE')
host = os.getenv('PGHOST')
port = os.getenv('PGPORT')
try:
    connection = psycopg2.connect(
        user = username,
        password = password,
        dbname = database,
        host = host,
        port = port

    )
    cursor = connection.cursor()
    print("Database connected sucessfully !!")
except Exception as e:
    print(f"Error : {e}")
    exit()