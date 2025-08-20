# wotd_discord_bot

Program is created to link an excel document stored in Google Drive, identify the cells that contain a word thats linked with a hyperlink, and posting that word + definition to discord.
Additionally a call to chat GPT will be placed to use the word with the definition attached to request 5 sentances. 
The hyperlink containing the definition of the word will also be sent to discord. 
If audio clip of the word exists in Merriam websters website, then that clip will be downloaded, another request will be made to GPT to create a prompt for this word with the definition in sheets. This prompt will then be sent to Dall-e to create an image. If an image can't be generated, a default image from the dependencies folder will be used for the audio clip and posted as a second message on discord. 

To use all three apps (sheets/discord/OpenAI) you will need to get API keys for all 3. OpenAI and Discord need to be added to the config.json file, and a 'credentials.json' file needs to be created with the information pulled from IAM/service accounts/keys section of your google cloud console. 
