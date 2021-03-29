import asyncio
from typing import Optional

import random as rand
from random import choice, randint
from aiohttp import request
from discord import Member, Embed, File, Message, NotFound, Object
from discord.ext.commands import Cog
from discord.ext.commands import BadArgument 
from discord.ext.commands import command, cooldown
from datetime import datetime, timedelta
import discord, requests

from re import search

from better_profanity import profanity
from discord.errors import HTTPException, Forbidden 

from discord.utils import find

from discord.ext.commands import CheckFailure, BadArgument
from discord.ext.commands import command, has_permissions, bot_has_permissions
from discord.ext.commands import MissingPermissions
class Games(Cog):
	def __init__(self, bot):
		self.bot = bot
		self.number_guessing_running = False
		self.rps_running = False

	def is_int(self, s: str) -> bool:
		try:
			int(s)
			return True
		except ValueError:
			return False

	@command(name="numguess", aliases=["ng"], brief="Guess a number\n Credit: Xhiro#0177")
	async def number_guessing(self, ctx, x: int = 1, y: int = 100):
		key = rand.randint(x, y)

		self.number_guessing_running = True
		guesses = guess_max = 10

		await ctx.send(f"Guess a number between {x} and {y}!")

		while self.number_guessing_running and guesses > 0:
			try:
				guess = int((await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and self.is_int(m.content.strip()), timeout=15.0)).content.strip())

			except asyncio.TimeoutError:
				return await ctx.send(f"Too slow. The answer was {key}")

			if key == guess:
				self.num_guess_running = False
				await ctx.send(f"Correct! You guessed {guess}.")
				return
			elif key < guess:
				await ctx.send(f"Too high! You have {guesses}/{guess_max} guesses left.")
			elif key > guess:
				await ctx.send(f"Too low! You have {guesses}/{guess_max} guesses left.")
			guesses -= 1
		await ctx.send(f"You couldn't guess the correct number, you lose! The answer was {key}")


	@command(name="yahtzee", aliases=["yaht", "yz"])
	async def yaht(self, ctx):
		dice = [0,0,0,0,0]
		for i in range(5):
			dice[i] = rand.randint(1, 6)
		await ctx.send(f"You rolled: {dice}")

		dice.sort()

		if dice[0] == dice[4]:
			await ctx.send("Yahtzee")

		elif (dice[0] == dice[3]) or (dice[1] == dice[4]):
			await ctx.send("Four of a kind")

		elif ((dice[0]) == dice[2]) or ((dice[1]) == dice[3]) or ((dice[2]) == dice[4]):
			await ctx.send("Three of a kind")

		else:
			await ctx.send("Roll again")

	@command(name="cardwar", aliases=["cw"])
	async def card_war(self, ctx):
		faces = ["two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "jack", "queen", "king", "ace"]
		suits = ["clubs", "dimonds", "hearts", "spades"]
		my_face = choice(faces)
		my_suit = choice(suits)
		your_face = choice(faces)
		your_suit = choice(suits)
		
		if faces.index(my_face) > faces.index(your_face):
			await ctx.send(f"I have a {my_face} of {my_suit}") 
			await ctx.send(f"You have a {your_face} of {your_suit}") 
			await ctx.send("I win!")

		elif faces.index(my_face) < faces.index(your_face):
			await ctx.send(f"I have a {my_face} of {my_suit}") 
			await ctx.send(f"You have a {your_face} of {your_suit}") 
			await ctx.send("You win!")
		
		else:
			await ctx.send(f"I have a {my_face} of {my_suit}") 
			await ctx.send(f"You have a {your_face} of {your_suit}") 
			await ctx.send("Draw")  



	@command(name="rps")
	async def rock_paper_scissors(self, ctx):
		ob = ['Rock', 'Paper', 'Scissors']
		my_pick  = str(choice(ob))
		await ctx.send("Respond with `Rock`, `Paper`, or `Scissors`!")


		self.rps_running = True
		try:
			your_pick = str((await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content.strip(), timeout=15.0)).content.capitalize())

		except asyncio.TimeoutError:
				return await ctx.send(f"Too slow.")

		while self.rps_running == True:
					
			if your_pick == my_pick:
				await ctx.send("Tie!")
				self.rps_running = False 

			elif your_pick == "Rock":
				if my_pick == "Paper":
					await ctx.send(f"You lose! {my_pick} covers {your_pick}")
					self.rps_running = False 

				else:
					await ctx.send(f"You win! {your_pick} smashes {my_pick}")
					self.rps_running = False 

			elif your_pick == "Paper":
				if my_pick == "Scissors":
					await ctx.send(f"You lose! {my_pick} cuts {your_pick}")
					self.rps_running = False 

				else:
					await ctx.send(f"You win! {your_pick} covers {my_pick}")
					self.rps_running = False 

			elif your_pick == "Scissors":
				if my_pick == "Rock":
					await ctx.send(f"You lose. {my_pick} smashes {your_pick}")
					self.rps_running = False 

				else:
					await ctx.send(f"You win! {your_pick} cut {my_pick}")
					self.rps_running = False 			





		
			





	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("games")

def setup(bot):
	bot.add_cog(Games(bot))

	