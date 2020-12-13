from random import choice, randint
from typing import Optional


from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import BadArgument 
from discord.ext.commands import command

import discord, requests

class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="hello", aliases=["hi"])
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey'))} {ctx.author.mention}!")


	@command(name="dice", aliases=["roll"])
	async def roll_dice(self, ctx, die_string: str):
		dice, value = (int(term) for term in die_string.split("d"))

		if dice <= 25:
			rolls = [randint(1, value) for i in range(dice)]

			await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

		else:
			await ctx.send("Dice is greater then 25, please choose a smaller number")

	@command(name="slap", aliases=["hit"])
	async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "for no reason"):
		await ctx.send(f"{ctx.author.name} slapped {member.mention} {reason}!")

	@slap_member.error
	async def slap_member_error(self, ctx, exc):
		if isinstance(exc, BadArgument):
			await ctx.send("That member dosent exist.")


	@command(name="echo", aliases=["say"])
	async def echo_message(self, ctx, *, message):
		await ctx.message.delete()
		await ctx.send(message)

	@command(name="mimic", aliases=["copy"])
	async def mimic(self, ctx, member: Member, *args):
		try:
			wb = await ctx.channel.create_webhook( 
				name=str(member)[:-5], 
				avatar=requests.get(member.avatar_url).content
            )
		except discord.HTTPException:
			return await ctx.send("Failed to create webhook.")
		except discord.Forbidden:
			return await ctx.send("I do not have permissions to manage webhooks.")
        
		await ctx.message.delete()
		await wb.send(" ".join(args))
		await wb.delete(reason="Mimic Webhook Deleted")

				

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")


def setup(bot):
	bot.add_cog(Fun(bot))