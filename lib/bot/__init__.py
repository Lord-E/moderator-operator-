from asyncio import sleep
from datetime import datetime
from glob import glob

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File
from discord.errors import HTTPException, Forbidden 
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)

from discord.ext.commands import when_mentioned_or
from ..db import db

PREFIX = "op."
OWNER_IDS = [717486310566133844]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
    return when_mentioned_or(PREFIX)(bot, message)



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
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()


        db.autosave(self.scheduler) 
        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")
        
        print("setup complete")

    def run(self, version):
        self.VERSION = version

        print("running setup")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("I'm not read to recieve commands. Please wait a few seconds.")

    async def rules_reminder(self):
        await self.stdout.send("You know the rules and so do I")

    async def on_connect(self):
        print(" bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")
            
        
        await self.stdout.send("`An error occured.`")
        raise


    async def on_command_error(self, ctx, exc):
        if any([isinstance( exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
            
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more arguments are missing")

        elif isinstance(exc, CommandOnCooldown):
            embed = Embed(title="2, 4, 6, 8, you should really decelerate", color=ctx.author.color, timestamp= datetime.utcnow())
            fields = [(( "\u200b"), ( f"That command in on `{str(exc.cooldown.type).split('.')[-1]}` cooldown. Try again in `{exc.retry_after:,.2f}` secs."), True)]
            
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=True)            
            await self.stdout.send(embed=embed)
            

        elif hasattr(exc, "original"):

        # elif isinstance(exc.original, HTTPException):
        #     await ctx.send("Unable to send message.")

            if isinstance(exc.original, Forbidden):
                await ctx.send("Unable to send message.")

            else:
                raise exc.original
            
        else:
            raise exc


    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(761766200555995147)
            self.stdout = self.get_channel(762507751535804436)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()



            # embed = Embed(title="This is the title", description="Discription", 
            #     color=0xB8821F, timestamp= datetime.utcnow())
            # fields = [("True Name", "True Value", True),
            #           ("True Name 2", "True Value 2", True),
            #           ("False Name 3", "False Value 3", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=True)
            #     embed.set_author(name="Author", icon_url=self.guild.icon_url)
            #     embed.set_footer(text="Footer")
            #     embed.set_thumbnail(url=self.guild.icon_url)
            #     embed.set_image(url=self.guild.icon_url)            
            # await channel.send(embed=embed)

            # await channel.send(file=File("./data/images/giphy.gif"))
            
            while not self.cogs_ready.all_ready():
                await sleep(0.5)            

            await self.stdout.send("`Bot online`")
            self.ready = True
            print(" bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

bot = Bot()