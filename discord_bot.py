import discord
from discord.ext import tasks
import sheets_api
from chatgpt_call import generate_sentences_with_word, generate_gpt_image
import helper_functions as hf
import datetime
import os
import logging

logger = logging.getLogger(__name__)

DISCORD_TOKEN = hf.DISCORD_TOKEN
CHANNEL_ID = hf.CHANNEL_ID

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

_last_post_date = None
_last_sync_date = None


@tasks.loop(minutes=1)
async def daily_post():
    global _last_post_date
    now = datetime.datetime.now()
    today = now.date()
    if now.hour == 8 and now.minute == 55 and _last_post_date != today:
        _last_post_date = today
        logger.info("Running daily post")
        try:
            selected_hyperlink = sheets_api.select_daily_hyperlink()
            await post_hyperlink_data(selected_hyperlink)
        except Exception as e:
            logger.error(f"Error in daily_post task: {e}", exc_info=True)


@tasks.loop(minutes=1)
async def daily_sync():
    global _last_sync_date
    now = datetime.datetime.now()
    today = now.date()
    if now.hour == 9 and now.minute == 0 and _last_sync_date != today:
        _last_sync_date = today
        logger.info("Running daily DB sync")
        try:
            sheets_api.populate_db()
            logger.info("Daily DB sync complete")
        except Exception as e:
            logger.error(f"Error in daily_sync task: {e}", exc_info=True)


@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")
    if not daily_post.is_running():
        daily_post.start()
    if not daily_sync.is_running():
        daily_sync.start()


async def post_hyperlink_data(hyperlink_data):
    sheet_name, _, hyperlink, text_value, definition_cell = hyperlink_data[1:6]

    def_list = sheets_api.get_cell_value(sheet_name, definition_cell)
    if not def_list:
        logger.error(f"Could not fetch definition for {text_value} at {definition_cell}")
        return
    definition = def_list[0]['values'][0].get('userEnteredValue').get('stringValue')
    gpt_usage = await generate_sentences_with_word(text_value, definition, False)

    embed = discord.Embed(
        color=discord.Colour.dark_red(),
        description=definition,
        title=text_value,
        url=hyperlink
    )
    embed.set_author(name="Word of the day!")
    embed.add_field(name='Example Sentences ', value=gpt_usage)

    channel = client.get_channel(CHANNEL_ID)
    if not isinstance(channel, discord.TextChannel):
        logger.error(f"Channel {CHANNEL_ID} not found or is not a text channel")
        return
    await channel.send(embed=embed)

    audio_path = await hf.download_audio_file(text_value)

    if audio_path:
        main_dir = os.path.dirname(os.path.abspath(__file__))
        dependencies_folder = os.path.join(main_dir, 'dependencies')
        mp4_file = os.path.join(dependencies_folder, f"{text_value}.mp4")
        image_path = os.path.join(dependencies_folder, f"{text_value}.png")
        default_image = os.path.join(dependencies_folder, "audio.png")
        dalle_image_path = None

        try:
            dalle_image_path = await generate_gpt_image(text_value, image_path, definition)

            if not dalle_image_path:
                image_path = default_image

            mp4_file = await hf.convert_mp3_to_mp4(audio_path, image_path, mp4_file)

            if mp4_file and os.path.exists(mp4_file):
                await channel.send(file=discord.File(mp4_file, filename=f"{text_value}_pronunciation.mp4"))
            else:
                logger.error(f"Failed to create MP4 file for {text_value}")

        finally:
            for file in [audio_path, dalle_image_path, mp4_file]:
                if file and os.path.exists(file):
                    os.remove(file)
                    logger.info(f"Removed temp file: {file}")
