from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, DMChannel
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
								  CommandOnCooldown, MissingPermissions)
from discord.ext.commands import when_mentioned_or, command, has_permissions
from discord import Intents 
from ..db import db

OWNER_IDS = [717486310566133844]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
	return when_mentioned_or(prefix)(bot, message)


class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
	def __init__(self):
		self.ready = False
		self.cogs_ready = Ready()

		self.guild = None
		self.scheduler = AsyncIOScheduler()

		try:
			with open("./data/banlist.txt", "r", encoding="utf-8") as f:
				self.banlist = [int(line.strip()) for line in f.readlines()]
		except FileNotFoundError:
			self.banlist = []

		db.autosave(self.scheduler)
		super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=Intents.all())

	def setup(self):
		for cog in COGS:
			self.load_extension(f"lib.cogs.{cog}")
			print(f" {cog} cog loaded")

		print("setup complete")

	def update_db(self):
		db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
					 ((guild.id,) for guild in self.guilds))

		db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
					 ((member.id,) for member in self.guild.members if not member.bot))

		to_remove = []
		stored_members = db.column("SELECT UserID FROM exp")
		for id_ in stored_members:
			if not self.guild.get_member(id_):
				to_remove.append(id_)
		

		stored_guilds = db.column("SELECT GuildID FROM guilds")
		for guildid_ in stored_guilds:
			if not self.get_guild(guildid_):
				to_remove.append(guildid_)

		db.multiexec("DELETE FROM exp WHERE UserID = ?",
					 ((id_,) for id_ in to_remove))

		db.multiexec("DELETE FROM guilds WHERE GuildID = ?",
				((guildid_,) for guildid_ in to_remove))

		db.commit()

	def run(self, version):
		self.VERSION = version

		print("running setup...")
		self.setup()

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
			self.TOKEN = tf.read()

		print("running bot...")
		super().run(self.TOKEN, reconnect=True)

	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)

		if ctx.command is not None and ctx.guild is not None:
			if message.author.id in self.banlist:
				await ctx.send("You are banned from using commands.")

			elif not self.ready:
				await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

			else:
				await self.invoke(ctx)

	async def rules_reminder(self):
		await self.stdout.send("")

	async def on_connect(self):
		print(" bot connected")

	async def on_disconnect(self):
		print("bot disconnected")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong.")



		await self.stdout.send("``An error occured.``")
		raise




		

	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send(embed=Embed(description="One or more required arguments are missing.", delete_after=5))
		
		elif isinstance(exc, TimeoutError):
			await ctx.send(embed=Embed(description="Timed out. Try again", delete_after=5))

		elif isinstance(exc, MissingPermissions):
			await ctx.send(embed=Embed(description="You do not have permmission to use this command", delete_after=5))


		elif isinstance(exc, CommandOnCooldown):
			await ctx.send(embed=Embed(description=f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in ``{exc.retry_after:,.2f}`` secs.", delete_after=5))

		elif hasattr(exc, "original"):
			# if isinstance(exc.original, HTTPException):
			# 	await ctx.send("Unable to send message.")

			if isinstance(exc.original, Forbidden):
				await ctx.send(embed=Embed(description="I do not have permission to do that.", delete_after=5))

			else:
				raise exc.original

		else:
			raise exc

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(761766200555995147)
			self.stdout = self.get_channel(762507751535804436)
			self.dm_channel = self.get_channel(828725126279069767)
			self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
			self.scheduler.start()

			self.update_db()

			# embed = Embed(title="Now online!", description="Carberretta is now online.",
			# 			  colour=0xFF0000, timestamp=datetime.utcnow())
			# fields = [("Name", "Value", True),
			# 		  ("Another field", "This field is next to the other one.", True),
			# 		  ("A non-inline field", "This field will appear on it's own row.", False)]
			# for name, value, inline in fields:
			# 	embed.add_field(name=name, value=value, inline=inline)
			# embed.set_author(name="Carberra Tutorials", icon_url=self.guild.icon_url)
			# embed.set_footer(text="This is a footer!")
			# await channel.send(embed=embed)

			# await channel.send(file=File("./data/images/profile.png"))

			while not self.cogs_ready.all_ready():
				await sleep(0.5)

			await self.stdout.send("`` ███╗   ██╗ ██████╗ ██╗    ██╗     ██████╗ ███╗   ██╗██╗     ██╗███╗   ██╗███████╗ \n  ████╗  ██║██╔═══██╗██║    ██║    ██╔═══██╗████╗  ██║██║     ██║████╗  ██║██╔════╝ \n  ██╔██╗ ██║██║   ██║██║ █╗ ██║    ██║   ██║██╔██╗ ██║██║     ██║██╔██╗ ██║█████╗ \n  ██║╚██╗██║██║   ██║██║███╗██║    ██║   ██║██║╚██╗██║██║     ██║██║╚██╗██║██╔══╝ \n  ██║ ╚████║╚██████╔╝╚███╔███╔╝    ╚██████╔╝██║ ╚████║███████╗██║██║ ╚████║███████╗ \n  ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝      ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝``")
			self.ready = True
			print(" bot ready")

			meta = self.get_cog("Meta")
			await meta.set()

		else:
			print("bot reconnected")


	async def on_message(self, message):
		member = self.guild.get_member(message.author.id)
		if not message.author.bot:
			if int(message.channel.id) == 837453025932738610:
				f = open("./data/number.txt", "r")
				num = int(f.read())


				x = message.content
				# messages = await message.channel.history(limit=200).flatten()
				if x.isdigit():
				# 	for mess in messages:
				# 		if mess != str(num):
				# 			await message.delete()
					if int(x) == num:
						num += 1 
						f = open("./data/number.txt", "w")
						f.write(str(num))
						f.close()

					else:
						await message.delete()

				else:
					await message.delete()
#------------------------------------------------------------------------------------------------------------------------------------------------------------
			if isinstance(message.channel, DMChannel):
				if message.content.startswith('op.modmail'):
					if len(message.content) < 50:
						await message.channel.send(embed=Embed(description="Your message needs to be 50 characters or more"))
					
					elif len(message.content) > 1000:
						await message.channel.send(embed=Embed(description="Your message needs to be below 1000 characters (Put it in parts if you need to)"))


					else:
						embed = Embed(title="Modmail",
									colour=0x03fcbe,
									timestamp=datetime.utcnow())
						try:
							url = member.avatar_url()
						except:
							url = 'https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/91_Discord_logo_logos-512.png'

						embed.set_thumbnail(url=url)

						fields = [("Member", f"{member.name}#{member.discriminator}", False),
								  ("Id", member.id, False),
								  ("Message", str(message.content).replace("op.modmail", "Dear Moderator,\n"), False)]

						for name, value, inline in fields:
							embed.add_field(name=name, value=value, inline=inline)
						
						mod = self.get_cog("Mod")
						await mod.mail_channel.send(embed=embed)
						await message.channel.send("Message relayed to moderators.")
#------------------------------------------------------------------------------------------------------------------------------------------------------------
				elif message.content.startswith('op.help'):
					await message.channel.send(f"You need help")
#------------------------------------------------------------------------------------------------------------------------------------------------------------
				
				
				else:
					await self.dm_channel.send(f"{message.author}  --> {message.content}")
			


			else:
				await self.process_commands(message)


bot = Bot()