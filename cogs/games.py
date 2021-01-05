import os
import json
import discord
import asyncio
import random
import textwrap

from time import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from discord.ext.commands import command
from utils.CustomCog import Cog
from utils.CustomEmbed import Embed


class Games(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.name = '🕹 Games'

    @command()
    async def trivia(self, ctx):
        """Trivia game in Discord!"""
        async with self.bot.session.get('https://opentdb.com/api.php?amount=1') as r:
            data = await r.json()
        correct = data['results'][0]['correct_answer']
        letters = ['🇦', '🇧', '🇨', '🇩']
        answers = data['results'][0]['incorrect_answers'] + [correct]
        answers = random.sample(answers, len(answers))
        embed = Embed(description=data['results'][0]['question'])
        for i in range(len(answers)):
            embed.add_field(name='\u200b', value=f'{letters[i]} {answers[i]}', inline=False)
        trv = await ctx.send(embed=embed)
        try:
            msg = await self.bot.wait_for('message', check=lambda m: m.content == correct, timeout=30.0)
            if not msg:
                return
            await ctx.send('Correct!')
        except asyncio.TimeoutError:
            try:
                await trv.delete()
            except discord.errors.NotFound:
                pass

    @command(aliases=['tr'], brief='typeracer command! compete with others using this.')
    async def typeracer(self, ctx):
        """Typeracer Command. Compete with others!
        Returns: Average WPM of the winner, time spent to type and the original text."""
        cs = self.bot.session
        r = await cs.get(os.getenv('tr_url'))
        buffer = BytesIO()
        quote = json.loads(await r.read())
        to_wrap = random.choice(quote)['text']
        wrapped_text = textwrap.wrap(to_wrap, 30)
        text = '\n'.join(wrapped_text)
        font = ImageFont.truetype('./data/fonts/monoid.ttf', size=30)
        w, h = font.getsize(text)
        with Image.new('RGB', (525, h * len(wrapped_text))) as base:
            canvas = ImageDraw.Draw(base)
            canvas.multiline_text((5, 5), text, font=font)
            base.save(buffer, 'png', optimize=True)
        buffer.seek(0)
        race = await ctx.send(
            file=discord.File(buffer, 'typeracer.png'),
            embed=Embed.default(
                ctx, title='Typeracer', description='see who is fastest at typing.'
            ).set_image(url='attachment://typeracer.png')
        )
        start = time()
        try:
            msg = await self.bot.wait_for('message', check=lambda m: m.content == to_wrap, timeout=60.0)
            if not msg:
                return
            end = time()
            final = round((end - start), 2)
            wpm = len(to_wrap.split()) * (60.0 / final)
            await ctx.send(embed=Embed(
                title=f'{msg.author.display_name} won!',
                description=f'**Done in**: {final}s\n**Average WPM**: {round(wpm)} words\n**Original text:**```diff\n+ {to_wrap}```',
            ))
        except asyncio.TimeoutError:
            try:
                await race.delete()
            except discord.errors.NotFound:
                pass

    @command(name='rps', brief="the Rock | Paper | Scissors game.")
    async def rockpaperscissors(self, ctx):
        """The Rock | Paper | Scissors game.
        There are three different reactions, depending on your choice
        random will find did you win, lose or made draw."""
        rps_dict = {
            "🪨": {"🪨": "draw", "📄": "lose", "✂": "win"},
            "📄": {"🪨": "win", "📄": "draw", "✂": "lose"},
            "✂": {"🪨": "lose", "📄": "win", "✂": "draw"}
        }
        choice = random.choice([*rps_dict.keys()])
        msg = await ctx.send(embed=Embed(description="**Choose one 👇**").set_footer(text="10 seconds left⏰"))
        for r in rps_dict.keys():
            await msg.add_reaction(r)
        try:
            r, u = await self.bot.wait_for('reaction_add', timeout=10, check=lambda re, us: us == ctx.author and str(re) in rps_dict.keys() and re.message.id == msg.id)
            play = rps_dict.get(str(r.emoji))
            await msg.edit(embed=Embed(description=f'''Result: **{play[choice].upper()}**\nMy choice: **{choice}**\nYour choice: **{str(r.emoji)}**'''))
        except asyncio.TimeoutError:
            await msg.delete()

    @command(aliases=['slots', 'bet'])
    async def slot(self, ctx):
        """Play the game on a slot machine!"""
        emojis = '🍎🍊🍐🍋🍉🍇🍓🍒'
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        slotmachine = f'{a} | {b} | {c}\n{ctx.author.display_name},'

        if (a == b == c):
            await ctx.send(f'{slotmachine} All 3 match, you are a big winner! 🎉')
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f'{slotmachine} 2 match, you won! 🎉')
        else:
            await ctx.send(f'{slotmachine} No matches, you have to buy me a VPS 😳')


def setup(bot):
    bot.add_cog(Games(bot))
