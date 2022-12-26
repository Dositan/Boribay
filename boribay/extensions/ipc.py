import json
from discord.ext import commands, ipc
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload

class Routes(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not hasattr(bot, "ipc"):
            bot.ipc = ipc.Server(self, secret_key="🐼")
    
    async def cog_load(self) -> None:
        await self.bot.ipc.start()

    async def cog_unload(self) -> None:
        await self.bot.ipc.stop()
        self.bot.ipc = None

    @Server.route()
    async def general_info(self, data: ClientPayload):
        return str({
            "cogs": self.bot.cogs,
            "commands": self.bot.all_commands
        })

async def setup(bot):
    await bot.add_cog(Routes(bot))
