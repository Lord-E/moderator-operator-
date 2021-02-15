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

class Rules(Cog):
	def __init__(self, bot):

		self.bot = bot
	
	
	@command(name="addrules", aliases=["ar"])
	@has_permissions(manage_guild=True)
	async def add_rule(self, ctx, *words):
		with open("./data/profanity.txt", "a", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in words]))

		await ctx.send("Rule added.")
		profanity.load_censor_words_from_file("./data/rules.txt")

	@command(name="delrule", aliases=["dr"])
	@has_permissions(manage_guild=True)
	async def remove_profanity(self, ctx, *words):
		with open("./data/profanity.txt", "r", encoding="utf-8") as f:
			stored = [w.strip() for w in f.readlines()]

		with open("./data/profanity.txt", "w", encoding="utf-8") as f:
			f.write("".join([f"{w}\n" for w in stored if w not in words]))
		
		profanity.load_censor_words_from_file("./data/rules.txt")
		
		await ctx.send("Rule deleted.")
	
	@command(name="rulelist", aliases=["rl"])
	@has_permissions(manage_guild=True)
	async def spill_profanity(self, ctx):
		profanity.load_censor_words_from_file("./data/rules.txt")
		a_file = open("./data/rules.txt")

		lines = a_file.readlines()
		for line in lines:
			await ctx.send(line)

	@Cog.listener()

	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("rules")


def setup(bot):
	bot.add_cog(Rules(bot))