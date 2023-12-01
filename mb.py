from MeowerBot import Bot
from MeowerBot.context import Context
from MeowerBot.cog import Cog
from MeowerBot.command import command

import logging

from dotenv import load_dotenv # type: ignore

load_dotenv() # type: ignore

from os import environ as env
from MeowerBot.ext.help import Help as HelpExt

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("websockets.client").setLevel(level=logging.INFO)

bot = Bot()

@bot.event
async def login(t):
	print("Logged in!")

class Ping(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command()
	async def cog_ping(self, ctx: Context):
		await ctx.send_msg("")

	@cog_ping.subcommand(name="pong")
	async def ping(self, ctx: Context):
		await ctx.send_msg(self.bot.message)

@bot.command(name="ping")
async def ping(ctx: Context):
	await ctx.send_msg("Pong!\nMy latency is: " + str(bot.latency))

@ping.subcommand(name="pong")
async def pong(ctx: Context, *message: str):
	msg = " ".join(message)
	await ctx.send_msg(msg)

bot.register_cog(HelpExt(bot, disable_command_newlines=True))
bot.run("Sb4bot", "A1S2D3F4")