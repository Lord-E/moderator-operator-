# from discord import Forrbidden
from discord.ext.commands import Cog
# from discord.ext.commands import command, has_permissions

# from ..db import db

class Log(Cog):
	def __init__(self, bot):
		self.bot = bot

	# @Cog.listener()
	# async def on_ready(self):
	# 	if not self.bot.ready:
	# 		self.bot.cogs_ready.ready_up("log")

	# @Cog.listener()
	# async def on_member_update(self, before, after):

	# @Cog.listener()
	# async def on_member_(self, before, after):

	# @Cog.listener()
	# async def on_message_delete(self, before, after):




	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("log")

def setup(bot):
	bot.add_cog(Log(bot))