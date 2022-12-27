from .images import Images


async def setup(bot):
    await bot.add_cog(Images())
