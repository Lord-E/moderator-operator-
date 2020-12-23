from typing import Optional
from datetime import datetime

from discord import Member, Spotify, Embed, ClientUser 
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions

from discord.ext.commands import Cog, Greedy, Converter
from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions
from discord.ext.commands import MissingPermissions

class Info(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="userinfo", aliases=["memberinfo", "ui", "mi"] )
	@has_permissions(manage_guild=True)
	async def user_info(self, ctx, target: Optional[Member]):
		target = target or ctx.author

		roles = [role for role in target.roles]

		embed= Embed(title=f"{target} Info",
					 color=target.color,
					 timestamp=datetime.utcnow())

		fields =  [	("Name", str(target), True),
				("ID", target.id, True),
				("Nickname", target.display_name, True),
				("Status", str(target.status).title(), False),
				("Bot", target.bot, True),				
				("Server Boosts", bool(target.premium_since), True),			
				("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
				("Created at", target.created_at.strftime("%m/%m/%Y at %H:%M:%S"), True),
				("Joined at", target.joined_at.strftime("%m/%m/%Y at %H:%M:%S"), True),
				("Roles", ", ".join([role.mention for role in roles]), False)]

		for name, value, inline in fields:
 			embed.add_field(name=name, value=value, inline=inline)
 			embed.set_thumbnail(url=target.avatar_url)
 			embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
		
		await ctx.send(embed=embed)

	@user_info.error
	async def user_info_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Insufficient permissions to perform that task.")


	@command(name="avatar", aliases=["avi", "pfp", "profilepicture"] )
	@has_permissions(manage_guild=True)
	async def user_piture(self, ctx, target: Optional[Member], ):
		target = target or ctx.author


		embed= Embed(title=f"{target} Avatar",
					 color=target.color,
					 timestamp=datetime.utcnow())

		fields =  [	("\u200b", "\u200b", False),

]

		for name, value, inline in fields:
 			embed.add_field(name=name, value=value, inline=inline)
 			embed.set_image(url=target.avatar_url)
 			embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
		
		await ctx.send(embed=embed)

	@command(name="usersong", aliases=["spotify", "song", "usp"])
	async def user_song(self, ctx, target: Optional[Member]):
		target = target or ctx.author
		for activity in target.activities:
			if isinstance(activity, Spotify):
					embed = Embed(
						title = f"{target}'s Spotify",
						description = "Listening to {}".format(activity.title),
						color = target.color)

					fields = [("Artist", target.activity.artist, False),    
							 ("Album", target.activity.album, False)]

					for name, value, inline in fields:
						embed.set_thumbnail(url=activity.album_cover_url)
						embed.set_footer(text="Song started at {}".format(activity.created_at.strftime("%H:%M")))

					await ctx.send(embed=embed)



	@command(name="serverinfo", aliases=["guildinfo", "si", "gi"])
	@has_permissions(manage_guild=True)
	async def server_info(self, ctx):


		embed= Embed(title="Server Info",
					 color=ctx.guild.owner.color,
					 timestamp=datetime.utcnow())

		statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

		fields = [("ID", ctx.guild.id, True),
				  ("Owner", ctx.guild.owner, True),
				  ("Region", ctx.guild.region, True),
				  ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Banned members", len(await ctx.guild.bans()), True),
				  ("Members", len(ctx.guild.members), True),
				  ("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
				  ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
				  ("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
				  ("Text channels", len(ctx.guild.text_channels), True),
				  ("Voice channels", len(ctx.guild.voice_channels), True),
				  ("Categories", len(ctx.guild.categories), True),
				  ("Roles", len(ctx.guild.roles), True),
				  ("Invites", len(await ctx.guild.invites()), True),
				  ("Verifaction Level", ctx.guild.verification_level, True),
				  ("Emojis", len(ctx.guild.emojis), True),
				  ("Boosts", ctx.guild.premium_tier, True),
				  ("\u200b", "\u200b", True)]

		for name, value, inline in fields:
 			embed.add_field(name=name, value=value, inline=inline)
 			embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
 			embed.set_thumbnail(url=ctx.guild.icon_url)
		
		await ctx.send(embed=embed)



	@Cog.listener()

	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("info")


def setup(bot):
	bot.add_cog(Info(bot))