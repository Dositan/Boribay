import contextlib
import copy
import re
import typing

import discord
import twemoji_parser
from discord.ext import commands
from PIL import ImageColor


class SettingsConverter(commands.Converter):
    async def convert(self, guild: discord.Guild, settings: dict):
        data = copy.copy(settings[guild.id])

        for k, v in data.items():
            if k == 'autorole':
                data[k] = guild.get_role(v)

            elif k == 'embed_color':
                data[k] = hex(v)

            elif k in ('welcome_channel', 'automeme', 'logging_channel'):
                data[k] = guild.get_channel(v)

        return data


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        time = 0
        time_dict = {'h': 3600, 's': 1, 'm': 60, 'd': 86400}
        matches = re.findall(r'(?:(\d{1,5})(h|s|m|d))+?', argument.lower())

        for v, k in matches:
            try:
                time += time_dict[k] * float(v)

            except KeyError:
                raise commands.BadArgument(f'{k} is an invalid time-key! h/m/s/d are valid.')

            except ValueError:
                raise commands.BadArgument(f'{v} is not a number!')

        return time


class ColorConverter(commands.Converter):
    async def convert(self, ctx, arg: str):
        with contextlib.suppress(AttributeError):
            match = re.match(r'\(?(\d+),?\s*(\d+),?\s*(\d+)\)?', arg)
            check = all(0 <= int(x) <= 255 for x in match.groups())

        if match and check:
            return discord.Color.from_rgb([int(i) for i in match.groups()])

        converter = commands.ColorConverter()
        try:
            result = await converter.convert(ctx, arg)
        except commands.BadColourArgument:
            try:
                color = ImageColor.getrgb(arg)
                result = discord.Color.from_rgb(*color)
            except ValueError:
                result = None

        if result:
            return result

        raise commands.BadArgument(f'Could not find any color that matches this: `{arg}`.')


class ImageURLConverter(commands.Converter):
    async def convert(self, ctx, arg: typing.Union[discord.Emoji, str]):
        try:
            mconv = commands.MemberConverter()
            m = await mconv.convert(ctx, arg)
            image = str(m.avatar_url_as(static_format='png', format='png', size=512))
            return image

        except (TypeError, commands.MemberNotFound):
            try:
                url = await twemoji_parser.emoji_to_url(arg, include_check=True)

                if re.match(ctx.bot.regex['URL_REGEX'], url):
                    return url

                if re.match(ctx.bot.regex['URL_REGEX'], arg):
                    return arg

                elif re.match(ctx.bot.regex['EMOJI_REGEX'], arg):
                    econv = commands.PartialEmojiConverter()
                    e = await econv.convert(ctx, arg)
                    image = str(e.url)
                    return image

            except TypeError:
                return None

        return None


class ImageConverter(commands.Converter):
    async def convert(self, ctx, arg: typing.Union[discord.Emoji, str]):
        try:
            mconv = commands.MemberConverter()
            m = await mconv.convert(ctx, arg)
            pfp = m.avatar_url_as(static_format='png', format='png', size=512)
            image = await pfp.read()
            return image

        except (TypeError, commands.MemberNotFound):
            try:
                url = await twemoji_parser.emoji_to_url(arg, include_check=True)
                cs = ctx.bot.session

                if re.match(ctx.bot.regex['URL_REGEX'], url):
                    r = await cs.get(url)
                    image = await r.read()
                    return image

                if re.match(ctx.bot.regex['URL_REGEX'], arg):
                    r = await cs.get(arg)
                    image = await r.read()
                    return image

                elif re.match(ctx.bot.regex['EMOJI_REGEX'], arg):
                    econv = commands.PartialEmojiConverter()
                    e = await econv.convert(ctx, arg)
                    asset = e.url
                    image = await asset.read()
                    return image

            except TypeError:
                return None

        return None