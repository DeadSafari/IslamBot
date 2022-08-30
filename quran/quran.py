import random
import re

import discord
import pymysql
from discord.ext.commands import CheckFailure, MissingRequiredArgument
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from quran.quran_info import *
from utils.database_utils import DBHandler
from utils.utils import convert_to_arabic_number, get_site_json

INVALID_TRANSLATION = "**Invalid translation**. List of translations: <https://github.com/galacticwarrior9/IslamBot/wiki/Qur%27an-Translation-List>"

INVALID_ARGUMENTS_ARABIC = "**Invalid arguments!** Type `{0}aquran [surah]:[ayah]`. \n\nExample: `{0}aquran 1:1`" \
                           "\n\nTo send multiple verses, type `{0}quran [surah]:[first ayah]-[last ayah]`" \
                           "\n\nExample: `{0}aquran 1:1-7`"

INVALID_ARGUMENTS_ENGLISH = "**Invalid arguments!** Type `{0}quran [surah]:[ayah]`. \n\nExample: `{0}quran 1:1`" \
                            "\n\nTo send multiple verses, type `{0}quran [surah]:[first ayah]-[last ayah]`" \
                            "\n\nExample: `{0}quran 1:1-7`"

INVALID_SURAH = "**There are only 114 surahs.** Please choose a surah between 1 and 114."
INVALID_AYAH = "**There are only {0} verses in this surah**."
INVALID_SURAH_NAME = "**Invalid Surah name!** Try the number instead."

DATABASE_UNREACHABLE = "Could not contact database. Please report this on the support server!"

TOO_LONG = "This passage was too long to send."

ICON = 'https://cdn6.aptoide.com/imgs/6/a/6/6a6336c9503e6bd4bdf98fda89381195_icon.png'

CLEAN_HTML_REGEX = re.compile('<[^<]+?>\d*')

