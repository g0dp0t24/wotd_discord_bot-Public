import discord
from discord.ext import commands, tasks
import sheets_api 
from chatgpt_call import generate_sentences_with_word, generate_dalle_image
import helper_functions as hf
import re
import datetime
import os

# Discord bot token
DISCORD_TOKEN = hf.DISCORD_TOKEN 
CHANNEL_ID = hf.CHANNEL_ID 

intents = discord.Intents.default()
intents.messages = True

# Initialize the Discord client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    selected_hyperlink = sheets_api.select_daily_hyperlink()
    await post_hyperlink_data(selected_hyperlink)

def find_closest_date(sheet, target_date):
    sheet_names = sheets_api.get_sheet_names()
    target_date = datetime.datetime.strptime(target_date, "%m/%d/%Y")
    for sheet_name in sheet_names:
        date = sheets_api.get_cell_value(sheet_name, 'B1:B60')
        closest_date = min(date, key=lambda d: abs(datetime.datetime.strptime(d, "%Y-%m-%d") - target_date))
    return date.index(closest_date) + 1

async def wotd(ctx, *, message: str):
    pattern = r'\((.*?)\)'
    match = re.match(pattern, message)

    if not match:
        await ctx.send("❌ Error: Incorrect format! Use `/wotd (word, definition, hyperlink)`")
        return
    
    try:
        content = match.group(1) 
        parts = [p.strip() for p in content.split(',')]
        if len(parts) != 3:
            await ctx.send("❌ Error: Incorrect format! Use `/wotd (word, definition, hyperlink)`")
            return
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
        return

# Function to post the hyperlink data to a Discord channel
async def post_hyperlink_data(hyperlink_data):

    sheet_name, cell, hyperlink, text_value, definition_cell = hyperlink_data[1:6]
    def_list = sheets_api.get_cell_value(sheet_name, definition_cell)
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
    await channel.send(embed=embed)

    audio_path = await hf.download_audio_file(text_value)

    if audio_path:
        try:
            main_dir = os.path.dirname(os.path.abspath(__file__))
            depedencies_folder = os.path.join(main_dir, 'dependencies')
            mp4_file = os.path.join(depedencies_folder, f"{text_value}.mp4")
            image_path = os.path.join(depedencies_folder, f"{text_value}.png")
            default_image = os.path.join(depedencies_folder, "audio.png")
            dalle_image_path = None

            dalle_image_path = await generate_dalle_image(text_value, image_path, definition)

            if not dalle_image_path:
                image_path = default_image
            
            mp4_file = hf.convert_mp3_to_mp4(audio_path, image_path, mp4_file)
            
            if mp4_file and os.path.exists(mp4_file):
                await channel.send(file=discord.File(mp4_file, filename=f"{text_value}_pronunciation.mp4"))
            else:
                print(f"Failed to create MP4 file for {text_value}.")
                return

        finally:
            for file in [audio_path, dalle_image_path, mp4_file]:
                if file and os.path.exists(file):
                    os.remove(file)
                    print(f"🗑️ Removed file: {file}")               

    # await channel.send(message)
    await client.close()

client.run(DISCORD_TOKEN)
