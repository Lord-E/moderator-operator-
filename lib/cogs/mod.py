from asyncio import sleep
from datetime import datetime, timedelta
from typing import Optional

from better_profanity import profanity
from discord.errors import HTTPException, Forbidden 
from discord import Embed, Member, NotFound, Object
from discord.utils import find
from discord.ext.commands import Cog, Greedy, Converter
from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions
from discord.ext.commands import MissingPermissions

from ..db import db

profanity.load_censor_words_from_file("./data/profanity.txt")

class Mod(Cog):
	def __init__(self, bot):

		self.bot = bot

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

	@command(name="mute", aliases=["silence"])
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def mute_command(self, ctx, targets: Greedy[Member], hours: Optional[int], *, 
						  reason: Optional[str] = "No reason provided."):
		
		if not len(targets):
			await ctx.send("Please specify a member to mute.")

		else:
			unmutes = []
			for target in targets:
				if not self.mute_role in target.roles:
					if ctx.guild.me.top_role.position > target.top_role.position:
						role_ids = ",".join([str(r.id) for r in target.roles])
						end_time = datetime.utcnow() + timedelta(hours=hours) if hours else None

						db.execute("INSERT INTO mutes VALUES (?, ?, ?)",
								target.id, role_ids, getattr(end_time, "isoformat", lambda: None)())
						
						await target.edit(roles=[self.mute_role])

						embed = Embed(title="Member muted",
							  		  colour=0xDD2222,
							  		  timestamp=datetime.utcnow())

						embed.set_thumbnail(url=target.avatar_url)

						fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
						 		  ("Actioned by", ctx.author.display_name, False),
								  ("Duration", f"{hours:,} hour(s)" if hours else "Indefinite", False),
						  		  ("Reason", reason, False)]

						for name, value, inline in fields:
							embed.add_field(name=name, value=value, inline=inline)

						await self.log_channel.send(embed=embed)

						if hours:
							unmutes.append(target)

					else:
						await ctx.send(f"{target.display_name} could not be muted.")

				else:
					await ctx.send(f"{target.display_name} is already muted.")

			await ctx.send(f"{target.display_name} was muted.")

			if len(unmutes):
				await sleep(hours)
				await self.unmute(ctx, targets)

	async def unmute(self, ctx, targets, *, reason="Mute time expired."):
		for target in targets:
			if self.mute_role in target.roles:
				role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ?", target.id)
				roles = [ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

				db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

				await target.edit(roles=roles)
				
				embed = Embed(title="Member unmuted",
								colour=0xDD2222,
								timestamp=datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a. {target.display_name}", False),
							("Reason", reason, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)


	@command(name="unmute", aliases=["um"])
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def unmute_command(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):		
		if not len(targets):
			await ctx.send("Please specify a member to unmute.")

		else:
			await self.unmute(ctx, targets, reason=reason)

	@command(name="addprofanity", aliases=["as", "addcurse"])
	@has_permissions(manage_guild=True)
	async def add_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "a", encoding="utf-8") as f:
			f.write("".join({f"{w}\n" for w in words}))

		await ctx.send("Word was added to profanity list")


	@command(name="delprofanity", aliases=["ds", "removecurse"])
	@has_permissions(manage_guild=True)
	async def add_profanity(self, ctx, *words):
		pass
	



	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(788905081704939550)
			self.mail_channel = self.bot.get_channel(794040379791114250)
			self.mute_role = self.bot.guild.get_role(788562237434232876)
			self.bot.cogs_ready.ready_up("mod")

	@Cog.listener()
	async def on_message(self, message):
		if not message.author.bot:
			if profanity.contains_profanity(message.content):
				await message.delete()
				await message.channel.send("`censored`")


def setup(bot):
	bot.add_cog(Mod(bot))