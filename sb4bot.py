from MeowerBot import Bot
from MeowerBot.context import Context, Post

import logging, random, json as j, requests, time

from dotenv import load_dotenv # type: ignore

load_dotenv() # type: ignore

from MeowerBot.ext.help import Help as HelpExt

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("websockets.client").setLevel(level=logging.INFO)

bot = Bot()

class XORShiftGenerator:
	def __init__(self, seed):
		self.state = seed

	def generate(self):
		self.state ^= (self.state << 21)
		self.state ^= (self.state >> 35)
		self.state ^= (self.state << 4)
		return self.state & 0xFFFFFFFFFFFFFFFF

@bot.event
async def login(t):
	print("Logged in!")
	await bot.get_chat("livechat").send_msg("Sb4bot is online!\nTry @Sb4bot help to see my commands!")
	await bot.get_chat("ef25294f-139c-4674-9485-90ddaa0852fd").send_msg("Sb4bot is online!\nTry @Sb4bot help to see my commands!")

@bot.command(name="ping")
async def ping(ctx: Context):
	await ctx.reply("Pong!\nMy latency is " + str(bot.latency * 1000) + " ms")

@bot.command(name="rps")
async def rps(ctx: Context):
	await ctx.reply("Add rock, paper, scissors to tell me your choice")

@rps.subcommand(name="rock")
async def rock(ctx: Context):
	choice = ["rock", "paper", "scissors"][random.randint(0, 2)]
	if choice == "rock":
		await ctx.reply("Rock vs Rock. Tie. gg")
	elif choice == "paper":
		await ctx.reply("Paper vs Rock. I win! gg")
	else:
		await ctx.reply("Scissors vs Rock. You win. gg")

@rps.subcommand(name="paper")
async def paper(ctx: Context):
	choice = ["rock", "paper", "scissors"][random.randint(0, 2)]
	if choice == "rock":
		await ctx.reply("Rock vs Paper. You win. gg")
	elif choice == "paper":
		await ctx.reply("Paper vs Paper. Tie. gg")
	else:
		await ctx.reply("Scissors vs Paper. I win! gg")

@rps.subcommand(name="scissors")
async def scissors(ctx: Context):
	choice = ["rock", "paper", "scissors"][random.randint(0, 2)]
	if choice == "rock":
		await ctx.reply("Rock vs Scissors. I win! gg")
	elif choice == "paper":
		await ctx.reply("Paper vs Scissors. You win. gg")
	else:
		await ctx.reply("Scissors vs Scissors. Tie. gg")

global rclass
rclass = XORShiftGenerator(random.randint(1, 2 ** 32))
@bot.command(name="rnumber")
async def rnumber(ctx: Context, *bounds: str):
	x = " ".join(bounds) + " "
	k = ""
	minimum = None
	maximum = None

	for i in range(0, len(x)):
		k += x[i]
		if x[i] == " ":
			if not minimum:
				minimum = int(k[:len(k) - 1])
			elif not maximum:
				maximum = int(k[:len(k) - 1])
			else:
				break
			k = ""

	global rnum, rclass
	rnum = rclass.generate()
	rnum = rnum % (maximum - minimum + 1) + minimum

	if "hidden" not in x:
		await ctx.reply(f"The number is {rnum}")
	else:
		await ctx.reply("Use @Sb4bot reveal when you want the number revealed")

@bot.command(name="reveal")
async def reveal(ctx: Context):
	global rnum
	await ctx.reply(f"The number is {rnum}")

@bot.command(name="whois")
async def whois(ctx: Context, *username: str):
	x = requests.get(f"https://api.meower.org/users/{" ".join(username)}").json()
	try:
		if x["banned"]:
			banned = "Deceased"
		else:
			banned = "Exists"
	
		created = time.localtime(x["created"])
		ampm = "AM"
		month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][created.tm_mon - 1]

		hour = created.tm_hour
		if hour > 12:
			ampm = "PM"
			hour -= 12
    
		minute = created.tm_min
		if minute < 10:
			minute = f"0{minute}"
    
		second = created.tm_sec
		if second < 10:
			second = f"0{second}"

		created = f"Born on {month} {created.tm_mday}, {created.tm_year} at {hour}:{minute}:{second} {ampm}"
		await ctx.reply(f"\n-- [ {x["_id"]} ] --\n{banned}\n{created}\nLevel {x["lvl"]}\nPermissions: {x["permissions"]}\nPFP #{x["pfp_data"]}\nQuote: {x["quote"]}")
	except:
		await ctx.reply("Did not find username. Are you confusing a Discord username with a Meower username (what you need to use)?")

@bot.command(name="economy")
async def economy(ctx: Context):
	await ctx.reply("This command requires a subcommand to work.\n@Sb4bot help for the commands")

