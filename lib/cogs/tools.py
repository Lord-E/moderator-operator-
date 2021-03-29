from typing import Optional
from datetime import datetime

from discord import Member, Spotify, Embed, ClientUser, CategoryChannel, Guild 
from discord.ext.commands import Cog
from discord.ext.commands import command, has_permissions
from discord.ext.commands import Cog, Greedy, Converter
from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions
from discord.ext.commands import MissingPermissions

class Tools(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="mt")
	async def make_text_channel(self, ctx, name):
		await guild.create_text_channel(name)


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("tools")


def setup(bot):
	bot.add_cog(Tools(bot))