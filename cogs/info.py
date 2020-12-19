from datetime import datetime
import discord
from typing import Optional
from discord import Embed, Member
from discord.ext.commands import Cog
from discord.ext.commands import command
import psutil as p


class Info(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="botinfo", aliases=['bi', 'about'], brief='see some information about me.')
	async def _bot_info(self, ctx):
		servers = self.bot.guilds

		bi_embed = Embed(title=f"{self.bot.user.name} Info", color=discord.Color.dark_theme())
		fields = [
			("Invite link", '[Here](https://discord.com/api/oauth2/authorize?client_id=735397931355471893&permissions=8&scope=bot)'),
			("GitHub", '[Here](https://github.com/Dositan/boribay/)'),
			("Support", '[Here](https://discord.gg/cZy6TvDg79)'),
			("Latency", f'{round(self.bot.latency * 1000)}ms'),
			("Memory", f'{round(p.virtual_memory().used/(1024**3), 2)}GB of {round(p.virtual_memory().total/(1024**3), 2)}GB'),
			("CPU", f"{p.cpu_percent(interval=1)}%"),
			("Owner", f'[Dosek](http://discord.com/users/682950658671902730)'),
			("Currently in", f'{len(servers)} servers'),
			("Prefix", f'{ctx.prefix}')
		]
		for name, value in fields:
			bi_embed.add_field(name=name, value=value)

		await ctx.send(embed=bi_embed)

	@command(name="userinfo", aliases=["memberinfo", "ui", "mi"], brief="displays user information")
	async def user_info(self, ctx, target: Optional[Member]):
		target = target or ctx.author

		ui_embed = Embed(title="User information", color=target.color if hash(target.color) != 0 else discord.Color.dark_theme(), timestamp=datetime.utcnow())

		ui_embed.set_thumbnail(url=target.avatar_url)

		fields = [
			("Name", f'{target.name}<:bot_tag:596576775555776522>' if target.bot else target.name, False),
			("Top role", target.top_role.mention, False),
			("Status", str(target.status).title(), False),
			("Activity", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", False),
			("Account created", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), False),
			("Here since", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), False),
			("Boosted server", bool(target.premium_since), False)
		]
		for name, value, inline in fields:
			ui_embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=ui_embed)

	@command(name="serverinfo", aliases=["guildinfo", "si", "gi"], brief="displays server information")
	async def server_info(self, ctx):
		serv_embed = Embed(
			title="Server information",
			color=discord.Color.dark_theme(),
			timestamp=datetime.utcnow()
		).set_thumbnail(url=ctx.guild.icon_url)

		statuses = [
			len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
			len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
			len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
			len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))
		]

		fields = [
			("Owner", ctx.guild.owner, True),
			("Region", ctx.guild.region, True),
			("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
			("Members", len(ctx.guild.members), True),
			("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
			("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
			("Statuses", f"<:status_online:596576749790429200>{statuses[0]} <:status_idle:596576773488115722>{statuses[1]} <:status_dnd:596576774364856321>{statuses[2]} <:status_offline:596576752013279242>{statuses[3]}", False),
			("Text channels", len(ctx.guild.text_channels), True),
			("Voice channels", len(ctx.guild.voice_channels), True),
			("Categories", len(ctx.guild.categories), True),
			("Roles", len(ctx.guild.roles), True),
		]
		for name, value, inline in fields:
			serv_embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=serv_embed)


def setup(bot):
	bot.add_cog(Info(bot))
