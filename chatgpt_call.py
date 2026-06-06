import openai
import helper_functions as hf
from PIL import Image
from io import BytesIO
import requests
import logging
import base64

logger = logging.getLogger(__name__)

openai.api_key = hf.OPENAI_KEY


async def generate_sentences_with_word(word, definition, image_prompt=False):
    if image_prompt:
        myPrompt = f"""capture the essence of the following word: '{word}', in the most concise prompt.
        A prompt that can be used to generate a photorealistic image to best represent this word, with the following definition: '{definition}'"""
    else:
        myPrompt = f"Write five sentences using the word '{word}' with this definition: '{definition}' :"

    try:
        response = openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "user",
                    "content": myPrompt
                }
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"An error occurred generating sentences: {e}", exc_info=True)
        return None


async def generate_dalle_image(word, image_path, definition):
    myPrompt = await generate_sentences_with_word(word, definition, True)
    if not myPrompt:
        logger.error("Failed to generate prompt for DALL-E image generation.")
        return None
    logger.info(f"Prompt generated: {myPrompt}")

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=myPrompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="url"
        )
        if not response.data or not response.data[0].url:
            logger.error("No image URL in API response")
            return None
        img_data = requests.get(response.data[0].url).content

        image = Image.open(BytesIO(img_data)).convert("RGB")
        image.save(image_path, "PNG")

        logger.info(f"Image generated and saved to {image_path}")
        return image_path

    except Exception as e:
        logger.error(f"An error occurred generating DALL-E image: {e}", exc_info=True)
        return None


async def generate_gpt_image(word, image_path, definition):
    myPrompt = await generate_sentences_with_word(word, definition, True) 
    if not myPrompt:
        logger.error("Failed to generate prompt for GPT image generation.")
        return None
    logger.info(f"Prompt generated: {myPrompt}")

    try:
        response = openai.images.generate(
            model="gpt-image-2",
            prompt=myPrompt,
            size="1024x1024",
            quality="medium",
        )

        if not response.data or not response.data[0].b64_json:
            logger.error("No image data in API response")
            return None
        img_data = base64.b64decode(response.data[0].b64_json)

        with open(image_path, "wb") as img_file:
            img_file.write(img_data)

        logger.info(f"Image generated and saved to {image_path}")
        return image_path

    except Exception as e:
        logger.error(f"An error occurred generating GPT image: {e}", exc_info=True)
        return None


# Example usage
# word_of_the_day = "quintessential"
# def_of_word = 'representing the most perfect or typical example of a quality or class'
# sentences = generate_sentences_with_word(word_of_the_day, def_of_word)
# print(sentences)
