from .moderation import Moderation


# Setting up the cog.
async def setup(bot):
    await bot.add_cog(Moderation())
