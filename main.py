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
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hyperlinks.db')
    if not os.path.exists(db_path):
        logging.info("Database does not exist, initializing...")
        init_db(db_path)
    else:
        logging.info("Database already exists, skipping initialization.")

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
