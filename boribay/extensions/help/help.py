from difflib import get_close_matches
from typing import List, Union

import discord
from boribay.core import Boribay, utils
from discord.ext import commands, menus

__all__ = ('HelpCommand', 'Help')


class HelpPages(menus.Menu):
    """The main help menu of the bot."""

    def __init__(self, embed: discord.Embed, **kwargs):
        super().__init__(timeout=60.0, clear_reactions_after=True, **kwargs)
        self.embed = embed

    async def send_initial_message(
        self, ctx: utils.Context, channel: discord.TextChannel
    ) -> None:
        return await channel.send(embed=self.embed)

    @menus.button('<:left:814725888653918229>')
    async def go_back(self, payload):
        """Go back to the main page."""
        await self.message.edit(embed=self.embed)

    @menus.button('<:info:814725889031667722>')
    async def on_info(self, payload):
        """Shows this information page."""
        embed = self.ctx.embed(title='Reactions Information')
        messages = [f'{emoji}: {button.action.__doc__}' for emoji, button in self.buttons.items()]
        embed.add_field(name='What are these reactions for?', value='\n'.join(messages))
        await self.message.edit(embed=embed)

    @menus.button('<:question:814725892215144458>')
    async def on_question(self, payload):
        """Shows how to use the bot."""
        embed = self.ctx.embed(title='Welcome to the FAQ page.')

        fields = [
            ('How to use commands?', 'Follow the given signature for the command.'),
            ('What is <argument>?', 'This means the argument is **required**.'),
            ('What about [argument]?', 'This means the argument is **optional**.'),
            ('[argument...]?', 'This means there can be multiple arguments.'),
            ('What the hell is [--flag FLAG]?', 'This means the optional flag\nExample: **todo show --dm**')
        ]

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        await self.message.edit(embed=embed)

    @menus.button('<:crossmark:814742130190712842>')
    async def stop(self, payload):
        """Deletes this message."""
        await self.message.delete()

    @menus.button('🤔')
    async def example(self, payload):
        """Shows some examples of usage."""
        embed = self.ctx.embed(title='Usage Examples.')

        fields = [
            ('Required argument', '{p}anime kaguya sama'),
            ('Optional argument', '**{p}ascii 😀** or just **{p}ascii**'),
            ('Multiple arguments', '{p}todo remove 12 5 7 3'),
            ('Using flags', '{p}covid --country Kazakhstan'),
        ]

        for name, value in fields:
            embed.add_field(name=name, value=value.format(p=self.ctx.prefix), inline=False)

        await self.message.edit(embed=embed)


class GroupHelp(menus.ListPageSource):
    """Sends help for group-commands."""

    def __init__(self, ctx: utils.Context, group: Union[commands.Cog, commands.Group], cmds, prefix: str):
        super().__init__(entries=cmds, per_page=3)
        self.ctx = ctx
        self.group = group
        self.prefix = prefix
        self.description = '```fix\n<> ← required argument\n[] ← optional argument```'

    async def format_page(self, menu: menus.Menu, cmds) -> discord.Embed:
        g = self.group

        if isinstance(g, commands.Cog):
            doc = g.__doc__
        else:
            doc = (g.help or 'Help not provided.').split('\n')[0]

        embed = self.ctx.embed(
            title=f'Help for category: {g}',
            description=doc + self.description
        )

        for cmd in cmds:
            cmd_help = cmd.help or 'Help not found.'
            embed.add_field(
                name=f'{self.prefix}{cmd} {cmd.signature}',
                value=cmd_help.split('\n')[0] + '..',
                # trying to mean that this help ↑ has its continuation.
                inline=False
            )

        if (maximum := self.get_max_pages()) > 1:
            embed.set_author(name=f'Page {menu.current_page + 1} of {maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'{self.prefix}help <cmd> to get detailed help for a command.')
        return embed


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'hidden': True,
            'aliases': ['h'],
            'help': 'Shows help about modules, command groups or commands.'
        })

    def get_ending_note(self):
        return f'Send {self.clean_prefix}{self.invoked_with} [Category] to get a category help.'

    async def send_bot_help(self, mapping):
        ctx = self.utils.Context
        links = ctx.config.links
        cats = []

        for cog, cmds in mapping.items():
            if cog:
                if await self.filter_commands(cmds, sort=True):
                    cats.append(str(cog))

        embed = ctx.embed(
            description=f'[Invite]({links.invite_url}) | [Support]({links.support_url}) | [Source]({links.github_url}) | [Vote]({links.topgg_url})'
        ).set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)

        embed.add_field(name='Modules:', value='\n'.join(cats))

        with open('./data/config/news.md', 'r') as f:
            news = f.readlines()

        embed.add_field(name=f'📰 News - {news[0]}', value=''.join(news[1:]))
        embed.set_footer(text=self.get_ending_note())

        await HelpPages(embed).start(ctx)

    async def send_cog_help(self, cog: commands.Cog):
        ctx = self.utils.Context
        entries = await self.filter_commands(cog.get_commands(), sort=True)

        await utils.Paginate(
            GroupHelp(ctx, cog, entries, self.clean_prefix),
            timeout=30.0,
            clear_reactions_after=True
        ).start(ctx)

    def get_flags(self, command: commands.Command) -> List[str]:
        """Get all available flags for the command.

        Parameters
        ----------
        command : commands.Command
            A command you are trying to get help for.

        Returns
        -------
        list
            A joinable list of strings, like `**--mode** the manager mode`.
        """
        return [f'**--{a.dest}** {a.help}'
                for a in command.callback._def_parser._actions
                if lambda x: '_OPTIONAL' not in a.dest]

    async def send_command_help(self, command: commands.Command):
        ctx = self.utils.Context
        description = command.help or 'Help not found.'

        embed = ctx.embed(
            title=self.get_command_signature(command),
            description=description.format(p=self.clean_prefix)
        ).set_footer(text=self.get_ending_note())

        if category := str(command.cog):
            embed.add_field(name='Category', value=category)

        if aliases := command.aliases:
            embed.add_field(name='Aliases', value=' | '.join(aliases))

        if hasattr(command.callback, '_def_parser'):
            embed.add_field(
                name='Flags',
                value='\n'.join(self.get_flags(command)),
                inline=False
            )

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        if len(subcommands := group.commands) == 0 or len(cmds := await self.filter_commands(subcommands, sort=True)) == 0:
            return await self.send_command_help(group)

        await utils.Paginate(
            GroupHelp(self.utils.Context, group, cmds, self.clean_prefix), timeout=30.0
        ).start(self.utils.Context)

    async def command_not_found(self, string: str):
        message = f'Could not find the command `{string}`. '
        commands_list = [str(cmd) for cmd in self.utils.Context.bot.walk_commands()]

        if dym := '\n'.join(get_close_matches(string, commands_list)):
            message += f'Did you mean...\n{dym}'

        return message

    def get_command_signature(self, command: commands.Command):
        return f'{self.clean_prefix}{command} {command.signature}'


class Help(utils.Cog):
    """
    The help command extension.
    """

    def __init__(self, bot: Boribay):
        self.icon = '🆘'
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command