@economy.subcommand(name="work")
async def add(ctx: Context):
	with open("example.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		if ctx.message.user.username in data["example"]:
			await ctx.send_msg("sorry, but you can't use this command")
			return "not allowed"
	
	with open("economy.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		usern = ctx.message.user.username
		print(usern)
		try:
			_ = data[f"{usern}-next"]
		except:
			data[f"{usern}-next"] = time.time() - 1
			f.seek(0)

		try:
			_ = data[f"{usern}-inventory"]
		except:
			data[f"{usern}-inventory"] = []
	
		if time.time() > data[f"{usern}-next"]:
			amount = random.randint(1, 80)
			try:
				data[f"{usern}-money"] += amount
				f.seek(0)
				await ctx.reply(f"${amount} has been added to your total!")
			except:
				data[f"{usern}-money"] = amount
				f.seek(0)
				await ctx.reply(f"${amount} has been added to your total!")
			data[f"{usern}-next"] = time.time() + 180
			j.dump(data, f, indent=4)
			f.truncate()
		else:
			await ctx.reply(f"You must wait {round(data[f"{usern}-next"] - time.time())} seconds before working again")

@economy.subcommand(name="remove")
async def remove(ctx: Context):
	with open("economy.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		usern = ctx.message.user.username
		data.pop(f"{usern}-money")
		f.seek(0)
		data.pop(f"{usern}-next")
		f.seek(0)
		data.pop(f"{usern}-inventory")
		f.seek(0)
		j.dump(data, f, indent=4)
		f.truncate()
		await ctx.reply("You have been removed from the economy!\nIf you want to begin again, just use the add subcommand.")

@economy.subcommand(name="balance")
async def amount(ctx: Context):
	with open("economy.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		usern = ctx.message.user.username
		await ctx.reply(f"You have ${data[f"{usern}-money"]}!")

@economy.subcommand(name="shop")
async def shop(ctx: Context):
	await ctx.reply("You may buy the following things:\n\t\twater - $3\n\t\teggs - $5\n\t\tfrench toast - $10\n\t\tsoup - $20\n\t\tturkey dinner - $60\n\t\tNFT - $2,000\n\t\tadmin cmds - $100,000")

@shop.subcommand(name="inventory")
async def inventory(ctx: Context):
	with open("economy.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		usern = ctx.message.user.username
		await ctx.reply(f"You have the following items:\n{", ".join(data[f"{usern}-inventory"])}")

global items
items = {
	"water": 3,
	"eggs": 5,
	"french toast": 10,
	"soup": 20,
	"turkey dinner": 60,
	"NFT": 2000,
	"admin cmds": 100000
}

@shop.subcommand(name="buy")
async def buy(ctx: Context, *item: str):
	global items
	noitem = True
	global bought
	bought = False
	for i in items:
		if i in " ".join(item):
			with open("economy.json", "r+") as f:
				f.seek(0)
				data = j.load(f)
				usern = ctx.message.user.username
				if data[f"{usern}-money"] > items[i] - 1:
					data[f"{usern}-money"] -= items[i]
					data[f"{usern}-inventory"].append(i)
					f.seek(0)
					j.dump(data, f, indent=4)
					f.truncate()
					bought = True
				else:
					await ctx.reply("sorry, you don't have enough money for that item")
				
				noitem = False
			
			break
	
	if noitem:
		await ctx.reply("please specify what you want to buy")
	elif bought:
		await ctx.reply(f"Successfully bought {" ".join(item)} for ${items[i]}.")

@shop.subcommand(name="sell")
async def sell(ctx: Context, *item: str):
	usern = ctx.message.user.username
	with open("economy.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		inventory = data[f"{usern}-inventory"]
		try:
			global items
			inventory.pop(data[f"{usern}-inventory"].index(" ".join(item)))
			data[f"{usern}-money"] += items[" ".join(item)]
			f.seek(0)
			j.dump(data, f, indent=4)
			f.truncate()
			await ctx.reply(f"Successfully sold {" ".join(item)} for ${items[" ".join(item)]}.")
		except:
			await ctx.reply("sorry, you don't have that item in your inventory")

@bot.command(name="execute")
async def execute(ctx: Context, *command: str):
	code = ctx.message.data[9:]
	await exec(code)

@bot.command(name="msg")
async def msg(ctx: Context, *message: str):
	with open("admins.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		if ctx.message.user.username in data["admins"]:
			msg = " ".join(message) + " "
			k = ""
			send = None
			chatid = None
			for i in range(len(msg)):
				k += msg[i]
				if msg[i] == " ":
					if not chatid:
						chatid = k[:i]
						send = msg[i + 1:len(msg) - 1]
					else:
						break
			
					k = ""

			if chatid == "this":
				await bot.get_chat("ef25294f-139c-4674-9485-90ddaa0852fd").send_msg(send)
			elif chatid == "h":
				await bot.get_chat("home").send_msg(send)
			elif chatid == "lc":
				await bot.get_chat("livechat").send_msg(send)
			else:	
				await bot.get_chat(chatid).send_msg(send)
		else:
			await ctx.reply("sorry, this command is for admins only")

@bot.command(name="minesweeper")
async def minesweeper(ctx: Context, *bombsanddimensions: str):
	with open("admins.json", "r+") as f:
		f.seek(0)
		data = j.load(f)
		if ctx.message.user.username not in data["admins"]:
			await ctx.reply("this command is admin only")
			return "no access"

	x = " ".join(bombsanddimensions) + " "
	k = ""
	bombs = None
	width = None
	length = None

	for i in range(0, len(x)):
		k += x[i]
		if x[i] == " ":
			if not bombs:
				bombs = int(k[:len(k) - 1])
			elif not width:
				width = int(k[:len(k) - 1])
			elif not length:
				length = int(k[:len(k) - 1])
			else:
				break
			k = ""

	grid = []

	if bombs >= (width * length - 9) or width < 1 or length < 1:
		await ctx.reply("too many bombs for the specified length and width")
		return "stopped"

	grid = [[0 for i in range(width)] for i in range(length)]

	while bombs > 0:
		row = random.randint(0, length - 1)
		column = random.randint(0, width - 1)
		if grid[row][column] != "💣":
			grid[row][column] = "💣"
			bombs -= 1

	for i in range(length * width):
		row = i // width
		column = i % width
		if grid[row][column] == "💣":
			continue

		if row > 0 and column > 0:
			if grid[row - 1][column - 1] == "💣":
				grid[row][column] += 1

		if row > 0:
			if grid[row - 1][column] == "💣":
				grid[row][column] += 1

		if row > 0 and column < width - 1:
			if grid[row - 1][column + 1] == "💣":
				grid[row][column] += 1

		if column > 0:
			if grid[row][column - 1] == "💣":
				grid[row][column] += 1

		if column < width - 1:
			if grid[row][column + 1] == "💣":
				grid[row][column] += 1

		if row < length - 1 and column > 0:
			if grid[row + 1][column - 1] == "💣":
				grid[row][column] += 1

		if row < length - 1:
			if grid[row + 1][column] == "💣":
				grid[row][column] += 1
	
		if row < length - 1 and column < width - 1:
			if grid[row + 1][column + 1] == "💣":
				grid[row][column] += 1

	for i in range(length * width):
		row = i // width
		column = i % width
		if grid[row][column] == 0:
			grid[row][column] = "||0️⃣||"
		elif grid[row][column] == 1:
			grid[row][column] = "||1️⃣||"
		elif grid[row][column] == 2:
			grid[row][column] = "||2️⃣||"
		elif grid[row][column] == 3:
			grid[row][column] = "||3️⃣||"
		elif grid[row][column] == 4:
			grid[row][column] = "||4️⃣||"
		elif grid[row][column] == 5:
			grid[row][column] = "||5️⃣||"
		elif grid[row][column] == 6:
			grid[row][column] = "||6️⃣||"
		elif grid[row][column] == 7:
			grid[row][column] = "||7️⃣||"
		elif grid[row][column] == 8:
			grid[row][column] = "||8️⃣||"
		elif grid[row][column] == "💣":
			grid[row][column] = "||💣||"

	msg = ""
	for i in range(length):
		msg += f"{str("".join(grid[i]))}\n"

	await ctx.reply("\n" + msg)

# make a bot so if there is any message ending in ™️ it adds it to a database with your username
# and if anyone says that word it tells you who trademarked that word
#@bot.listen(Post)
#async def onMessage(message: Post, *words):
#	with open("trademarks.json", "r+") as f:
#		if message.data.endswith("™️"):
#			f.seek(0)
#			x = j.load(f)
#			x[message.data[:len(message.data) - 1]] = message.user.username
#			f.seek(0)
#			j.dump(x, f, indent=4)
#			f.truncate()
		
#		for i in words:
#			if 

@bot.command(name="shut")
async def shut(ctx: Context, *secret: str):
	try:
		global usern
		usern = ctx.message.user.username
	except:
		await ctx.reply("error")

	with open("admins.json", "r+") as f:
		f.seek(0)
		x = j.load(f)
		if ((usern in x["admins"]) or (" ".join(secret) == "private (not actual string)")):
			await ctx.reply("fine")
			exit()
		else:
			await ctx.reply("ain't NO WAY YOU are telling me to SHUT.")

bot.register_cog(HelpExt(bot, disable_command_newlines=True))

json = open('accInfo.json')
data = j.load(json)

user = data["accInfo"][0]["user"]
pswd = data["accInfo"][0]["pass"]

json.close()
bot.run(user, pswd)
