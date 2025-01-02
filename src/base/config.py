import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or ""
ALGORITHM = os.getenv("ALGORITHM") or ""

def get_config(key: str):
    if(key == "SECRET_KEY"):
        return SECRET_KEY
    elif (key == "ALGORITHM"):
        return ALGORITHM
    else :
        return ""