import json

from discord.ext import commands, ipc
from discord.ext.ipc.server import Server
from discord.ext.ipc.objects import ClientPayload

from boribay.core import utils

class Routes(utils.Cog):

    def __init__(self, bot: commands.Bot):
        self.icon = "💾"
        self.bot = bot
        if not hasattr(bot, "ipc"):
            bot.ipc = ipc.Server(self, secret_key="🐼")
    
    async def cog_load(self) -> None:
        await self.bot.ipc.start()

    async def cog_unload(self) -> None:
        await self.bot.ipc.stop()
        self.bot.ipc = None

    @Server.route()
    async def list_commands(self, _: ClientPayload):
        return json.dumps([
            {
                cog_name: [{
                    'name': str(c),
                    'description': c.help
                } for c in commands.get_commands()]
            } for cog_name, commands in self.bot.cogs.items()
        ])

async def setup(bot):
    await bot.add_cog(Routes(bot))
