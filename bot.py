import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="/", intents=intents)

def load_directory():
    if os.path.exists("config.txt"):
        with open("config.txt", "r") as file:
            directory = file.readline().strip()
            if os.path.exists(directory):
                return directory
    return None

def save_file(directory, attachment):
    file_path = os.path.join(directory, attachment.filename)
    attachment.save(file_path)

@bot.event
async def on_ready():
    print(f"{bot.user} is ready.")

@bot.event
async def on_message(message):
    if message.attachments:
        directory = load_directory()
        if not directory:
            print("Directory not set or invalid. Please configure 'config.txt'.")
            return
        for attachment in message.attachments:
            file_path = os.path.join(directory, attachment.filename)
            await attachment.save(file_path)
            print(f"File {attachment.filename} saved to {file_path}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
