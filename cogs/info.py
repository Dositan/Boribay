import discord
from typing import Optional
from utils.CustomEmbed import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command, guild_only
import psutil as p
import matplotlib.pyplot as plt
from humanize import time


class Info(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command()
	async def uptime(self, ctx):
		hours, remainder = divmod((await self.bot.get_uptime()), 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		embed = Embed().add_field(
			name='Uptime',
			value=f'{days}d, {hours}h {minutes}m {seconds}s'
		)
		return await ctx.send(embed=embed)

	@command(name="botinfo", aliases=['bi', 'about'], brief='see some information about me.')
	async def _bot_info(self, ctx):
		servers = self.bot.guilds
		embed = Embed(title=f"{self.bot.user.name} Info").set_image(url='https://cdn.discordapp.com/attachments/381963689470984203/789812779040636928/ph.png')
		fields = [
			('Invite link', f'[Here]({self.bot.invite_url})'),
			('GitHub', f'[Here]({self.bot.github_url})'),
			('Support', f'[Here]({self.bot.support_url})'),
			('Latency', f'{round(self.bot.latency * 1000)}ms'),
			('Memory', f'{round(p.virtual_memory().used/(1024**3), 2)}GB of {round(p.virtual_memory().total/(1024**3), 2)}GB'),
			('CPU', f"{p.cpu_percent(interval=1)}%"),
			('Owner', f'[{self.bot.dosek}]({self.bot.owner_url})'),
			('Currently in', f'{len(servers)} servers'),
			('Prefix', f'{ctx.prefix}'),
			('Uptime', f'{time.precisedelta(await self.bot.get_uptime(), minimum_unit="seconds")}'),
			('Commands', f'{len(self.bot.commands)}')
		]
		for name, value in fields:
			embed.add_field(name=name, value=value)
		await ctx.send(embed=embed)

	@command(name="userinfo", aliases=["memberinfo", "ui", "mi"], brief="displays user information")
	@guild_only()
	async def user_info(self, ctx, target: Optional[discord.Member]):
		target = target or ctx.author
		embed = Embed(title="User information", color=target.color)
		embed.set_thumbnail(url=target.avatar_url)
		fields = [
			("Name", f'{target.name}<:bot_tag:596576775555776522>' if target.bot else target.name, True),
			("Top role", target.top_role.mention, True),
			("Status", str(target.status).title(), True),
			("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
			("Boosted server", bool(target.premium_since), False),
			("Account created", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
			("Here since", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True)
		]
		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)
		await ctx.send(embed=embed)

	@command(name="serverinfo", aliases=["guildinfo", "si", "gi"], brief="displays server information")
	@guild_only()
	async def server_info(self, ctx):
		embed = Embed(title=f'{ctx.guild.name} info.').set_thumbnail(url=ctx.guild.icon_url)
		statuses = [
			len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
			len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
			len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
			len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))
		]

		labels = 'Offline', 'Idle', 'Online', 'DND'
		sizes = [statuses[3], statuses[1], statuses[0], statuses[2]]
		explode = (0.1, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

		fig1, ax1 = plt.subplots()
		ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
		ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
		plt.savefig(fname='./images/server.png')
		f = discord.File('./images/server.png')
		embed.set_image(url='attachment://server.png')
		fields = [
			("Owner", ctx.guild.owner, True),
			("Region", ctx.guild.region, True),
			("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
			("Members", len(ctx.guild.members), True),
			("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
			("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
			("Boosts", ctx.guild.premium_subscription_count, True),
			("Guild Icon", f'[Here]({ctx.guild.icon_url})', True),
			("Roles", len(ctx.guild.roles), True),
			("Text channels", len(ctx.guild.text_channels), True),
			("Voice channels", len(ctx.guild.voice_channels), True),
			("Categories", len(ctx.guild.categories), True),
		]
		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(file=f, embed=embed)


def setup(bot):
	bot.add_cog(Info(bot))
