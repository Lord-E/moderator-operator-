import discord, requests, datetime, asyncio, random, os
from discord.ext import commands

class Misc(commands.Cog, name="MiscCommands"):
    def __init__(self, bot):
        self.bot = bot
        self.num_guess_running = False

    @commands.command()
    async def hello(self, ctx, *args):
        mentions = ", ".join(m.mention for m in ctx.message.mentions)
        await ctx.send(f"Hello {mentions}.")

    @commands.command(name="say", aliases=["parrot", "speak", "talk"] )
    async def parrot(self, ctx, *, message: str):
      await ctx.message.delete()
      await ctx.send(message)
    
    @commands.command()
    async def gameexit(self, ctx):
        self.num_guess_running = False

    def is_int(self, s: str) -> bool:
        try:
            int(s)
            return True
        except ValueError:
            return False

    @commands.command()
    async def uploadself(self, ctx):
        await ctx.send(
            file = discord.File(
                open(os.path.join(os.getcwd(), "cogs", "Misc", "Misc.py"), "rb")
            )
        )

    @commands.command()
    async def numguess(self, ctx, x: int = 1, y: int = 100):
        key = random.randint(x, y)
        print(key)
        self.num_guess_running = not self.num_guess_running
        await ctx.send(f"You have 15 seconds to guess a number between {x} and {y}!")
        while self.num_guess_running:
            try:
                guess = int((await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and self.is_int(m.content.strip()), timeout=15.0)).content.strip())
            except asyncio.TimeoutError:
                return await ctx.send("No Response was reported, command timed out.")
            except Exception as err:
                print(err)
                return await ctx.send("Error occured while await user response")
            if guess == key:
                self.num_guess_running = False
                return await ctx.send(f"Correct! You guessed {key}.")




    # base function for api
    async def emotion_base(self, ctx, *,
        member: discord.Member, api: str, format: str):
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
                timestamp=datetime.datetime.utcnow()
            ).set_image(url=gif_url)
        )
        

    @commands.command()
    async def pat(self, ctx, member: discord.Member, *args):
        await self.emotion_base(ctx,
            member=member,
            api="https://some-random-api.ml/animu/pat",
            format="<author> pats <member> " + " ".join(args)
        )

    @commands.command()
    async def hug(self, ctx, member: discord.Member, *args):
        await self.emotion_base(ctx,
            member=member,
            api="https://some-random-api.ml/animu/hug",
            format="<author> hugs <member> " + " ".join(args)
        )

    @commands.command()
    async def mimic(self, ctx, member: discord.Member, *args):
        try:
            wb = await ctx.channel.create_webhook( # create webhook
                name=str(member)[:-5], # cut discriminator
                avatar=requests.get(member.avatar_url).content
            )
        except discord.HTTPException:
            return await ctx.send("Failed to create webhook.")
        except discord.Forbidden:
            return await ctx.send("I do not have permissions to manage webhooks.")
        
        await ctx.message.delete()
        await wb.send(" ".join(args))
        await wb.delete(reason="Mimic Webhook Deleted") # delete the tmp webhook

setup = lambda bot: bot.add_cog( Misc(bot) ) # ok ok look at server lets see