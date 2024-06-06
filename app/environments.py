import os
from dotenv import load_dotenv
load_dotenv()

LLMODEL = os.getenv("LLMODEL")
LUNA_DEV_KEY = os.getenv("LUNA_DEV_KEY")
JWT_SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_TIME = float(os.getenv("ACCESS_TOKEN_EXPIRE_TIME"))