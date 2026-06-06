import logging, os
from logging.handlers import RotatingFileHandler
from database import init_db


def setup_logging():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(script_dir, 'data_entryDB.log')

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(name)s] %(message)s',
        handlers=[file_handler],
        force=True
    )


if __name__ == '__main__':
    setup_logging()
    init_db()
    from discord_bot import client, DISCORD_TOKEN
    client.run(DISCORD_TOKEN)
