from typing import Optional

from discord import app_commands
from discord.ext import commands
from humanize import naturaldate, naturaltime

from boribay.core import utils

LOADING = "<a:loading:837049644462374935>"
POSTGRES = "<:pg:795005204289421363>"


class Miscellaneous(utils.Cog):
    """The miscellaneous extension.

    Commands that do not match other categories will be inserted here.
    """

    icon = "💫"

    @commands.hybrid_command(name='report')
    @app_commands.describe(content="The content of your report.")
    async def suggest(self, ctx: utils.Context, content: str) -> None:
        """Write a report or suggest an idea to the bot owner."""
        query = "INSERT INTO ideas(content, author_id) VALUES($1, $2);"

        await ctx.bot.pool.execute(query, content, ctx.author.id)
        await ctx.send(
            "✅ Added your suggestion, you will be notified when it will be approved/rejected."
        )

    @commands.hybrid_command()
    async def uptime(self, ctx: commands.Context) -> None:
        """Returns bot's uptime."""
        h, r = divmod((ctx.bot.uptime), 3600)
        (m, s), (d, h) = divmod(r, 60), divmod(h, 24)

        embed = ctx.embed()
        embed.add_field(name="For how long am I online?", value=f"{d}d {h}h {m}m {s}s")

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def about(self, ctx: utils.Context) -> None:
        """Some information about Boribay."""
        bot = ctx.bot
        embed = ctx.embed().set_author(
            name=f"{bot.user} - v2",
            icon_url=bot.user.avatar
        )
        fields = {
            "Development": {
                ("Developer", str(bot.owner)),
                ("Language", "Python"),
                ("Library", "discord.py"),
            },
            "General": {
                ("Currently in", f"{len(bot.guilds)} servers"),
                ("Commands working", f"{len(bot.commands)}"),
                ("Commands usage (last restart)", bot.counter["command_usage"]),
            },
        }
        for key in fields:
            embed.add_field(
                name=key,
                value="\n".join(f"> **{k}:** {v}" for k, v in fields[key]),
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.guild_only()
    @app_commands.describe(member="@ you want to get info about")
    async def info(self, ctx: utils.Context, member: Optional[commands.MemberConverter]) -> None:
        """See some general information about a mentioned user."""
        member = member or ctx.author
        fields = [
            ("Top role", member.top_role.mention),
            ("Boosted server", bool(member.premium_since)),
            ("Account created", naturaldate(member.created_at)),
            ("Here since", naturaldate(member.joined_at)),
        ]

        embed = ctx.embed(
            description="\n".join(f"**{name}:** {value}" for name, value in fields)
        ).set_thumbnail(url=member.avatar)
        embed.set_author(name=str(member), icon_url=ctx.guild.icon)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.guild_only()
    async def serverinfo(self, ctx: utils.Context) -> None:
        """See some general information about current guild."""
        g = ctx.guild

        fields = [
            ("Created", str(g.created_at)),
            ("Members", g.member_count),
            ("Boosts", g.premium_subscription_count),
            ("Roles", len(g.roles)),
            ("Text channels", len(g.text_channels)),
            ("Voice channels", len(g.voice_channels)),
            ("Categories", len(g.categories)),
        ]

        embed = ctx.embed(
            description="\n".join(f"**{n}:** {v}" for n, v in fields)
        ).set_author(name=str(g), icon_url=g.icon)

        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def ping(self, ctx: utils.Context) -> None:
        """Check latency of the bot and its system."""
        fields = (
            (f"{LOADING} Websocket", ctx.bot.latency),
            (f"{POSTGRES} Database", await ctx.db_latency),
        )

        embed = ctx.embed()
        for name, value in fields:
            embed.add_field(
                name=name, value=f"```{value * 1000:.2f} ms```", inline=False
            )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="modules")
    async def cogs(self, ctx: utils.Context) -> None:
        """Get the list of modules the bot offers to use."""
        exts = [str(ext) for ext in ctx.bot.cogs.values()]
        embed = ctx.embed(
            title="Currently working modules.",
            description=f"Currently loaded: {len(ctx.bot.cogs)}",
        ).add_field(name='List of modules', value="\n".join(exts))
        await ctx.send(embed=embed)
