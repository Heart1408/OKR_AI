import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase

load_dotenv()

KNOWLEDGE_DB_HOST = os.getenv("KNOWLEDGE_DB_HOST") or  ''
KNOWLEDGE_DB_PORT = os.getenv("KNOWLEDGE_DB_PORT") or  ''
KNOWLEDGE_DB_NAME = os.getenv("KNOWLEDGE_DB_NAME") or  ''
KNOWLEDGE_DB_USERNAME = os.getenv("KNOWLEDGE_DB_USERNAME") or  ''
KNOWLEDGE_DB_PWD = os.getenv("KNOWLEDGE_DB_PWD") or  ''

def get_knowledge_db():
    db = SQLDatabase.from_uri(f"""mysql+mysqlconnector://{KNOWLEDGE_DB_USERNAME}:{KNOWLEDGE_DB_PWD}@{KNOWLEDGE_DB_HOST}:{KNOWLEDGE_DB_PORT}/{KNOWLEDGE_DB_NAME}""")
    return db
