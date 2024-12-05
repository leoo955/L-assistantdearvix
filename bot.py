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
    # Mettre à jour l'activité du bot
    activity = discord.Game(name="debug le patch de UTY")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel

    # Restreindre l'envoi de messages pour le rôle spécifié
    restricted_role = ctx.guild.get_role(RESTRICTED_ROLE_ID)
    if restricted_role:
        overwrite = channel.overwrites_for(restricted_role)
        overwrite.send_messages = False
        await channel.set_permissions(restricted_role, overwrite=overwrite)

    # Conserver les permissions pour le rôle spécifié
    allowed_role = ctx.guild.get_role(ALLOWED_ROLE_ID)
    if allowed_role:
        overwrite = channel.overwrites_for(allowed_role)
        overwrite.send_messages = True
        await channel.set_permissions(allowed_role, overwrite=overwrite)

    await ctx.send(f"Le salon {channel.mention} a été verrouillé pour le rôle {restricted_role.name}.")

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel

    # Réactiver l'envoi de messages pour le rôle spécifié
    restricted_role = ctx.guild.get_role(RESTRICTED_ROLE_ID)
    if restricted_role:
        overwrite = channel.overwrites_for(restricted_role)
        overwrite.send_messages = True
        await channel.set_permissions(restricted_role, overwrite=overwrite)

    await ctx.send(f"Le salon {channel.mention} a été déverrouillé pour le rôle {restricted_role.name}.")

@bot.command(name='nekii')
async def nekii(ctx):
    global global_nekii_count
    global_nekii_count += 1
    await ctx.send(f"/nekii a été utilisé {global_nekii_count} fois au total.")

    if global_nekii_count >= 200:
        user_to_ban = ctx.guild.get_member(USER_TO_BAN_ID)
        if user_to_ban:
            await ctx.send(f"{user_to_ban.mention} a été banni pour 1 jour pour avoir utilisé /nekii 200 fois.")
            await ctx.guild.ban(user_to_ban, reason="Nekii est banni pour un jour et sa sentence est irrévocable", delete_message_days=1)
        else:
            await ctx.send("L'utilisateur à bannir n'est pas dans le serveur.")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
