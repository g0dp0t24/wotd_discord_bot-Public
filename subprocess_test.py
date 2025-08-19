from helper_functions import download_audio_file, convert_mp3_to_mp4
from chatgpt_call import generate_dalle_image
import os


def test_mp4_creation():
    random_word = "inimitable"

        
    mp4_file = rf"D:\Code\wotd_discord_bot\dependencies\{random_word}.mp4"
    try:
        mp3_file_test = download_audio_file(random_word)
        print(f"Audio file downloaded: {mp3_file_test}")
    except Exception as e:
        print(f"Error scraping audio for word '{random_word}': {e}")

    try:
        mp4_file_test = convert_mp3_to_mp4(mp3_file_test, r"D:\Code\wotd_discord_bot\dependencies\audio.png", mp4_file)
        print(f"Video file created: {mp4_file_test}")
    except Exception as e:
        print(f"Error converting audio to video for word '{random_word}': y{e}")

def test_dalle_calls():

    random_word = "inimitable"
    definition = "so good or unusual as to be impossible to copy; unique"
    
    main_dir = os.path.dirname(os.path.abspath(__file__))
    depedencies_folder = os.path.join(main_dir, 'dependencies')

    # mp4_file = os.path.join(depedencies_folder, f"{random_word}.mp4")
    image_path = os.path.join(depedencies_folder, f"{random_word}.png")
    default_image = os.path.join(depedencies_folder, "audio.png")
    print(depedencies_folder)

    try:
        generate_dalle_image(random_word, image_path, definition)
        print("DALL-E image generated successfully!")
    
    except Exception as e:
        print(f"Error generating DALL-E image for word '{random_word}': {e}")   

# command = [
#     r"H:\Software\ffmpeg\bin\ffmpeg.exe",
#     "-version"
# ]

# try:
#     subprocess.run(command, check=True)
#     print("FFmpeg is working correctly!")
# except FileNotFoundError as e:
#     print(f"Error: {e}")
# except subprocess.CalledProcessError as e:
#     print(f"FFmpeg command failed with error: {e}")

# test_mp4_creation()
test_dalle_calls()