translation_list = {
    'khattab': 131,  # English
    'bridges': 149,  # English
    'sahih': 20,  # English
    'maarifulquran': 167,  # English
    'jalandhari': 234,  # Urdu
    'suhel': 82,  # Hindi
    'awqaf': 78,  # Russian
    'musayev': 75,  # Azeri
    'uyghur': 76,  # Uyghur
    'haleem': 85,  # English
    'abuadel': 79,  # Russian
    'karakunnu': 80,  # Malayalam
    'isagarcia': 83,  # Spanish
    'divehi': 86,  # Maldivian
    'burhan': 81,  # Kurdish
    'taqiusmani': 84,  # English
    'ghali': 17,  # English
    'hilali': 203,  # English
    'maududi.en': 95,  # English
    'transliteration': 57,
    'pickthall': 19,  # English
    'yusufali': 22,  # English
    'ruwwad': 206,  # English
    'muhammadhijab': 207,  # English
    'junagarri': 54,  # Urdu
    'sayyidqutb': 156,  # Urdu
    'mahmudhasan': 151,  # Urdu
    'israrahmad': 158,  # Urdu
    'maududi': 97,  # Urdu
    'montada': 136,  # French
    'khawaja': 139,  # Tajik
    'ryoichi': 35,  # Japanese
    'fahad.in': 134,  # Indonesian
    'piccardo': 153,  # Italian
    'taisirulquran': 161,  # Bengali
    'mujibur': 163,  # Bengali
    'rawai': 162,  # Bengali
    'tagalog': 211,  # Tagalog
    'ukrainian': 217,  # Ukrainian
    'omar': 229,  # Tamil
    'serbian': 215,  # Serbian
    'bamoki': 143,  # Kurdish
    'sabiq': 141,  # Indonesian
    'telegu': 227,  # Telugu
    'marathi': 226,  # Marathi
    'hebrew': 233,  # Hebrew
    'gujarati': 225,  # Gujarati
    'abdulislam': 235,  # Dutch
    'ganda': 232,  # Ganda
    'khamis': 231,  # Swahili
    'thai': 230,  # Thai
    'kazakh': 222,  # Kazakh
    'vietnamese': 220,  # Vietnamese
    'siregar': 144,  # Dutch
    'hasanefendi': 88,  # Albanian
    'amharic': 87,  # Amharic
    'jantrust': 50,  # Tamil
    'barwani': 49,  # Somali
    'swedish': 48,  # Swedish
    'khmer': 128,  # Khmer (Cambodian)
    'kuliev': 45,  # Russian
    'diyanet': 77,  # Turkish
    'turkish': 77,  # Turkish
    'basmeih': 39,  # Malay
    'malay': 39,  # Malay
    'korean': 219,  # Korean (Hamed Choi)
    'finnish': 30,  # Finnish
    'czech': 26,  # Czech
    'nasr': 103,  # Portuguese
    'ayati': 74,  # Tajik
    'mansour': 101,  # Uzbek
    'tatar': 53,  # Tatar
    'romanian': 44,  # Romanian
    'polish': 42,  # Polish
    'norwegian': 41,  # Norwegian
    'amazigh': 236,  # Amazigh
    'sindhi': 238,  # Sindhi
    'chechen': 106,  # Chechen
    'bulgarian': 237,  # Bulgarian
    'yoruba': 125,  # Yoruba
    'shahin': 124,  # Turkish
    'abduh': 46,  # Somali
    'britch': 112,  # Turkish
    'maranao': 38,  # Maranao
    'ahmeti': 89,  # Albanian
    'majian': 56,  # Chinese
    'hausa': 32,  # Hausa
    'nepali': 108,  # Nepali
    'hameed': 37,  # Malayalam
    'elhayek': 43,  # Portuguese
    'cortes': 28,  # Spanish
    'oromo': 111,  # Oromo
    'french': 31,  # French
    'hamidullah': 31,  # French
    'persian': 29,  # Persian
    'farsi': 29,  # Persian
    'aburida': 208,  # German
    'othman': 209,  # Italian
    'georgian': 212,  # Georgian
    'baqavi': 133,  # Tamil
    'mehanovic': 25,  # Bosnian
    'yazir': 52,  # Turkish
    'zakaria': 213,  # Bengali
    'noor': 199,  # Spanish
    'sato': 218,  # Japanese
    'sinhalese': 228,  # Sinhala/Sinhalese
    'korkut': 126,  # Bosnian
    'umari': 122,  # Hindi
    'assamese': 120,  # Assamese
    'sodik': 127,  # Uzbek
    'pashto': 118,  # Pashto
    'makin': 109,  # Chinese
    'bubenheim': 27,  # German
    'indonesian': 33,  # Indonesian
}


