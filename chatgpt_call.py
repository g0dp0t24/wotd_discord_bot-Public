import openai
import helper_functions as hf
from PIL import Image
from io import BytesIO
import requests
import logging


openai.api_key = hf.OPENAI_KEY 

async def generate_sentences_with_word(word, definition, image_prompt=False):
    if image_prompt:
        myPrompt = f"""capture the essence of the following word: '{word}', in the most concise prompt.  
        A prompt that can be used to generate a vivid image to best represent this word, with the following definition: '{definition}'"""
    else:
        myPrompt = f"Write five sentences using the word '{word}' with this definition: '{definition}' :"

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {
                    "role" : "user",
                    "content" : myPrompt
                }
            ],

        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def generate_dalle_image(word, image_path, definition):
    myPrompt = await generate_sentences_with_word(word, definition, True)
    logging.info(f"Prompt generated: {myPrompt}")
    
    try:
        response = openai.images.generate(
            model="dall-e-3",  
            prompt=myPrompt,
            size="1024x1024",
            quality="standard",
            n=1,
            # style= "natural",
            response_format="url"
            )
        image_url = response.data[0].url
        img_data = requests.get(image_url).content

        image = Image.open(BytesIO(img_data)).convert("RGB")
        image.save(image_path, "PNG")
        
        print(f"Image generated and saved as PNG to {image_path}")
        return image_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Example usage
# word_of_the_day = "quintessential"  
# def_of_word = 'representing the most perfect or typical example of a quality or class'
# sentences = generate_sentences_with_word(word_of_the_day, def_of_word)
# print(sentences)