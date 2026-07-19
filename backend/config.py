import os
from pymongo import MongoClient
from dotenv import load_dotenv
from db_indexes import ensure_indexes

# Carga variables desde .env (no se versiona - ver .gitignore).
# Fix DEF-001 (secrets:S6694): credenciales fuera del codigo fuente.
load_dotenv()

mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    raise RuntimeError(
        "Falta MONGO_URI. Definela en el archivo .env "
    )

db_name = os.environ.get("MONGO_DB_NAME", "Sureno")
client = MongoClient(mongo_uri)
db = client[db_name]
ensure_indexes(db)
