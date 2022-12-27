import random
from io import BytesIO
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from boribay.core import utils
from boribay.core.utils.manipulation import Manip, make_image


class Images(utils.Cog):
    """The image commands extension.

    A module that is created to work with images.

    Has features like: filters, text-images and legendary memes.
    """

    icon = "🖼"

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command()
    @app_commands.describe(member="@member whose avatar you want to have")
    async def avatar(
        self,
        ctx: commands.Context,
        member: Optional[discord.Member]
    ) -> None:
        """Sends either author or member avatar if specified."""
        member = member or ctx.author
        await ctx.send(str(member.avatar))

    @commands.hybrid_command(name="pixelate")
    @app_commands.describe(image="@member that you want to put")
    async def pixelate(self, ctx: commands.Context, image: Optional[str]) -> None:
        """Pixelate an image."""
        image = await make_image(ctx, image)
        buffer = await Manip.pixelate(BytesIO(image))

        file = discord.File(buffer, "pixelated.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name="achievement")
    @app_commands.describe(
        title="achievement title",
        caption="smaller text under title",
    )
    async def achievement(self, ctx: commands.Context, title: str, caption: str):
        """Minecraft achievement meme."""
        if len(title) > 90 or len(caption) > 90:
            return await ctx.send("Sorry, the title/caption was too long to render.")

        buffer = await Manip.achievement(title, caption)
        file = discord.File(buffer, "achievement.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name="wanted")
    @app_commands.describe(image="@member that you want to put")
    async def wanted(self, ctx: commands.Context, image: Optional[str]) -> None:
        """Make someone wanted."""
        image = await make_image(ctx, image)
        buffer = await Manip.wanted(BytesIO(image))

        file = discord.File(buffer, "wanted.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name='jail')
    @app_commands.describe(image="@member that you want to put")
    async def jail(self, ctx: commands.Context, image: Optional[str]) -> None:
        """Put someone into jail."""
        image = await make_image(ctx, image)
        buffer = await Manip.jail(BytesIO(image))

        file = discord.File(buffer, "jail.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name='f')
    @app_commands.describe(image="@member that you want to put")
    async def press_f(self, ctx, image: Optional[str]) -> None:
        """Pay respects to someone."""
        image = await make_image(ctx, image)
        buffer = await Manip.press_f(BytesIO(image))

        file = discord.File(buffer, "f.png")
        message = await ctx.send(file=file)
        await message.add_reaction("<:press_f:796264575065653248>")

    @commands.hybrid_command(name="5g1g")
    @app_commands.describe(member="@member that you want to put")
    async def fiveguysonegirl(self, ctx: commands.Context, member: Optional[str]) -> None:
        """Legendary "5 guys 1 girl" meme maker."""
        author = await ctx.author.avatar.replace(size=128).read()
        member = await make_image(ctx, member)
        buffer = await Manip.fiveguysonegirl(BytesIO(author), BytesIO(member))

        file = discord.File(buffer, "5g1g.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name='fight')
    @app_commands.describe(member="@member that you want to put")
    async def fight(self, ctx: commands.Context, member: str) -> None:
        """K.O. someone!"""
        winner = await ctx.author.avatar.replace(size=64).read()
        knocked_out = await make_image(ctx, member)
        buffer = await Manip.fight(BytesIO(winner), BytesIO(knocked_out))

        file = discord.File(buffer, "fight.png")
        await ctx.send(file=file)

    @commands.hybrid_command()
    @app_commands.describe(
        degrees="amount of degrees to swirl",
        image="any type of image to swirl",
    )
    async def swirl(self, ctx, degrees: Optional[int], image: Optional[str]) -> None:
        """Swirl an image."""
        degrees = degrees or random.randint(-360, 360)

        image = await make_image(ctx, image)
        buffer = await Manip.swirl(degrees, BytesIO(image))

        file = discord.File(buffer, "swirl.png")
        await ctx.send(file=file)

    @commands.hybrid_command()
    @app_commands.describe(image="@member that you want to communize")
    async def communist(self, ctx: commands.Context, image: Optional[str]) -> None:
        """The communist meme maker."""
        image = await make_image(ctx, image)
        buffer = await Manip.communist(BytesIO(image))

        file = discord.File(buffer, "communist.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name="rainbow")
    @app_commands.describe(image="@member that you want to put")
    async def rainbow(self, ctx, image: Optional[str]) -> None:
        """Put rainbow filter on a user."""
        image = await make_image(ctx, image)
        buffer = await Manip.rainbow(BytesIO(image))

        file = discord.File(buffer, "rainbow.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name="whyareyougay")
    @app_commands.describe(member="@member that you want to put")
    async def whyareyougay(self, ctx, member: Optional[str]) -> None:
        """The legendary "WhY aRe YoU gAy?" meme maker."""
        author = await ctx.author.avatar.replace(size=128).read()

        member = await make_image(ctx, member)
        buffer = await Manip.whyareyougae(BytesIO(author), BytesIO(member))

        file = discord.File(buffer, "wayg.png")
        await ctx.send(file=file)

    @commands.hybrid_command()
    @app_commands.describe(
        no="Text that Drake hates.",
        yes="Text that Drake likes.",
    )
    async def drake(self, ctx: commands.Context, no: str, yes: str) -> None:
        """The legendary "Drake yes/no" meme maker."""
        if len(yes) > 90 or len(no) > 90:
            return await ctx.send("The text was too long to render.")

        buffer = await Manip.drake(no, yes)
        file = discord.File(buffer, "drake.png")
        await ctx.send(file=file)

    @commands.hybrid_command(name='clyde')
    @app_commands.describe(text="text for clyde bot to say")
    async def clyde(self, ctx: commands.Context, text: str) -> None:
        """Send message as Clyde - Discord Bot."""
        if len(text) > 75:
            return await ctx.send("Sorry, the text was too long to render.")

        buffer = await Manip.clyde(text)
        file = discord.File(buffer, "clyde.png")
        await ctx.send(file=file)
