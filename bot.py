import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
import aiohttp
from gtts import gTTS
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

# IDs des rôles
RESTRICTED_ROLE_ID = 1301286137293308045
ALLOWED_ROLE_ID = 1289228157827682326
REQUIRED_ROLE_ID = 1289228157827682326

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt.")
    await bot.change_presence(activity=discord.Game(name="debug le patch de UTY"))

    try:
        bot.tree.clear_commands(guild=None)
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes slash : {e}")

# Vérification du rôle pour /lock /unlock
def has_required_role(interaction: discord.Interaction) -> bool:
    return any(role.id == REQUIRED_ROLE_ID for role in interaction.user.roles)

@bot.tree.command(name="lock", description="Verrouille un salon pour un rôle spécifique.")
@app_commands.check(has_required_role)
async def lock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    restricted_role = interaction.guild.get_role(RESTRICTED_ROLE_ID)
    if restricted_role:
        overwrite = channel.overwrites_for(restricted_role)
        overwrite.send_messages = False
        await channel.set_permissions(restricted_role, overwrite=overwrite)

    allowed_role = interaction.guild.get_role(ALLOWED_ROLE_ID)
    if allowed_role:
        overwrite = channel.overwrites_for(allowed_role)
        overwrite.send_messages = True
        await channel.set_permissions(allowed_role, overwrite=overwrite)

    await interaction.response.send_message(f"🔒 {channel.mention} verrouillé pour {restricted_role.name}.")

@bot.tree.command(name="unlock", description="Déverrouille un salon pour un rôle spécifique.")
@app_commands.check(has_required_role)
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    restricted_role = interaction.guild.get_role(RESTRICTED_ROLE_ID)
    if restricted_role:
        overwrite = channel.overwrites_for(restricted_role)
        overwrite.send_messages = True
        await channel.set_permissions(restricted_role, overwrite=overwrite)

    await interaction.response.send_message(f"🔓 {channel.mention} déverrouillé pour {restricted_role.name}.")

@bot.tree.command(name="quote", description="Affiche une citation aléatoire.")
async def quote(interaction: discord.Interaction):
    api_url = "https://api.quotable.io/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                citation = data["content"]
                auteur = data["author"]

                embed = discord.Embed(
                    title="📜 Citation du jour",
                    description=f"\"{citation}\"\n— **{auteur}**",
                    color=discord.Color.blurple()
                )
                embed.set_footer(text="Source : Quotable API")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("❌ Impossible de récupérer une citation.")

@bot.tree.command(name="tts", description="Lit un message à voix haute dans le salon vocal.")
@app_commands.describe(message="Le message à lire.")
async def tts(interaction: discord.Interaction, message: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Tu dois être dans un salon vocal.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel
    try:
        vc = await voice_channel.connect()
    except discord.ClientException:
        vc = interaction.guild.voice_client

    filename = f"tts_{interaction.user.id}.mp3"
    tts = gTTS(text=message, lang='fr')
    tts.save(filename)

    vc.play(discord.FFmpegPCMAudio(source=filename), after=lambda e: os.remove(filename))
    await interaction.response.send_message(f"🔊 Lecture : \"{message}\"")

    while vc.is_playing():
        await asyncio.sleep(1)

    await vc.disconnect()

@bot.tree.command(name="sync", description="Force la resynchronisation des commandes slash.")
async def sync(interaction: discord.Interaction):
    await bot.tree.sync()
    await interaction.response.send_message("✅ Commandes resynchronisées.")

@lock.error
@unlock.error
async def lock_unlock_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser cette commande.", ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
