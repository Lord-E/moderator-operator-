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
import praw

class Fun(Cog):
	def __init__(self, bot):
		self.bot = bot


	@command(name="hello", aliases=["hi"], brief= "Say hi to me")
	async def say_hello(self, ctx): 
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey'))} {ctx.author.mention}!")

	@command(name="flip", aliases=["headsortails"], brief= "Say hi to me")
	async def flip(self, ctx):
		await ctx.send(f"{choice(('Heads', 'Tails'))}")

	@command(name="magic")
	async def magictrick(self, ctx):
		await ctx.send("Screen shot this picture:")
		await ctx.send("https://thispersondoesnotexist.com/image")

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

	@command(name="mimic", aliases=["copy"], brief = "Credit: xhiro#(numbers)")
	async def mimic(self, ctx, member: Member, *args):
		if str(member.nick) == "None":
			name = str(member)[:-5]
		else:
			name = str(member.nick)

		
		try:
			wb = await ctx.channel.create_webhook( 
				name=name, 
				avatar=requests.get(member.avatar_url).content
			)
		except discord.errors.HTTPException:
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
				sen = data["sentence"]
				car = data["characther"]
				ani = data["anime"]

				embed = Embed(title=f"Anime quote",
							  description=f"{sen} \n by {car} from {ani}",
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
	async def overlays(self, ctx, *, member: discord.Member=None, api: str, format: str):
		if not member:
			member = ctx.author
				
		wastedsession = aiohttp.ClientSession()
		async with wastedsession.get(f"{api}?avatar={member.avatar_url_as(format='png')}") as img:
			if img.status != 200:
				await ctx.send("Unable to get image")
				await wastedsession.close()      
			else:
				data = io.BytesIO(await img.read())
				await ctx.send(file=discord.File(data, f'{format}.png'))
			await wastedsession.close()

	@command(name="wasted")
	async def wasted_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/wasted",
			format= "wasted")

	@command(name="gay")
	async def gay_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/gay",
			format= "gay")

	@command(name="glass")
	async def glass_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/glass",
			format= "glass")

	@command(name="jail")
	async def jail_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/jail",
			format= "jail")

	@command(name="invert")
	async def invert_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/invert",
			format= "invert")


	@command(name="blur")
	async def blur_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/blur",
			format= "blur")
	
	@command(name="brightness")
	async def brightness_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/brightness",
			format= "brightness")

	@command(name="threshold")
	async def threshold_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/threshold",
			format= "threshold")

	@command(name="sepia")
	async def sepia_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/sepia",
			format= "sepia")

	@command(name="pixelate")
	async def pixelate_member(self, ctx, member: discord.Member=None):
		if not member:
			member = ctx.author

		await self.overlays(ctx,
			member=member, 
			api="https://some-random-api.ml/canvas/pixelate",
			format= "pixelate")

	@command(name="trigger")
	async def tiger(self, ctx, *, member: discord.Member=None):
		if not member:
			member = ctx.author
				
		wastedsession = aiohttp.ClientSession()
		async with wastedsession.get(f"https://some-random-api.ml/canvas/triggered/?avatar={member.avatar_url_as(format='png')}") as img:
			if img.status != 200:
				await ctx.send("Unable to get image")
				await wastedsession.close()      
			else:
				data = io.BytesIO(await img.read())
				await ctx.send(file=discord.File(data, f'triggered.gif'))
			await wastedsession.close()

	
	@command(name="simp")
	async def simply(self, ctx, *, member: discord.Member=None):
		if not member:
			member = ctx.author
				
		wastedsession = aiohttp.ClientSession()
		async with wastedsession.get(f"https://some-random-api.ml/canvas/simpcard/?avatar={member.avatar_url_as(format='png')}") as img:
			if img.status != 200:
				await ctx.send("Unable to get image")
				await wastedsession.close()      
			else:
				data = io.BytesIO(await img.read())
				await ctx.send(file=discord.File(data, f'simpcard.png'))
			await wastedsession.close()

	@command(name="horny")
	async def horm(self, ctx, *, member: discord.Member=None):
		if not member:
			member = ctx.author
				
		wastedsession = aiohttp.ClientSession()
		async with wastedsession.get(f"https://some-random-api.ml/canvas/horny/?avatar={member.avatar_url_as(format='png')}") as img:
			if img.status != 200:
				await ctx.send("Unable to get image")
				await wastedsession.close()      
			else:
				data = io.BytesIO(await img.read())
				await ctx.send(file=discord.File(data, f'horny.png'))
			await wastedsession.close()


	@command(name="lolijail")
	async def lolice(self, ctx, *, member: discord.Member=None):
		if not member:
			member = ctx.author
				
		wastedsession = aiohttp.ClientSession()
		async with wastedsession.get(f"https://some-random-api.ml/canvas/lolice/?avatar={member.avatar_url_as(format='png')}") as img:
			if img.status != 200:
				await ctx.send("Unable to get image")
				await wastedsession.close()      
			else:
				data = io.BytesIO(await img.read())
				await ctx.send(file=discord.File(data, f'lolice.png'))
			await wastedsession.close()

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
		await ctx.message.delete()
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

	@command(name="godzuki")
	async def zuki(self, ctx):

		path = choice(os.listdir("./data/images/godz/"))
		await ctx.send(file=File(f"./data/images/godz/{path}"))

	@command(name="owoify")
	async def owoify(self, ctx, *, x):
		await ctx.message.delete()
		await ctx.send(x.lower().replace("l", "w").replace("r", "w").replace("s", "sh")+ " OwO")
	
	# @command(name="smol")
	# async def smolify(self, ctx, *, x):
	# 	await ctx.message.delete()
	# 	await ctx.send(x.lower().replace("a", "\:regional_indicator_a:").replace("b", "\:regional_indicator_b:")
	# 	.replace("c", "\:regional_indicator_c:").replace("d", "\:regional_indicator_d:").replace("e", "\:regional_indicator_e:")
	# 	.replace("f", "\:regional_indicator_f:").replace("g", "\:regional_indicator_g:").replace("h", "\:regional_indicator_h:")
	# 	.replace("i", "\:regional_indicator_i:").replace("j", "\:regional_indicator_j:").replace("k", "\:regional_indicator_k:")
	# 	.replace("l", "\:regional_indicator_l:").replace("m", "\:regional_indicator_m:").replace("n", "\:regional_indicator_n:")
	# 	.replace("o", "\:regional_indicator_o:").replace("p", "\:regional_indicator_p:").replace("q", "\:regional_indicator_q:")
	# 	.replace("r", "\:regional_indicator_r:").replace("s", "\:regional_indicator_s:").replace("t", "\:regional_indicator_t:")
	# 	.replace("u", "\:regional_indicator_u:").replace("v", "\:regional_indicator_v:").replace("w", "\:regional_indicator_w:")
	# 	.replace("x", "\:regional_indicator_x:").replace("y", "\:regional_indicator_y:").replace("z", "\:regional_indicator_z:"))

	@command(name="beer")
	async def beerbrew(self, ctx):
		await ctx.send(":beer:")

	# @command(name="stupid")
	# async def stup(self, ctx, *, member: discord.Member=None,  dog):
	# 	if not member:
	# 		member = ctx.author
		
	# 	wastedsession = aiohttp.ClientSession()
	# 	async with wastedsession.get(f'https://some-random-api.ml/canvas/its-so-stupid/?avatar={member.avatar_url_as(format="png")}') as img:
	# 		if img.status != 200:
	# 			await ctx.send("Unable to get image")
	# 			await wastedsession.close()
	# 			data = await       
	# 		else:
	# 			dog = data["dog"]
	# 			read = io.BytesIO(await img.read())

	# 			await ctx.send(file=discord.File(read, f'its-so-stupid.png&{dog}'))
	# 		await wastedsession.close()

	
	@command(name="binary")
	@cooldown(3, 180, BucketType.user)
	async def bian(self, ctx, *, text):
		bi_url = f"https://some-random-api.ml/binary?text={text}"

		async with request("GET", bi_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()
				encode = data["binary"]


			for chunk in [encode[i : i + 2000] for i in range(0, len(encode), 2000)]:
				await ctx.send(chunk)

	@command(name="decodebinary", aliases = ["deb"])
	@cooldown(3, 180, BucketType.user)
	async def debian(self, ctx, *, text):
		bi_url = f"https://some-random-api.ml/binary?decode={text}"

		async with request("GET", bi_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()
				decode = data["text"]

				await ctx.send(decode)


	@command(name="time", aliases=["clock", "date"])
	async def clocker(self, ctx):
		now = datetime.now()
		num = now.strftime("%I")

		current_time = now.strftime("Date: %d:%A/%m:%B/%Y \nTime: %I hr:%M mins:%S secs %p \nDay %j out of 365 \nWeek %U out of 52 \nMonth %m out of 12")

		embed = Embed(title = f"Time :clock{int(num)}:")
					
		fields = [("It is", current_time, False)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)
			
		embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

		await ctx.send(embed=embed)

	@command(name="joke")
	@cooldown(3, 180, BucketType.user)
	async def funny_quote(self, ctx):
		quote_url = "https://some-random-api.ml/joke"

		async with request("GET", quote_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()
				sen = data["joke"]

				embed = Embed(title=f"Joke",
							  description=f"{sen}",
							  timestamp=datetime.utcnow(),
							  color=ctx.author.color)
				await ctx.send(embed=embed)


			else:
				await ctx.send(f"API returned a {response.status} status.")

	@command(name="token")
	async def tok_quote(self, ctx):
		quote_url = "https://some-random-api.ml/bottoken"

		async with request("GET", quote_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()
				sen = data["token"]

				embed = Embed(title=f"Bot token",
							  description=f"{sen}",
							  timestamp=datetime.utcnow(),
							  color=ctx.author.color)
				await ctx.send(embed=embed)


			else:
				await ctx.send(f"API returned a {response.status} status.")

	@command(name="minecraft", aliases=['mc'])
	async def mc_member(self, ctx, name):
		mc_url = f"https://some-random-api.ml/mc?username={name}"

		async with request("GET", mc_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()
				us = data["username"]
				uuid = data["uuid"]
				history = data["name_history"]
				old_name = history[0]
				info_num = len(history)
				if int(info_num) >= 2:
					now_name = history[1]
					x = now_name["changedToAt"]
					y = old_name["name"]

				else:
					x = "Never"
					y = "Original name"

				#changedate = change["changedToAt"]

				pfp = f"https://crafatar.com/renders/body/{uuid}?overlay=true"

				try:
					embed= Embed(title=f"{us} Minecraft Info",
						color=ctx.author.color,
						timestamp=datetime.utcnow())

					fields =  [("Username", us, False),
							   ("UUID", uuid, False),
							   ("Original name", y, False),
							   ("Change date", x, False)]

					for name, value, inline in fields:
			 			embed.add_field(name=name, value=value, inline=inline)
					
					embed.set_thumbnail(url=pfp)
					embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

					await ctx.send(embed=embed)

				except:
					await ctx.send("No get a different bot")

	@command(name="pokemon", aliases=['poke'])
	async def pokemon_info(self, ctx, name):
		mc_url = f"https://some-random-api.ml/pokedex?pokemon={name}"

		async with request("GET", mc_url, headers=[]) as response:
			if response.status == 200:
				data = await response.json()
				nam = data["name"]
				pid = data["id"]
				ptype = data["type"]
				species = data["species"]
				height = data["height"]
				weight = data["weight"]




				try:
					embed= Embed(title=f"{nam} Podedex Info",
						color=ctx.author.color,
						timestamp=datetime.utcnow())

					fields =  [("Pokemon Name", nam, False),
							   ("Number", pid, False),
							   ("Type", ptype, False),
							   ("Species", species, False),
							   ("Height", height, False),
							   ("Weight", weight, False)]

					for name, value, inline in fields:
			 			embed.add_field(name=name, value=value, inline=inline)
					
					embed.set_thumbnail(url=f"http://i.some-random-api.ml/pokemon/{nam}.gif")
					embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

					await ctx.send(embed=embed)

				except:
					pass

	

	@command(name="adios")
	async def leave_server(self, ctx):
		await ctx.message.delete() 
		await ctx.guild.leave()

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("fun")

def setup(bot):
	bot.add_cog(Fun(bot))