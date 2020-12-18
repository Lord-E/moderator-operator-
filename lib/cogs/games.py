import random, asyncio
from typing import Optional


from aiohttp import request
from discord import Member, Embed, File, Message
from discord.ext.commands import Cog
from discord.ext.commands import BadArgument 
from discord.ext.commands import command, cooldown
from datetime import datetime
import discord, requests

class Games(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.number_guessing_running = False

	def is_int(self, s: str) -> bool:
		try:
			int(s)
			return True
		except ValueError:
			return False

	@command(name="numguess", aliases=["ng"], breif="Guess a number\n Credit: Xhiro#0177")
	async def number_guessing(self, ctx, x: int = 1, y: int = 100):
		key = random.randint(x, y)
		self.number_guessing_running = True
		await ctx.send(f"Guess a number between {x} and {y}!")
		while self.number_guessing_running:
			try:
				guess = int((await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and self.is_int(m.content.strip()), timeout=15.0)).content.strip())

			except asyncio.TimeoutError:
				return await ctx.send(f"Too slow. The answer was {key}")

			if guess > key:
				self.num_guess_running = True
				return await ctx.send(f"Too high! You guessed {guess}.")

			if guess < key:
				self.num_guess_running = True
				return await ctx.send(f"Too low! You guessed {guess}.")

			if guess == key:
				self.num_guess_running = False
				return await ctx.send(f"Correct! You guessed {guess}.")



	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("games")

def setup(bot):
	bot.add_cog(Games(bot))