class InvalidReference(commands.CommandError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InvalidTranslation(commands.CommandError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Translation:
    def __init__(self, key):
        self.id = self.get_translation_id(key)

    @staticmethod
    def get_translation_id(key):
        if key in translation_list:
            return translation_list[key]

        translation = process.extract(key, translation_list.keys(), scorer=fuzz.partial_ratio, limit=1)
        if translation is None:
            raise InvalidTranslation

        return translation_list[translation[0][0]]

    @staticmethod
    async def get_guild_translation(guild_id):
        translation_key = await DBHandler.get_guild_translation(guild_id)
        # Ensure we are not somehow retrieving an invalid translation
        try:
            Translation.get_translation_id(translation_key)
            return translation_key
        except InvalidTranslation:
            await DBHandler.delete_guild_translation(guild_id)
            return 'haleem'


class QuranRequest:
    def __init__(self, ctx, ref: str, is_arabic: bool, translation_key: str = None, reveal_order: bool = False):
        self.ctx = ctx
        self.ref = QuranReference(ref=ref, allow_multiple_verses=True, reveal_order=reveal_order)
        self.is_arabic = is_arabic
        if translation_key is not None:
            self.translation = Translation(translation_key)

        self.regular_url = 'https://api.quran.com/api/v4/quran/translations/{}?verse_key={}:{}'
        self.arabic_url = 'https://api.quran.com/api/v4/quran/verses/uthmani?verse_key={}'
        self.verse_ayah_dict = {}

    async def get_verses(self):
        for ayah in self.ref.ayat_list:
            json = await get_site_json(self.regular_url.format(self.translation.id, self.ref.surah, ayah))
            text = json['translations'][0]['text']

            # Clear HTML tags
            text = re.sub(CLEAN_HTML_REGEX, ' ', text)

            # Truncate verses longer than 1024 characters
            if len(text) > 1024:
                text = text[0:1018] + " [...]"

            self.verse_ayah_dict[f'{self.ref.surah}:{ayah}'] = text

            # TODO: Don't fetch the translation name every time we fetch a verse.
            self.translation_name = json['meta']['translation_name']

    async def get_arabic_verses(self):
        for ayah in self.ref.ayat_list:
            json = await get_site_json(self.arabic_url.format(f'{self.ref.surah}:{ayah}'))
            text = json['verses'][0]['text_uthmani']

            # Truncate verses longer than 1024 characters
            if len(text) > 1024:
                text = text[0:1018] + " [...]"

            self.verse_ayah_dict[
                f'{convert_to_arabic_number(str(self.ref.surah))}:{convert_to_arabic_number(str(ayah))}'] = text

    def construct_embed(self):
        surah = Surah(self.ref.surah)
        if self.is_arabic:
            em = discord.Embed(colour=0x048c28)
            em.set_author(name=f" سورة {surah.arabic_name}", icon_url=ICON)
        else:
            em = discord.Embed(colour=0x048c28)
            em.set_author(name=f"Surah {surah.name} ({surah.translated_name})", icon_url=ICON)
            em.set_footer(text=f"Translation: {self.translation_name} | {surah.revelation_location}")

        if len(self.verse_ayah_dict) > 1:
            for key, text in self.verse_ayah_dict.items():
                em.add_field(name=key, value=text, inline=False)

            return em

        em.title = list(self.verse_ayah_dict)[0]
        em.description = list(self.verse_ayah_dict.values())[0]

        return em

    async def process_request(self):
        if self.is_arabic:
            await self.get_arabic_verses()
        else:
            await self.get_verses()

        em = self.construct_embed()
        if len(em) > 6000:
            await self.ctx.send(TOO_LONG)
        else:
            await self.ctx.send(embed=em)


class Quran(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="quran")
    async def quran(self, ctx, ref: str, translation_key: str = None):
        await ctx.channel.trigger_typing()
        if translation_key is None:
            translation_key = await Translation.get_guild_translation(ctx.guild.id)
        await QuranRequest(ctx=ctx, is_arabic=False, ref=ref, translation_key=translation_key).process_request()

    @commands.command(name="aquran")
    async def aquran(self, ctx, ref: str):
        await ctx.channel.trigger_typing()
        await QuranRequest(ctx=ctx, is_arabic=True, ref=ref).process_request()

    @commands.command(name="rquran")
    async def rquran(self, ctx, translation_key: str = None):
        await ctx.channel.trigger_typing()
        surah = random.randint(1, 114)
        verse = random.randint(1, quranInfo['surah'][surah][1])

        if translation_key is None:
            translation_key = await Translation.get_guild_translation(ctx.guild.id)

        await QuranRequest(ctx=ctx, is_arabic=False, ref=f'{surah}:{verse}',
                           translation_key=translation_key).process_request()

    @commands.command(name="raquran")
    async def raquran(self, ctx):
        await ctx.channel.trigger_typing()
        surah = random.randint(1, 114)
        verse = random.randint(1, quranInfo['surah'][surah][1])

        await QuranRequest(ctx=ctx, is_arabic=True, ref=f'{surah}:{verse}').process_request()

    @cog_ext.cog_slash(name="quran", description="Send verses from the Qurʼān.",
                       options=[
                           create_option(
                               name="surah",
                               description="The surah name/number to fetch, e.g. Al-Ikhlaas, 112",
                               option_type=3,
                               required=True),
                           create_option(
                               name="start_verse",
                               description="The start verse to fetch, e.g. 255",
                               option_type=4,
                               required=True),
                           create_option(
                               name="end_verse",
                               description="If you want to send multiple verses - the end verse to fetch, e.g. 260",
                               option_type=4,
                               required=False),
                           create_option(
                               name="translation",
                               description="The translation to use.",
                               option_type=3,
                               required=False),
                           create_option(
                               name="reveal_order",
                               description="Is the surah referenced the revelation order number? (If it's a number)",
                               option_type=5,
                               required=False)])
    async def slash_quran(self, ctx: SlashContext, surah: str, start_verse: int, end_verse: int = None,
                          translation: str = None, reveal_order: bool = False):
        await ctx.defer()
        ref = start_verse if end_verse is None else f'{start_verse}-{end_verse}'
        if translation is None:
            translation = await Translation.get_guild_translation(ctx.guild.id)

        surah_number = QuranReference.parse_surah_number(surah)
        await QuranRequest(ctx=ctx, is_arabic=False, ref=f'{surah_number}:{ref}', translation_key=translation,
                           reveal_order=reveal_order).process_request()

    @cog_ext.cog_slash(name="aquran",
                       description="تبعث آيات قرآنية في الشات",
                       options=[
                           create_option(
                               name="surah",
                               description="اكتب رقم أو اسم السورة",
                               option_type=3,
                               required=True),
                           create_option(
                               name="start_verse",
                               description="اكتب رقم أول آية",
                               option_type=4,
                               required=True),
                           create_option(
                               name="end_verse",
                               description="اذا اردت ان تبعث اكثر من اية اكتب رقم اخر آية",
                               option_type=4,
                               required=False),
                           create_option(
                               name="reveal_order",
                               description="هل السورة تشير إلى رقم أمر الوحي؟",
                               option_type=5,
                               required=False)])
    async def slash_aquran(self, ctx: SlashContext, surah: str, start_verse: int, end_verse: int = None,
                           reveal_order: bool = False):
        await ctx.defer()
        ref = start_verse if end_verse is None else f'{start_verse}-{end_verse}'
        surah_number = QuranReference.parse_surah_number(surah)
        await QuranRequest(ctx=ctx, is_arabic=True, ref=f'{surah_number}:{ref}',
                           reveal_order=reveal_order).process_request()

    @cog_ext.cog_slash(name="rquran", description="Send a random translated verse from the Qurʼān.",
                       options=[
                           create_option(
                               name="translation",
                               description="The translation to use.",
                               option_type=3,
                               required=False)])
    async def slash_rquran(self, ctx: SlashContext, translation: str = None):
        await ctx.defer()
        surah = random.randint(1, 114)
        verse = random.randint(1, quranInfo['surah'][surah][1])

        if translation is None:
            translation = await Translation.get_guild_translation(ctx.guild.id)

        await QuranRequest(ctx=ctx, is_arabic=False, ref=f'{surah}:{verse}',
                           translation_key=translation).process_request()

    @cog_ext.cog_slash(name="raquran", description="Send a random verse from the Qurʼān in Arabic.")
    async def slash_raquran(self, ctx: SlashContext):
        await ctx.defer()
        surah = random.randint(1, 114)
        verse = random.randint(1, quranInfo['surah'][surah][1])

        await QuranRequest(ctx=ctx, is_arabic=True, ref=f'{surah}:{verse}').process_request()

    @quran.error
    @rquran.error
    @slash_quran.error
    @slash_rquran.error
    async def quran_command_error(self, ctx, error):
        if isinstance(error, InvalidSurah):
            await ctx.send(INVALID_SURAH)
        if isinstance(error, InvalidAyah):
            await ctx.send(INVALID_AYAH.format(error.num_verses))
        if isinstance(error, (InvalidTranslation, MissingRequiredArgument)):
            await ctx.send(INVALID_TRANSLATION)
        if isinstance(error, InvalidReference):
            try:
                await ctx.send(INVALID_ARGUMENTS_ENGLISH.format(ctx.prefix))
            except AttributeError:
                await ctx.send(INVALID_ARGUMENTS_ENGLISH.format('/'))
        if isinstance(error, BadArgument):
            await ctx.send(INVALID_ARGUMENTS_ENGLISH.format(ctx.prefix))
        if isinstance(error, InvalidSurahName):
            await ctx.send(INVALID_SURAH_NAME)

    @aquran.error
    @raquran.error
    @slash_aquran.error
    @slash_raquran.error
    async def aquran_command_error(self, ctx, error):
        if isinstance(error, InvalidSurah):
            await ctx.send(INVALID_SURAH)
        if isinstance(error, InvalidAyah):
            await ctx.send(INVALID_AYAH.format(error.num_verses))
        if isinstance(error, (InvalidTranslation, MissingRequiredArgument)):
            await ctx.send(INVALID_TRANSLATION)
        if isinstance(error, InvalidReference):
            try:
                await ctx.send(INVALID_ARGUMENTS_ARABIC.format(ctx.prefix))
            except AttributeError:
                await ctx.send(INVALID_ARGUMENTS_ARABIC.format('/'))
                # SlashContext doesn't have the attribute `prefix`
        if isinstance(error, BadArgument):
            await ctx.send(INVALID_ARGUMENTS_ARABIC.format(ctx.prefix))
        if isinstance(error, InvalidSurahName):
            await ctx.send(INVALID_SURAH_NAME)

    async def _settranslation(self, ctx, translation):
        translation_id = Translation.get_translation_id(translation)
        translation = list(translation_list.keys())[list(translation_list.values()).index(translation_id)]
        # this is so when giving success message, it says it sets it to the actual translation instead of user's typos
        # e.g user gives `khatab` but it will set it to `khattab` and tell the user the bot set it to `khattab`
        await DBHandler.update_guild_translation(ctx.guild.id, translation)
        await ctx.send(f"**Successfully updated default translation to `{translation}`!**")

    @commands.command(name="settranslation")
    @commands.has_permissions(administrator=True)
    async def settranslation(self, ctx, translation: str):
        await self._settranslation(ctx, translation)

    @cog_ext.cog_slash(name="settranslation",
                       description="🔒 Administrator only command. Changes the default translation for /quran.",
                       options=[
                           create_option(
                               name="translation",
                               description="The translation to use. See /help quran for a list.",
                               option_type=3,
                               required=True)])
    @commands.has_permissions(administrator=True)
    async def slash_settranslation(self, ctx: SlashContext, translation: str):
        await ctx.defer()
        await self._settranslation(ctx, translation)

    @settranslation.error
    @slash_settranslation.error
    async def settranslation_error(self, ctx, error):
        if isinstance(error, CheckFailure):
            await ctx.send("🔒 You need the **Administrator** permission to use this command.")
        if isinstance(error, (MissingRequiredArgument, InvalidTranslation)):
            await ctx.send(INVALID_TRANSLATION)
        if isinstance(error, pymysql.err.OperationalError):
            print(error)
            await ctx.send(DATABASE_UNREACHABLE)

    async def _surah(self, ctx, surah: str, reveal_order: bool = False):
        surah_num = QuranReference.parse_surah_number(surah)
        surah = Surah(num=surah_num, reveal_order=reveal_order)
        em = discord.Embed(colour=0x048c28)
        em.set_author(name=f'Surah {surah.name} ({surah.translated_name}) |  سورة {surah.arabic_name}', icon_url=ICON)
        em.description = (f'\n• **Surah number**: {surah.num}'
                          f'\n• **Number of verses**: {surah.verses_count}'
                          f'\n• **Revelation location**: {surah.revelation_location}'
                          f'\n• **Revelation order**: {surah.revelation_order} ')

        await ctx.send(embed=em)

    @commands.command(name="surah")
    async def surah(self, ctx, *, surah: str):
        # the star is so a user can e.g: -surah an naml
        # instead of 2 args, its 1 arg: "an naml"
        await ctx.channel.trigger_typing()
        await self._surah(ctx, surah)

    @cog_ext.cog_slash(name="surah",
                       description="Send information on a surah",
                       options=[
                           create_option(
                               name="surah",
                               description="The name/number of the Surah",
                               option_type=3,
                               required=True),
                           create_option(
                               name="reveal_order",
                               description="Is the surah referenced the revelation order number? (If it's a number)",
                               option_type=5,
                               required=False)])
    async def slash_surah(self, ctx: SlashContext, surah: str, reveal_order: bool = False):
        await ctx.defer()
        await self._surah(ctx=ctx, surah=surah, reveal_order=reveal_order)

    @surah.error
    @slash_surah.error
    async def surah_error(self, ctx, error):
        if isinstance(error, BadArgument):
            await ctx.send("**Error**: Invalid surah number.")
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("**Error**: You typed the command wrongly. Type `-surah <surah number>`.")
        if isinstance(error, InvalidSurah):
            await ctx.send(INVALID_SURAH)


def setup(bot):
    bot.add_cog(Quran(bot))
