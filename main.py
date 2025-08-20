# This example requires the 'members' and 'message_content' privileged intents to function.

import discord
from discord.ext import commands
import random

user_warnings = {}

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')


@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not cool')


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')


@bot.command()
async def ping(ctx):
    """Calculates bot latency."""
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f'Pong XD!! 🦤 Latency: {latency_ms}ms')


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: str):
    if amount.lower() == 'all':
        await ctx.channel.purge()
        await ctx.send("All messages cleared XD!!! 🗑️", delete_after=5)
    else:
        try:
            amount = int(amount)
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(f'{amount} messages cleared! ✅', delete_after=5)
        except ValueError:
            await ctx.send('Please provide a valid number or "all".', delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):    
    await ctx.send(f'Kicking {member.mention}...')
    await member.kick(reason=reason)
    await ctx.send(f'{member.name} has been kicked from the server. Reason: {reason or "None"}.')


import discord
from discord.ext import commands

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    ban_embed = discord.Embed(
        title="🚫 Usuario Baneado",
        description=f"**{member.name}** ha sido baneado del servidor.",
        color=discord.Color.dark_red()
    )
    ban_embed.add_field(name="Razón", value=reason or "No se proporcionó una razón.", inline=False)
    ban_embed.set_footer(text=f"Banearon a {member.name} por {ctx.author.name}")

    await member.ban(reason=reason)
    await ctx.send(f"{member.mention}", embed=ban_embed)


import discord
from discord.ext import commands

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name):
    banned_users = [entry async for entry in ctx.guild.bans()]
    
    for ban_entry in banned_users:
        user = ban_entry.user

        if user.name == member_name or str(user) == member_name:
            unban_embed = discord.Embed(
                title="✅ Usuario Desbaneado",
                description=f"**{user.name}** ha sido desbaneado del servidor.",
                color=discord.Color.green()
            )
            unban_embed.set_footer(text=f"Desbaneado por {ctx.author.name}")
            
            await ctx.guild.unban(user)
            await ctx.send(embed=unban_embed)
            return

    await ctx.send(f'Could not find user **{member_name}** in the ban list.')


@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not muted_role:
        return await ctx.send("The 'Muted' role was not found. Please create it.")

    if muted_role in member.roles:
        return await ctx.send(f"{member.mention} is already muted.")

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'{member.mention} has been muted. Reason: {reason or "None"}.')


@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not muted_role:
        return await ctx.send("The 'Muted' role was not found.")

    if muted_role not in member.roles:
        return await ctx.send(f"{member.mention} is not muted.")

    await member.remove_roles(muted_role, reason=reason)
    await ctx.send(f'{member.mention} has been unmuted. Reason: {reason or "None"}.')



active_polls = {}

@bot.command()
async def poll(ctx, *, args):
    parts = args.split('"')
    question = parts[1]
    options = [p.strip() for p in parts[2:] if p.strip() and p.strip() != '"']

    if len(options) < 2:
        return await ctx.send("Please provide at least two options for the poll.")
    if len(options) > 10:
        return await ctx.send("You can only have up to 10 options.")
    if ctx.channel.id in active_polls:
        return await ctx.send("There is already an active poll in this channel.")

    emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    poll_text = "\n".join([f"{emojis[i]} {option}" for i, option in enumerate(options)])

    embed = discord.Embed(
        title=f"📊 Encuesta: {question}",
        description=poll_text,
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Encuesta iniciada por {ctx.author.name}. Usa ?closepoll para cerrar.")

    poll_message = await ctx.send(embed=embed)

    for i in range(len(options)):
        await poll_message.add_reaction(emojis[i])

    active_polls[ctx.channel.id] = {
        "message_id": poll_message.id,
        "author_id": ctx.author.id,
        "options": options,
        "emojis": emojis
    }

@bot.command()
async def closepoll(ctx):
    """Closes the active poll in this channel and announces the winner."""
    if ctx.channel.id not in active_polls:
        return await ctx.send("There is no active poll in this channel.")

    poll_info = active_polls[ctx.channel.id]

    if ctx.author.id != poll_info["author_id"]:
        return await ctx.send("You can only close a poll that you started.")

    try:
        poll_message = await ctx.channel.fetch_message(poll_info["message_id"])
    except discord.NotFound:
        del active_polls[ctx.channel.id]
        return await ctx.send("The poll message was not found. The poll has been removed.")

    votes = {}
    for reaction in poll_message.reactions:
        if reaction.emoji in poll_info["emojis"]:
            votes[reaction.emoji] = reaction.count - 1

    if not votes:
        embed = discord.Embed(
            title="🗳️ Votación Finalizada",
            description="La votación se ha cerrado sin votos.",
            color=discord.Color.red()
        )
        await poll_message.edit(embed=embed)
        await ctx.send("La votación se ha cerrado sin votos.")
        del active_polls[ctx.channel.id]
        return

    winner_emoji = max(votes, key=votes.get)
    winner_count = votes[winner_emoji]

    winners = [emoji for emoji, count in votes.items() if count == winner_count]

    if len(winners) > 1:
        result_text = "¡Es un empate! 🤝"
    else:
        winning_option_index = poll_info["emojis"].index(winner_emoji)
        winning_option = poll_info["options"][winning_option_index]
        result_text = f"¡El ganador es **{winning_option}** con **{winner_count}** votos! 🎉"

    embed = poll_message.embeds[0]
    embed.add_field(name="Resultados", value=result_text, inline=False)
    embed.set_footer(text="Votación cerrada.")
    await poll_message.edit(embed=embed)

    del active_polls[ctx.channel.id]


user_warnings = {}

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if member.id not in user_warnings:
        user_warnings[member.id] = []

    user_warnings[member.id].append(reason)
    warning_count = len(user_warnings[member.id])

    warn_embed = discord.Embed(
        title="⚠️ Advertencia",
        description=f"¡Ten cuidado {member.mention}!",
        color=discord.Color.gold()
    )
    warn_embed.add_field(name="Razón", value=reason, inline=False)
    warn_embed.set_footer(text=f"Esta es tu advertencia número {warning_count}.")
    
    await ctx.send(f"{member.mention}", embed=warn_embed)

    if warning_count >= 5:
        ban_embed = discord.Embed(
            title="🚫 Usuario Baneado",
            description=f"**{member.name}** ha sido baneado automáticamente por exceder **5 advertencias**.",
            color=discord.Color.dark_red()
        )
        ban_embed.set_footer(text=f"Razón: Excedió las 5 advertencias.")
        
        await member.ban(reason="Exceeded 5 warnings.")
        await ctx.send(f"{member.mention}", embed=ban_embed)
        del user_warnings[member.id]


@bot.command()
@commands.has_permissions(kick_members=True)
async def warnings(ctx, member: discord.Member):
    """Displays a member's warnings in a professional-looking card."""
    if member.id not in user_warnings or not user_warnings[member.id]:
        no_warnings_embed = discord.Embed(
            title="✅ Sin Advertencias",
            description=f"**{member.name}** no tiene advertencias registradas.",
            color=discord.Color.green()
        )
        await ctx.send(embed=no_warnings_embed)
        return

    warn_list = "\n".join([f"**{i+1}.** {reason}" for i, reason in enumerate(user_warnings[member.id])])
    
    warnings_embed = discord.Embed(
        title=f"⚠️ Advertencias de {member.name}",
        description=warn_list,
        color=discord.Color.orange()
    )
    warnings_embed.set_footer(text=f"Total: {len(user_warnings[member.id])} advertencias")
    await ctx.send(embed=warnings_embed)

bot.run('token')
