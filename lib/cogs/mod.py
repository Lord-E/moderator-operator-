import asyncio 
from datetime import datetime, timedelta
from typing import Optional
from re import search

from better_profanity import profanity
from discord.errors import HTTPException, Forbidden 
from discord import Embed, Member, NotFound, Object
from discord.utils import find
from discord.ext.commands import Cog, Greedy, Converter
from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions
from discord.ext.commands import MissingPermissions

import time
from ..db import db

profanity.load_censor_words_from_file("./data/profanity.txt")

class BannedUser(Converter):
	async def convert(self, ctx, arg):
		if ctx.guild.me.guild_permissions.ban_members:
			if arg.isdigit():
				try:
					return (await ctx.guild.fetch_ban(Object(id=int(arg)))).user
				except NotFound:
					raise BadArgument

		banned = [e.user for e in await ctx.guild.bans()]
		if banned:
			if (user := find(lambda u: str(u) == arg, banned)) is not None:
				return user
			else:
				raise BadArgument


class Mod(Cog):
	def __init__(self, bot):

		self.bot = bot

		self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
		
		self.no_links_allowed = (794040379791114250, 761766201680068633)
		self.no_images_allowed = (794040379791114250, 761766201680068633)

	async def kick_members(self, message, targets, reason):
		for target in targets:
			if (message.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
				await target.kick(reason=reason)

				embed = Embed(title="Member kicked",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
						  ("Actioned by", message.author.display_name, False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="kick", brief="Kicks member", description="(Mods only) kick @member <reason>")
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def kick_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("Please specify a member to kick.")

		else:
			await self.kick_members(ctx.message, targets, reason)
			await ctx.send(f"Member was kicked.")


	async def ban_members(self, message, targets, reason):
		for target in targets:
			if (message.guild.me.top_role.position > target.top_role.position
				and not target.guild_permissions.administrator):
				await target.ban(reason=reason)

				embed = Embed(title="Member banned",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
						  ("Actioned by", message.author.display_name, False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="ban", brief="Ban a member", help="(Mod only) ban @member <reason>")
	@bot_has_permissions(ban_members=True)
	@has_permissions(ban_members=True)
	async def ban_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("Please specify a member to ban.")

		else:
			await self.ban_members(ctx.message, targets, reason)
			await ctx.send("Member was banned.")

	@command(name="clear", aliases=["purge"])
	@bot_has_permissions(manage_messages=True)
	@has_permissions(manage_messages=True)
	async def clear_messages(self, ctx, targets: Greedy[Member], limit: Optional[int] = 1):
		def _check(message):
			return not len(targets) or message.author in targets

		if 0 < limit <= 1000:
			with ctx.channel.typing():
				await ctx.message.delete()
				deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14),
												  check=_check)

				await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

		else:
			await ctx.send("The limit provided is not within acceptable bounds.")


	async def mute_members(self, message, targets, hours, reason):
		unmutes = []

		for target in targets:
			if not self.mute_role in target.roles:
				if message.guild.me.top_role.position > target.top_role.position:
					role_ids = ",".join([str(r.id) for r in target.roles])
					end_time = datetime.utcnow() + timedelta(seconds=hours) if hours else None

					db.execute("INSERT INTO mutes VALUES (?, ?, ?)",
							   target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())

					await target.edit(roles=[self.mute_role])

					embed = Embed(title="Member muted",
								  colour=0xDD2222,
								  timestamp=datetime.utcnow())

					embed.set_thumbnail(url=target.avatar_url)

					fields = [("Member", target.display_name, False),
							  ("Actioned by", message.author.display_name, False),
							  ("Duration", f"{hours:,} hour(s)" if hours else "Indefinite", False),
							  ("Reason", reason, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

					await self.log_channel.send(embed=embed)

					if hours:
						unmutes.append(target)

		return unmutes

	@command(name="mute")
	@bot_has_permissions(manage_roles=True)
	@has_permissions(manage_roles=True, manage_guild=True)
	async def mute_command(self, ctx, targets: Greedy[Member], hours: Optional[int], *,
						   reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more required arguments are missing.")

		else:
			unmutes = await self.mute_members(ctx.message, targets, hours, reason)
			await ctx.send(f"`Member/s were muted.`")

			if len(unmutes):
				time.sleep(hours)
				await self.unmute_members(ctx.guild, targets)

	@mute_command.error
	async def mute_command_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")

	async def unmute_members(self, guild, targets: Optional[Member], *, reason="Mute time expired."):

		for target in targets:
			if self.mute_role in target.roles:
				role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ?", target.id)
				roles = [guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

				db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

				await target.edit(roles=roles)

				embed = Embed(title="Member unmuted",
							  colour=0xDD2222,
							  timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", target.display_name, False),
						  ("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@command(name="unmute")
	@bot_has_permissions(manage_roles=True)
	@has_permissions(manage_roles=True, manage_guild=True)
	async def unmute_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("One or more required arguments is missing.")

		else:
			await self.unmute_members(ctx.guild, targets, reason=reason)
			await ctx.send(f"`Member/s were unmuted.`")


	@command(name="addprofanity", aliases=["addswears", "addcurses"])
	@has_permissions(manage_guild=True)
	async def add_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "a", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in words]))

		await ctx.send("Word added.")
		profanity.load_censor_words_from_file("./data/profanity.txt")

	@command(name="delprofanity", aliases=["delswears", "delcurses"])
	@has_permissions(manage_guild=True)
	async def remove_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "r", encoding="utf-8") as f:
			stored = [w.strip() for w in f.readlines()]

		with open("./data/profanity.txt", "w", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in stored if w not in words]))
		
		profanity.load_censor_words_from_file("./data/profanity.txt")
		
		await ctx.send("Word deleted.")
	
	@command(name="prolist", aliases=["ps", "spillpro"])
	@has_permissions(manage_guild=True)
	async def spill_profanity(self, ctx):
		profanity.load_censor_words_from_file("./data/profanity.txt")
		a_file = open("./data/profanity.txt")

		lines = a_file.readlines()
		for line in lines:
			await ctx.send(line)

	@command(aliases=["renameall"], brief = "Credit: https://github.com/ARealWant/Guildbomb-Discord-Raid-Bot")
	@has_permissions(manage_guild=True)
	async def all_rename(self, ctx, *, newname):
		await ctx.send(f"Rename everyone to `{newname}` in `{ctx.guild.name}`? [y/n]")

		def check_data(message):
			return message.author == ctx.message.author

		while True:
			try:
				msg = await self.bot.wait_for('message', check=check_data, timeout=15.0)
				if msg.content == "y":
					await ctx.send("Renaming...")
					for user in list(ctx.guild.members):
						try:
							await user.edit(nick=f"{newname}")
							
						except Exception:
							pass
					await ctx.send("Done")
					return
				if msg.content == "n":
					await ctx.send("Canceled")
					return
			except asyncio.TimeoutError:
				await ctx.send("You toke too long")
				return

	@command(name="dmall", aliases=["annouce", "alldm"], brief = "Credit: https://github.com/ARealWant/Guildbomb-Discord-Raid-Bot")
	@has_permissions(manage_guild=True)
	async def all_dm(self, ctx, *, message):
		await ctx.send(f"DM everyone with `{message}` in `{ctx.guild.name}`? [y/n]")

		def check_data(message):
			return message.author == ctx.message.author

		while True:
			try:
				msg = await self.bot.wait_for('message', check=check_data, timeout=15.0)
				if msg.content == "y":
					await ctx.send("Sending...")
					for user in list(ctx.guild.members):
						try:
							await user.send(message)
						except Exception:
							pass
					await ctx.send("Done")
					return
				if msg.content == "n":
					await ctx.send("Canceled")
					return
			except asyncio.TimeoutError:
				await ctx.send("You toke too long")
				return


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(788905081704939550)
			self.mail_channel = self.bot.get_channel(794040379791114250)
			self.mute_role = self.bot.guild.get_role(788562239958810635)
			self.bot.cogs_ready.ready_up("mod")

	@Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:
			if profanity.contains_profanity(message.content):
				await message.delete()
				await message.channel.send("`censored`", delete_after=10)

			elif message.channel.id in self.no_links_allowed and search(self.url_regex, message.content):
				await message.delete()
				await message.channel.send("`You can't send links here`", delete_after=10)

			if (message.channel.id in self.no_images_allowed
				and any([hasattr(a, "width") for a in message.attachments])):
				await message.delete()
				await message.channel.send("`You can't send images here`", delete_after=10)


def setup(bot):
	bot.add_cog(Mod(bot))