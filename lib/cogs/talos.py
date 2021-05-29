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
import asyncpraw 
import pyautogui, sys

class Talos(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="meme")
	@cooldown(3, 180, BucketType.user)
	async def meme_quote(self, ctx):
		reddit = asyncpraw.Reddit(client_id = "cv4eeeqKG-IseA",
							 client_secret = "t3O9tFzRXpYybwLAn4cquJ2QKgLh2Q",
							 username = "Budget_Sport7551",
							 password = ":L3uW2VjUZ8Y6d3",
							 user_agent = "eleop")

		subreddit = reddit.subreddit("memes")
		all_subs = []

		top = subreddit.top(limit = 50)

		for submission in top:
			all_subs.append(submission)

		random_sub = choice(all_subs)

		name = random_sub.title
		url = random_sub.url

		embed = Embed(title = name) 

		embed.set_image(url=url)
		embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

		await ctx.send(embed=embed)

	@command(name="mousepos")
	@cooldown(3, 180, BucketType.user)
	async def mouse_pos(self, ctx):
		if ctx.author.id == 717486310566133844:
			x, y = pyautogui.position()
			await ctx.send(f"Operator's current mouse position:\n X:  + {str(x).rjust(4)} +  Y:  + {str(y).rjust(4)}")







	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("talos")



def setup(bot):
	bot.add_cog(Talos(bot))