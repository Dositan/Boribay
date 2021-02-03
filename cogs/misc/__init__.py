from time import perf_counter
from utils.Cog import Cog
from discord.ext import commands


class Miscellaneous(Cog):
    '''Misc commands extension. Here owner inserts commands that aren't
    related to other categories, such as hello, ping etc.'''

    def __init__(self, bot):
        self.bot = bot
        self.name = '💫 Miscellaneous'

    @commands.command()
    async def vote(self, ctx):
        """Vote for the bot on Top.GG!"""
        await ctx.send('Alright link is right here, thanks for the vote! %s' % self.bot.topgg_url)

    @commands.command(aliases=['hi', 'hey'])
    async def hello(self, ctx):
        """Introduction"""
        await ctx.send(f'Hello there! I am **{self.bot.user}**, created by **{self.bot.dosek}**')

    @commands.command()
    async def prefix(self, ctx):
        """See bot's prefix."""
        if not ctx.guild:
            prefix = '.'
        else:
            prefix = self.bot.config['prefixes'][ctx.guild.id]
        await ctx.send(embed=self.bot.embed.default(
            ctx, description=f'The prefix is: `{prefix}` or {self.bot.user.mention}'
        ))

    @commands.command(aliases=['links'])
    async def invite(self, ctx):
        """Some useful invites (support server and the bot itself)"""
        embed = self.bot.embed.default(
            ctx, description=f'To invite me to your server click [here]({self.bot.invite_url})\n'
            f'Invite to the support server is [here]({self.bot.support_url})'
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Check latency of the bot and its system."""
        s = perf_counter()
        msg = await ctx.send('Pinging...')
        e = perf_counter()
        embed = self.bot.embed.default(ctx)
        fields = [
            ('<a:loading:787357834232332298> Websocket', f'```{self.bot.latency * 1000:.2f} ms```'),
            ('<a:typing:787357087843745792> Typing', f'```{(e - s) * 1000:.2f} ms```'),
            ('<:pg:795005204289421363> Database', f'```{await self.bot.db_latency()} ms```')
        ]
        for n, v in fields:
            embed.add_field(name=n, value=v)
        await msg.edit(embed=embed)

    @commands.command(aliases=['src'])
    async def source(self, ctx):
        """Sends a GitHub source link."""
        await ctx.send('AGPL-3.0 ' + self.bot.github_url)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
