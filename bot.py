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
    # Mettre à jour l'activité du bot
    activity = discord.Game(name="debug le patch de UTY")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_message(message):
    if message.attachments:
        directory = load_directory()
        if not directory:
            print("Directory not set or invalid. Please configure 'config.txt'.")
            return
        for attachment in message.attachments:
            if attachment.filename == "data.win":
                file_path = os.path.join(directory, attachment.filename)
                await attachment.save(file_path)
                print(f"File {attachment.filename} saved to {file_path}")

                # Demander à l'utilisateur le chemin du fichier du jeu
                game_directory = input("Please enter the game directory: ")
                if os.path.exists(game_directory):
                    game_file_path = os.path.join(game_directory, "data.win")
                    if os.path.exists(game_file_path):
                        os.remove(game_file_path)
                    os.rename(file_path, game_file_path)
                    print(f"File {attachment.filename} moved to {game_file_path}")
                else:
                    print(f"Game directory {game_directory} does not exist.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))

