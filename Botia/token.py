from huggingface_hub import HfApi
import os
from dotenv import load_dotenv

load_dotenv()
api = HfApi()
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
me = api.whoami(token=token)
print(me)
