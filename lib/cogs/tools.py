from typing import Optional
from datetime import datetime
import asyncio 
import discord
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

	@command(name="makechannel")
	async def make_text_channel(self, ctx):
		await ctx.send("Name of channel?")
		name = str((await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.strip(), timeout=15.0)).content.capitalize())

		await ctx.send("What kind of channel would you like to create? ``text/voice/stage``")
		chan_type = str((await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.strip(), timeout=15.0)).content.capitalize())

		if chan_type == "Text":

			await ctx.send("Creating text channel...")
			try:
				await ctx.author.guild.create_text_channel(str(name))
				await ctx.send(f"Text channel: {str(name)} has been made")
			
			except:
				await ctx.send(f"Could not make text channel: {str(name)}")

		elif chan_type == "Voice":

			await ctx.send("Creating voice channel...")
			try:
				await ctx.author.guild.create_voice_channel(str(name))
				await ctx.send(f"voice channel: {str(name)} has been made")
			
			except:
				await ctx.send(f"Could not make voice channel: {str(name)}")

		elif chan_type == "Stage":

			await ctx.send("Creating stage channel...")
			try:
				await ctx.author.guild.create_stage_channel(str(name))
				await ctx.send(f"stage channel: {str(name)} has been made")
			
			except:
				await ctx.send(f"Could not make stage channel: {str(name)}")

		else:
			await ctx.send(f"That is not a option")






	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("tools")


def setup(bot):
	bot.add_cog(Tools(bot))