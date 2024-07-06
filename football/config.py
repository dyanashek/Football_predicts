import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
MANAGER_ID = os.getenv('MANAGER_ID')
MANAGER_USERNAME = os.getenv('MANAGER_USERNAME')

CHANNEL_LINK = 'https://t.me/WildBoost_app'
CHANNEL_ID = '-1001721715180'

PER_PAGE = 1
TIME_DELTA = 4