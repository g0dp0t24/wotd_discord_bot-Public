import re
import sqlite3
from contextlib import closing
import json
import os
import logging
import requests
from bs4 import BeautifulSoup
import subprocess


logging.basicConfig(filename='data_entryDB.log', 
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependencies', 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

DISCORD_TOKEN = config['DISCORD_TOKEN']
CHANNEL_ID = int(config['DISCORD_CHANNEL_ID'])
SPREADSHEET_ID = config['SPREADSHEET_ID']
OPENAI_KEY = config['OPENAI_KEY']

def a1_to_row_col(cell):
    match = re.match(r"([A-Za-z]+)([0-9]+)", cell)
    if not match:
        raise ValueError(f"Invalid cell reference: {cell}")
    col_str, row_str = match.groups()
    row = int(row_str)
    
    col = 0
    for char in col_str:
        col = col * 26 + (ord(char.upper()) - ord('A')) + 1
    return row, col

def row_col_to_a1(row, col):
    col_str = ""
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        col_str = chr(65 + remainder) + col_str
    return f"{col_str}{row}"

def get_next_cell(cell):
    row, col = a1_to_row_col(cell)
    return row_col_to_a1(row, col + 1)

def reset_used_flags():
    with closing(sqlite3.connect('hyperlinks.db')) as conn, conn, closing(conn.cursor()) as cursor:
        cursor.execute('UPDATE hyperlinks SET used = 0')
        conn.commit()

def log_duplicate(duplicate_word):
    logger.info(f"Duplicate entry deteceted for word: {duplicate_word}")

def log_entrySuccess(newWord_entry):
    logger.info(f"new word detected and added to DB: {newWord_entry}")

async def download_audio_file(word):
    url = f"https://www.merriam-webster.com/dictionary/{word}"
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f"Failed to fetch dictionary page for '{word}'. Status Code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')

    main_entry_section = soup.find('div', {'class': 'entry-attr'})  
    if not main_entry_section:
        print(f"Could not locate the main entry section for {word}.")
        return None

    audio_tag = main_entry_section.find('a', {'class': 'play-pron-v2'})
    logger.info(f"Audio tag found: {audio_tag}")

    if audio_tag and 'data-file' in audio_tag.attrs and 'data-dir' in audio_tag.attrs:
        audio_file = audio_tag['data-file']
        audio_dir = audio_tag['data-dir']
        audio_url = f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{audio_dir}/{audio_file}.mp3"
        logger.info(f"Constructed audio URL: {audio_url}")

        audio_response = requests.get(audio_url)
        if audio_response.status_code == 200:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, 'dependencies', f"{word}_audio.mp3")
            with open(file_path, 'wb') as f:
                f.write(audio_response.content)
                logger.info(f"Successfully downloaded audio file for {word}. Saved as {file_path}.")
            return file_path
        else:
            logger.error(f"Failed to download audio file for '{word}'. Status Code: {audio_response.status_code}")
            return None

def convert_mp3_to_mp4(mp3_file, image_path, mp4_file):

    command = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-i", mp3_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        mp4_file
    ]
    try:
        subprocess.run(command, check=True)
        return mp4_file
    except FileNotFoundError:
        logger.error("ffmpeg not found. Please install ffmpeg.")
        print("ffmpeg not found. Please install ffmpeg.")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg command failed with error: {e}")
        print(f"ffmpeg command failed with error: {e}")
    return None


# reset_used_flags() # run when you want to reset from testing