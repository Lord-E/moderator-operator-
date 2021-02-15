from random import choice, randint, random
from typing import Optional

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

class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="hello", aliases=["hi"], brief= "Say hi to me")
	async def say_hello(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey'))} {ctx.author.mention}!")

	@command(name="flip", aliases=["headsortails"], brief= "Say hi to me")
	async def flip(self, ctx):
		await ctx.send(f"{choice(('Heads', 'Tails'))}")

	@command(name="shoot")
	@cooldown(3, 60, BucketType.user)
	async def shoot_member(self, ctx, member: Member):
		await ctx.send(f"{ctx.author.name} fired at {member.mention} and {choice(('hit them', 'missed them'))}")

	@command(name="dice", aliases=["roll"])
	async def roll_dice(self, ctx, die_string: str):
		dice, value = (int(term) for term in die_string.split("d"))

		if dice <= 25:
			rolls = [randint(1, value) for i in range(dice)]

			await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

		else:
			await ctx.send("Dice is greater than 25, please choose a smaller number")


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
		profanity.load_censor_words_from_file("./data/profanity.txt")
		if profanity.contains_profanity(message):
			await ctx.send("I cant say that")

		else:
			await ctx.message.delete()
			await ctx.send(message)

	@command(name="spam")
	@cooldown(3, 180, BucketType.user)
	async def spammer(self, ctx, x, *, message):
		w = int(x)
		if w > 7:
			await ctx.send("I can only spam a maximum of 7 times")
		
		else:
			y = range(w)
			for i in y:
				await ctx.send(message)

	@command(name="mimic", aliases=["copy"])
	async def mimic(self, ctx, member: Member, *args):	
		profanity.load_censor_words_from_file("./data/profanity.txt")
		if profanity.contains_profanity(args):
			await ctx.send("I cant say that")

		else:
			try:
				wb = await ctx.channel.create_webhook( 
					name=str(member)[:-5], 
					avatar=requests.get(member.avatar_url).content
				)
			except discord.HTTPException:
				return await ctx.send("Failed to create webhook.")
			
			await ctx.message.delete()
			await wb.send(" ".join(args))
			await wb.delete(reason="Mimic Webhook Deleted")

	@command(name="quote")
	@cooldown(3, 180, BucketType.user)
	async def anime_quote(self, ctx):
		quote_url = "https://some-random-api.ml/animu/quote"

		async with request("GET", quote_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()

				embed = Embed(title=f"Anime quote",
							  description=data["sentence"],
							  timestamp=datetime.utcnow(),
							  color=ctx.author.color)
				await ctx.send(embed=embed)


			else:
				await ctx.send(f"API returned a {response.status} status.")

	@command(name="facepalm")
	@cooldown(3, 180, BucketType.user)
	async def face_palm(self, ctx):
		face_url = "https://some-random-api.ml/animu/face-palm"

		async with request("GET", face_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()
				face_url = data["link"]

				embed = Embed(title=f"{ctx.author} facepalms",							  
							  timestamp=datetime.utcnow(),
							  color=ctx.author.color)
				embed.set_image(url=face_url)
				await ctx.send(embed=embed)


			else:
				await ctx.send(f"API returned a {response.status} status.")



	@command(name="fact")
	@cooldown(3, 180, BucketType.user)
	async def animal_fact(self, ctx, animal: str):
		if (animal := animal.lower()) in ("dog", "cat", "panda", "fox", "bird", "koala", "racoon", "kangaroo", "whale"):
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
	@cooldown(3, 180, BucketType.user)
	async def pat_member(self, ctx, member: discord.Member, *args):
		await self.emotion_base(ctx,
		member=member,
			api="https://some-random-api.ml/animu/pat",
			format="<author> pats <member> " + " ".join(args))

	@command(name="hug")
	@cooldown(3, 180, BucketType.user)
	async def hug_member(self, ctx, member: discord.Member, *args):
		await self.emotion_base(ctx,
			member=member,
			api="https://some-random-api.ml/animu/hug",
			format="<author> hugs <member> " + " ".join(args))

	@command(name= "wink")
	@cooldown(3, 180, BucketType.user)
	async def wink_member(self, ctx, member: discord.Member, *args):
		await self.emotion_base(ctx,
			member=member,
			api="https://some-random-api.ml/animu/wink",
			format="<author> winks to <member> " + " ".join(args))

	@command(name="8ball")
	async def roll_ball(self, ctx, *, message):
		answer = ['As I see it, yes.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.', 'Don’t count on it.', 'It is certain.','It is decidedly so.', 'Most likely.', 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Outlook good.', 'Reply hazy, try again.', 'Signs point to yes.', 'Very doubtful.', 'Without a doubt.', 'Yes.', 'Yes – definitely.', 'You may rely on it'] 
				
		embed = Embed(title="8Ball", timestamp= datetime.utcnow())


		embed.add_field(name= "\u200b", value= f"**Message:** {message}", inline= True)
		embed.add_field(name= "\u200b", value= f"**Answer:** {choice(answer)}", inline= False)         

		await ctx.send(embed=embed)

	@command(name="sep")
	@cooldown(5, 60, BucketType.user)
	async def seperate(self, ctx, x, *, message):
		if len(message) > 150:
			await ctx.send("150 charactors maximum to reduce spam")

		else:		
			message = message.split(" ")
			await ctx.send(f" {x} ".join(message))

	@command(name="ranper")
	async def random_percent(self, ctx):
			
		embed = Embed(color=0xB8821F, timestamp= datetime.utcnow())


		embed.add_field(name="Percetometer", value=f"{randint(1, 100)}%", inline=False)  
		
		await ctx.send(embed=embed)

	@command(name="random", aliases=['rand'])
	async def ran_word(self, ctx):
		rw = RandomWord(max_word_size=15,
				constant_word_size=True,
				special_chars=r"@#$%.*",
				include_special_chars=True)

		await ctx.send(rw.generate())


	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")


def setup(bot):
	bot.add_cog(Fun(bot))