from datetime import datetime
from typing import Optional

from discord import Embed, Member
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions

class Mod(Cog):
	def __init__(self, bot):

		self.bot = bot

	@command(name="kick")
	@bot_has_permissions(kick_members=True)
	@has_permissions(kick_members=True)
	async def kick_member(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason provided."):
		if not len(targets):
			await ctx.send("Who are you kicking?")

		else:
			for target in targets:
				await target.kick(reason=reason)

				embed = Embed(title= f"{target.display_name} was kicked!",
					  	  	  color=0xE60000,
					  	  	  timestamp= datetime.utcnow())

				embed.set_thumbnail(url=target.avatar_url)

				fields = [("Member", f"{target.name} a.k.a {target.display_name}", False),
						  ("Actioned by", ctx.author.display_name, False),
						  ("Reason", reason, False)]


				for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(788905081704939550)
			self.bot.cogs_ready.ready_up("mod")

def setup(bot):
	bot.add_cog(Mod(bot))