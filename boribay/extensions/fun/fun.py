import os
import asyncio
import random
import textwrap
from io import BytesIO
from time import time
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from boribay.core import Boribay, utils
from boribay.core.utils import make_image, Manip


class Fun(utils.Cog):
    """The fun commands extension."""

    def __init__(self, bot: Boribay):
        self.icon = "🎉"
        self.bot = bot

    async def dagpi_image(self, url: str, fn: str = None) -> discord.File:
        """Quick-Dagpi-image making function.

        Args:
            url (str): The URL of an image.
            fn (str, optional): Filename to take. Defaults to None.

        Returns:
            discord.File: A done to send file.
        """
        r = await self.bot.session.get(
            f"https://api.dagpi.xyz/image/{url}",
            headers={"Authorization": os.environ.get('DAGPI_API_KEY')}
        )
        fp = BytesIO(await r.read())
        return discord.File(fp, fn or "dagpi.png")

    @commands.hybrid_command()
    async def rockpaperscissors(self, ctx: utils.Context) -> None:
        """The Rock-Paper-Scissors game."""
        rps_logic = {
            "🪨": {"🪨": "draw", "📄": "lose", "✂": "win"},
            "📄": {"🪨": "win", "📄": "draw", "✂": "lose"},
            "✂": {"🪨": "lose", "📄": "win", "✂": "draw"},
        }
        choice = random.choice([*rps_logic.keys()])
        embed = ctx.embed(description="**Choose one 👇**")
        msg = await ctx.send(embed=embed.set_footer(text="10 seconds left⏰"))

        for r in rps_logic:
            await msg.add_reaction(r)

        try:
            r, u = await ctx.bot.wait_for(
                "reaction_add",
                timeout=10,
                check=lambda re, us: us == ctx.author
                and str(re) in rps_logic.keys()
                and re.message.id == msg.id,
            )
            game = rps_logic.get(str(r.emoji))
            embed = ctx.embed(
                description=f"Result: **{game[choice].upper()}**\n"
                f"My choice: **{choice}**\n"
                f"Your choice: **{r.emoji}**"
            )
            await msg.edit(embed=embed)

        except asyncio.TimeoutError:
            await ctx.try_delete(msg)

    @commands.hybrid_command()
    @commands.max_concurrency(1, per=commands.BucketType.channel)
    @app_commands.describe(timeout="timer for typing contest")
    async def typeracer(self, ctx: commands.Context, timeout: float = 60.0) -> None:
        """Typeracer game. Compete with others and find out the best typist."""
        if not 10.0 < timeout < 120.0:
            return await ctx.send(
                "Timeout limit has been reached. Please specify between 10 and 120."
            )

        async with ctx.loading:
            r = await ctx.bot.session.get("https://api.quotable.io/random")
            quote = await r.json()
            content = quote["content"]
            buffer = await Manip.typeracer("\n".join(textwrap.wrap(content, 30)))

        embed = ctx.embed(
            title="Typeracer",
            description="see who is the fastest at typing."
        ).set_image(url="attachment://typeracer.png")
        embed.set_footer(text=f'© {quote["author"]}')

        race = await ctx.send(file=discord.File(buffer, "typeracer.png"), embed=embed)
        await race.add_reaction("🗑")
        start = time()

        try:
            done, pending = await asyncio.wait(
                [
                    ctx.bot.wait_for(
                        "raw_reaction_add",
                        check=lambda p: str(p.emoji) == "🗑"
                        and p.user_id == ctx.author.id
                        and p.message_id == race.id,
                    ),
                    ctx.bot.wait_for(
                        "message", check=lambda m: m.content == content, timeout=timeout
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            stuff = done.pop().result()

            if isinstance(stuff, discord.RawReactionActionEvent):
                return await race.delete()

            final = round(time() - start, 2)
            embed = ctx.embed(
                title=f"{stuff.author} won!",
                description=f"**Done in**: {final}s\n"
                f'**Average WPM**: {quote["length"] / 5 / (final / 60):.0f} words\n'
                f"**Original text:**```diff\n+ {content}```",
            )
            await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            await ctx.try_delete(race)

    @commands.hybrid_command()
    async def dadjoke(self, ctx: utils.Context):
        """Get a dadjoke from icanhazdadjoke.com/"""
        resp = await self.bot.session.get(
            "https://icanhazdadjoke.com/",
            headers={"Accept": "text/plain"}
        )
        if resp.status != 200:
            return await ctx.send("Could not fetch the joke. Please try again later!")

        joke = await resp.text()
        embed = ctx.embed(title="Here is yo joke:", description=joke)
        await ctx.send(embed=embed)

    @commands.hybrid_command()
    async def qr(self, ctx: utils.Context, url: Optional[str]) -> None:
        """Generate QR-code for a given URL."""
        url = await make_image(ctx, url, return_url=True)
        r = await ctx.bot.session.get(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}")
        io = BytesIO(await r.read())
        await ctx.send(file=discord.File(io, "qr.png"))

    @commands.hybrid_command()
    @app_commands.describe(image="any kind of image to put caption on it.")
    async def caption(self, ctx: utils.Context, image: Optional[str]) -> None:
        """Get caption for any image."""
        image = await make_image(ctx, image, return_url=True)

        r = await ctx.bot.session.post(
            "https://captionbot.azurewebsites.net/api/messages",
            json={"Content": image, "Type": "CaptionRequest"},
        )
        embed = ctx.embed(title=await r.text())
        await ctx.send(embed=embed.set_image(url=image))

    @commands.hybrid_command()
    @app_commands.describe(image="image to trigger")
    async def triggered(self, ctx: utils.Context, image: Optional[str]) -> None:
        """Make the "TrIgGeReD" meme."""
        image = await make_image(ctx, image, return_url=True)
        file = await self.dagpi_image(f"triggered?url={image}", "triggered.gif")
        await ctx.send(file=file)

    @commands.hybrid_command(name="ascii")
    @app_commands.describe(image="image to convert to ascii")
    async def ascii_command(self, ctx: utils.Context, image: Optional[str]) -> None:
        """Get the ASCII version of an image."""
        image = await make_image(ctx, image, return_url=True)
        file = await self.dagpi_image(f"ascii?url={image}", "ascii.png")
        await ctx.send(file=file)

    @commands.hybrid_command()
    @app_commands.describe(
        color="color of player.",
        name="name of player.",
    )
    async def eject(
        self, ctx: utils.Context, color: str.lower, name: Optional[str]
    ) -> None:
        """Among Us "ejected" meme maker."""
        # This check is still bad since the API colors are limited
        # and ImageColor.getrgb supports more colors.
        if not utils.color_exists(color):
            raise commands.BadArgument(
                f"Color {color} does not exist. "
                f"Choose one from `{ctx.prefix}help {ctx.command}`"
            )

        url = f"https://vacefron.nl/api/ejected?name={name}&impostor=true&crewmate={color}"

        r = await self.bot.session.get(url)
        io = BytesIO(await r.read())

        await ctx.send(file=discord.File(fp=io, filename="ejected.png"))

    @commands.hybrid_command(name="pp")
    @app_commands.describe(member="@ of member whose pp size you wanna check.")
    async def command_pp(
        self, ctx: utils.Context, member: Optional[discord.Member]
    ) -> None:
        """Get the random size of your PP."""
        member = member or ctx.author
        sz = 100 if member.id in self.bot.owner_ids else random.randint(1, 10)
        await ctx.send(f"{member.mention}'s pp size is:\n3{'=' * sz}D")
