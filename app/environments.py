import os
from dotenv import load_dotenv
load_dotenv()

LLMODEL = os.getenv("LLMODEL")
LUNA_DEV_KEY = os.getenv("LUNA_DEV_KEY")
JWT_SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_TIME = float(os.getenv("ACCESS_TOKEN_EXPIRE_TIME"))
DATABASE_URL = os.getenv("DATABASE_URL")
GRAPH_API_TOKEN = os.getenv("GRAPH_API_TOKEN")
WEBHOOK_WPP_VERIFY_TOKEN = os.getenv("WEBHOOK_WPP_VERIFY_TOKEN")