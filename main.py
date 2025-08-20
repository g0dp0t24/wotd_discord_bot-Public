import discord_bot
import schedule
import time
import logging
import os
from database import init_db


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "hyperlinks.db")

logging.basicConfig(filename='data_entryDB.log', 
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_db():
    if not os.path.isfile(DB_PATH):
        logging.info("No database found. Initializing...")
        init_db()
    else:
        logging.info("Database exists at %s", DB_PATH)  

def setup_scheduler():
    schedule.every().day.at("08:55").do(discord_bot.on_ready())

    while True:
        schedule.run_pending()
        time.sleep(45)

def main():
    ensure_db()
    discord_bot.on_ready()
    # setup_scheduler()

if __name__ == '__main__':
    main()
