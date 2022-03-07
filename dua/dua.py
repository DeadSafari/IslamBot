import random
import re

import discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from utils.utils import get_site_source

ICON = 'https://sunnah.com/images/hadith_icon2_huge.png'

DUAS = {
    'Afflictions': 49,
    'After Eating': 66,
    'After Insulting': 105,
    'After Sinning': 41,
    'After Sneezing': 72,
    'Angriness': 76,
    'Anxiety': 34,
    'Before Eating': 65,
    'Breaking Fast': 64,
    'Completing Wudu': 9,
    'Delight': 115,
    'Distress': 35,
    'Doubts': 37,
    'During Adhan': 15,
    'Entering Home': 11,
    'Fear Of People': 114,
    'Fear Of Shirk': 86,
    'Forgiveness': 127,
    'In Ruku': 17,
    'Leaving Home': 10,
    'Pain': 117,
    'Returning From Travel': 99,
    'Sorrow': 34,
    'Travel': 90,
    'Visiting Graves': 56,
    'Visiting Sick': 45,
    'During Rain': 60,
    'After Rain': 61,
    'Hearing Thunder': 58,
    'Entering Mosque': 13,
    'Leaving Mosque': 14,
    'Entering Toilet': 6,
    'Leaving Toilet': 7,
}


class Dua(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = 'https://ahadith.co.uk/hisnulmuslim-dua-{}'

    @staticmethod
    def get_dua_id(subject):
        return DUAS[subject]

    async def _dua(self, ctx, subject: str):
        subject = subject.title()
        dua_id = self.get_dua_id(subject)

        site_source = await get_site_source(self.url.format(dua_id))
        dua_text = []
        for dua in site_source.findAll("div", {"class": 'search-item'}):
            text = dua.get_text(separator=" ").strip() \
                .replace("(saw)", "ﷺ")
            text = '\n' + text
            dua_text.append(text)
        dua_text = ''.join(dua_text)
        dua_text = re.sub(r'\d+', '', dua_text)

        em = discord.Embed(title=f'Duas for {subject.title()}', colour=0x467f05, description=dua_text)
        em.set_author(name="Fortress of the Muslim", icon_url=ICON)
        await ctx.send(embed=em)

    async def _dualist(self, ctx, prefix):
        dua_list_message = [f'**Type {prefix}dua <topic>**. Example: `{prefix}dua breaking fast`\n']

        for dua in DUAS:
            dua_list_message.append('\n' + dua)

        em = discord.Embed(title='Dua List', colour=0x467f05, description=''.join(dua_list_message))
        em.set_footer(text="Source: Fortress of the Muslim (Hisn al-Muslim)")

        await ctx.send(embed=em)

    @commands.command(name='dua')
    async def dua(self, ctx, *, subject: str):
        await ctx.channel.trigger_typing()
        await self._dua(ctx, subject)

    @commands.command(name="rdua")
    async def randomdua(self, ctx):
        await ctx.channel.trigger_typing()
        await self._dua(ctx, random.choice(list(DUAS.keys())))

    @commands.command(name='dualist')
    async def dualist(self, ctx):
        await ctx.channel.trigger_typing()
        await self._dualist(ctx, ctx.prefix)

    @cog_ext.cog_slash(name="dua", description="Send ʾadʿiyah by topic.",
                       options=[
                           create_option(
                               name="topic",
                               description="The topic of the dua.",
                               option_type=3,
                               required=True)])
    async def slash_dua(self, ctx: SlashContext, topic: str):
        await ctx.defer()
        await self._dua(ctx, topic)

    @cog_ext.cog_slash(name="rdua", description="Send a random dua.")
    async def slash_rdua(self, ctx: SlashContext):
        await ctx.defer()
        await self._dua(ctx, random.choice(list(DUAS.keys())))

    @cog_ext.cog_slash(name="dualist", description="Send dua list.")
    async def slash_dualist(self, ctx: SlashContext):
        await ctx.defer()
        await self._dualist(ctx, '/')

    @dua.error
    async def on_dua_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send(f"**You need to provide a dua topic**. Type `{ctx.prefix}dualist` for a list of dua topics.")
        if isinstance(error, KeyError):
            await ctx.send(
                f"**Could not find dua for this topic.** Type `{ctx.prefix}dualist` for a list of dua topics.")


def setup(bot):
    bot.add_cog(Dua(bot))
