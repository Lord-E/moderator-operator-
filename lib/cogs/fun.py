from random import choice, randint
from typing import Optional


from aiohttp import request
from discord import Member, Embed, File
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import BadArgument 
from discord.ext.commands import command, cooldown
import json
from datetime import datetime
import discord, requests

class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="hello", aliases=["hi"], brief= "Say hi to me")
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey'))} {ctx.author.mention}!")

	@command(name="shoot", aliases=["kill"])
	@cooldown(6, 60, BucketType.user)
	async def shoot_member(self, ctx, member: Member):
		await ctx.send(f"{ctx.author.name} fired at {member.mention} and {choice(('hit them', 'missed them'))}")


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
	@cooldown(1, 60, BucketType.user)
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

	@command(name="fact")
	@cooldown(3, 180, BucketType.user)
	async def animal_fact(self, ctx, animal: str):
		if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala"):
			fact_url = f"https://some-random-api.ml/facts/{animal.lower()}"
			image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

			async with request("GET", image_url, headers=[]) as response:
				if response.status == 200:
					data = await response.json()
					image_link = data["link"]

				else:
					image_link = None

			async with request("GET", fact_url, headers=[]) as response:
				if response.status == 200:
					data = await response.json()

					embed = Embed(title=f"{animal.title()} fact",
								  description=data["fact"],
								  timestamp=datetime.utcnow(),
								  color=ctx.author.color)
					if image_link is not None:
						embed.set_image(url=image_link)
					await ctx.send(embed=embed)


				else:
					await ctx.send(f"API returned a {response.status} status.")

		else:
			await ctx.send("No facts are avilable for that animal.")

	@Cog.listener()
	async def emotion_base(self, ctx, *, member: discord.Member, api: str, format: str):
		if not member:
			return await ctx.send("`Invalid user.`")

		with requests.request("GET", api) as req:
			if not req.status_code == 200:
				return await ctx.send("`Error while getting GIF URL.`")
			gif_url = req.json()["link"]

		format = format.replace("<author>", str(ctx.author)[:-5]).replace("<member>", str(member)[:-5])

		await ctx.send(
			embed=discord.Embed(
				title=format,
				timestamp=datetime.utcnow()
			).set_image(url=gif_url)
		)


	@command(name= "pat")
	async def pat_member(self, ctx, member: discord.Member, *args):
		await self.emotion_base(ctx,
		member=member,
			api="https://some-random-api.ml/animu/pat",
			format="<author> pats <member> " + " ".join(args))

	@command(name="hug")
	async def hug_member(self, ctx, member: discord.Member, *args):
		await self.emotion_base(ctx,
			member=member,
			api="https://some-random-api.ml/animu/hug",
			format="<author> hugs <member> " + " ".join(args))

	@command(name= "wink")
	async def wink_member(self, ctx, member: discord.Member, *args):
		await self.emotion_base(ctx,
			member=member,
			api="https://some-random-api.ml/animu/wink",
			format="<author> winks to <member> " + " ".join(args))


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")


def setup(bot):
	bot.add_cog(Fun(bot))