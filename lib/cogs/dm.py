from random import choice, randint, random
from typing import Optional
import os
from better_profanity import profanity
from RandomWordGenerator import RandomWord
from aiohttp import request
from discord import Member, Embed, File, Message
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument
from discord.ext.commands import command, cooldown
import json
from datetime import datetime
import discord, requests
import aiohttp
import io


class Dm(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="modmail", aliases=["mm"], brief= "Mail a mod")
	async def mod_message(self, ctx):
		await ctx.message.delete() 
		await ctx.send(embed=Embed(description=f"{ctx.author.mention} Send a direct message to me", delete_after=5))





	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("dm")

def setup(bot):
	bot.add_cog(Dm(bot))