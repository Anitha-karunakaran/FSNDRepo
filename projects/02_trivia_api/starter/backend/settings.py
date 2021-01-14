from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_HOSTNAME=os.getenv("DATABASE_HOSTNAME")
DATABASE_PORT=os.getenv("DATABASE_PORT")
DATABASE_USER=os.getenv("DATABASE_USER")
DATABASE_PASSWORD=os.getenv("DATABASE_PASSWORD")
