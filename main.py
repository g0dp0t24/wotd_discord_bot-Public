import discord_bot
import schedule
import time
import logging


logging.basicConfig(filename='data_entryDB.log', 
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def setup_scheduler():
    schedule.every().day.at("08:55").do(discord_bot.on_ready())

    while True:
        schedule.run_pending()
        time.sleep(45)

def main():
    discord_bot.on_ready()
    # setup_scheduler()

if __name__ == '__main__':
    main()