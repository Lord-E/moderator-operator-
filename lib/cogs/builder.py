from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db

class Builder(Cog):
	def __init__(self, bot):
		self.bot = bot

	# @command(name="mtc")
	# async def make_text_channel(self, ctx):

	# 	# mtc = True
	# 	# await ctx.send(f"Design text channel")

	# 	# while self.mtc:





	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("builder")

def setup(bot):
	bot.add_cog(Builder(bot))