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

# ID du salon spécifique
TARGET_CHANNEL_ID = 1301938008232034477

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

@bot.command(name='install')
async def install(ctx):
    # Vérifier si la commande est exécutée dans le salon spécifique
    if ctx.channel.id != TARGET_CHANNEL_ID:
        await ctx.send("Cette commande ne peut être exécutée que dans le salon spécifique.")
        return

    await ctx.send("Veuillez télécharger le fichier `data.win` ici.")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and message.attachments

    message = await bot.wait_for('message', check=check)
    directory = load_directory()
    if not directory:
        await ctx.send("Le répertoire n'est pas défini ou est invalide. Veuillez configurer 'config.txt'.")
        return

    for attachment in message.attachments:
        if attachment.filename == "data.win":
            file_path = os.path.join(directory, attachment.filename)
            await attachment.save(file_path)
            await ctx.send(f"Fichier `{attachment.filename}` enregistré dans `{file_path}`")

            # Demander à l'utilisateur le chemin du fichier du jeu
            await ctx.send("Veuillez entrer le répertoire du jeu :")

            def check_directory(message):
                return message.author == ctx.author and message.channel == ctx.channel

            game_directory_message = await bot.wait_for('message', check=check_directory)
            game_directory = game_directory_message.content
            if os.path.exists(game_directory):
                game_file_path = os.path.join(game_directory, "data.win")
                if os.path.exists(game_file_path):
                    os.remove(game_file_path)
                os.rename(file_path, game_file_path)
                await ctx.send(f"Fichier `{attachment.filename}` déplacé vers `{game_file_path}`")
            else:
                await ctx.send(f"Le répertoire du jeu `{game_directory}` n'existe pas.")
        else:
            await ctx.send(f"Fichier `{attachment.filename}` n'est pas `data.win`.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))

