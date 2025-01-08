import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive
import aiohttp  # Pour la commande /quote

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

# ID du rôle à restreindre
RESTRICTED_ROLE_ID = 1301286137293308045
# ID du rôle à conserver les permissions
ALLOWED_ROLE_ID = 1289228157827682326

# Compteur global pour suivre le nombre d'utilisations de /nekii
global_nekii_count = 0

@bot.event
async def on_ready():
    print(f"{bot.user} est prêt.")
    await bot.change_presence(activity=discord.Game(name="debug le patch de UTY"))
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes slash : {e}")

# Commande /lock avec description
@bot.tree.command(name="lock", description="Désactive l'envoi de messages pour un rôle spécifique dans un salon")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel

    # Restreindre l'envoi de messages pour le rôle spécifié
    restricted_role = interaction.guild.get_role(RESTRICTED_ROLE_ID)
    if restricted_role:
        overwrite = channel.overwrites_for(restricted_role)
        overwrite.send_messages = False
        await channel.set_permissions(restricted_role, overwrite=overwrite)

    # Conserver les permissions pour le rôle spécifié
    allowed_role = interaction.guild.get_role(ALLOWED_ROLE_ID)
    if allowed_role:
        overwrite = channel.overwrites_for(allowed_role)
        overwrite.send_messages = True
        await channel.set_permissions(allowed_role, overwrite=overwrite)

    await interaction.response.send_message(f"Le salon {channel.mention} a été verrouillé pour le rôle {restricted_role.name}.")

# Commande /unlock avec description
@bot.tree.command(name="unlock", description="Réactive l'envoi de messages pour un rôle spécifique dans un salon")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel

    # Réactiver l'envoi de messages pour le rôle spécifié
    restricted_role = interaction.guild.get_role(RESTRICTED_ROLE_ID)
    if restricted_role:
        overwrite = channel.overwrites_for(restricted_role)
        overwrite.send_messages = True
        await channel.set_permissions(restricted_role, overwrite=overwrite)

    await interaction.response.send_message(f"Le salon {channel.mention} a été déverrouillé pour le rôle {restricted_role.name}.")

# Commande /nekii avec description
@bot.tree.command(name="nekii", description="Compteur d'utilisations de /nekii")
async def nekii(interaction: discord.Interaction):
    global global_nekii_count
    global_nekii_count += 1
    await interaction.response.send_message(f"/nekii a été utilisé {global_nekii_count} fois au total.")

    if global_nekii_count >= 200:
        user_to_ban = interaction.guild.get_member(USER_TO_BAN_ID)
        if user_to_ban:
            await interaction.response.send_message(f"{user_to_ban.mention} a été banni pour 1 jour pour avoir utilisé /nekii 200 fois.")
            await interaction.guild.ban(user_to_ban, reason="Nekii est banni pour un jour et sa sentence est irrévocable", delete_message_days=1)
        else:
            await interaction.response.send_message("L'utilisateur à bannir n'est pas dans le serveur.")

# Commande /quote avec description
@bot.tree.command(name="quote", description="Affiche une citation aléatoire depuis Internet")
async def quote(interaction: discord.Interaction):
    api_url = "https://api.quotable.io/random"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                citation = data["content"]
                auteur = data["author"]

                embed = discord.Embed(
                    title="Citation du jour",
                    description=f"\"{citation}\"\n— **{auteur}**",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Source : Quotable API")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("Désolé, je n'ai pas pu récupérer de citation pour le moment. 😢")

# Lancer le bot
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
