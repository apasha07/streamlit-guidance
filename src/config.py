from dotenv import find_dotenv, load_dotenv
load_dotenv(dotenv_path=find_dotenv(), override=True)

import os


GUIDANCE_SERVER_URL=os.getenv('GUIDANCE_SERVER_URL')
OPENAI_ORG = os.getenv('OPENAI_ORGANIZATION')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
ENV = os.getenv('ENVIRONMENT', 'dev')
MONGO_CONN_STR = os.getenv('MONGO_CONN_STR')