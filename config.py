import os
from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN", "")
COC_API_TOKEN = os.getenv("COC_API_TOKEN", "")
CLAN_TAG = os.getenv("CLAN_TAG", "")
