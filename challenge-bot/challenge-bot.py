import os
from dotenv import load_dotenv
import discord
import responses
from flask_app import startFlask

# Loads the .env file that resides on the same level as the script.
load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.
intents=discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@bot.event
async def on_ready():
	startFlask()#start up the Webserver that is used for retrieving Strava auth
	print(f'{bot.user} is now running!')

# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@bot.event
async def on_message(message):
	#checks if the message is from the bot
	if message.author == bot.user:
		return
	
	username = str(message.author)
	user_message = str(message.content)
	channel = str(message.channel)
	print(f"{username} said : '{user_message}' ({channel})")
	
	try:
		response = responses.handle_response(user_message)
		if(response):
			await message.channel.send(response)
	except Exception as e:
		print(e)
	

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)