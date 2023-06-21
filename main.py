from dataclasses import dataclass, field
from typing import Optional
import discord
from discord import VoiceClient
from discord.ext import commands
import yt_dlp as yd
from discord.ext.commands import Context
import json
import asyncio


def get_function_default_args(func):
    return {
        k: v for k, v
        in zip(
            [
                x for i, x in enumerate(func.__code__.co_varnames)
                if i >= func.__code__.co_argcount - len(func.__defaults__)
            ],
            func.__defaults__
        )
    }


description = '''A simple music bot created for fun. Part of the MaMA network.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='\\', description=description, intents=intents)

# Dictionary Containing GuildInf Instances for each guild
Guild_Q: dict[int, 'GuildInf'] = {}

@dataclass
class SongInfo:
    '''
    A class containing info on a song / argument passed to play:
    :var srch_trm - Search term to be passed to yt-dL
    :var srch_type - Tracks if search is a url or ytsearch
    :var title - Song title
    :var uploader - Uploder's Channel
    :var url - url to video
    :var duration - Length of song in seconds
    :var plying_url - URL used to launch a PCM audio stream
    :var seek_to - Time in seconds to seek to
    '''
    srch_trm: str = field(default_factory=str)
    srch_type: str = field(default_factory=str)
    title: str = field(default_factory=str)
    uploader: str = field(default_factory=str)
    url: str = field(default_factory=str)
    duration: float = field(default_factory=float)
    plying_url: str = field(default_factory=str)
    seek_to: int = 0

    def __str__(self):
        return f"Title: {self.title}\tUploaded by: {self.uploader}\n"


@dataclass
class GuildInf:
    '''
    A class used to contain instance data from each guild the bot is a member of.
    :var voice - A VoiceClient object from discord.py. Used to establish connections to voice channels
    :var CurrentSong - Contains a SongInfor instance.
    :var que - List of SongInfo instances.
    '''
    voice: VoiceClient = None
    CurrentSong: SongInfo = None
    que: list[SongInfo] = field(default_factory=list)
    name: str = field(default_factory=str)


@bot.event
async def on_ready():
    '''
    Prints that the bot is ready and intializes the Guild_Q dictionary
    :return: None
    '''
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

    for guild in bot.guilds:
        Guild_Q[guild.id] = GuildInf()
        Guild_Q[guild.id].name = guild.name
    print('------')
    print(Guild_Q)


@bot.command()
async def p(ctx: Context, *term: str):
    """
    Takes a str term and plays a video from yt-dlp
    :param ctx:
    :param term: Search String
    :return: None
    """

    channel = ctx.author.voice.channel
    guild = ctx.author.guild
    guild_id = ctx.author.guild.id

    guild_data = Guild_Q[guild_id]

    def initialize_info(term):
        SngInf: SongInfo = SongInfo()
        temp_song = None

        if len(term) == 0:
            SngInf.srch_type = 'url'
            SngInf.srch_trm = "https://youtu.be/6GEI3PpXEAo"
            temp_song = yd.YoutubeDL({'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}).extract_info(SngInf.srch_trm, download=False)
            pass

        elif len(term) == 1 :
            if 'youtu.be ' in term[0]:
                SngInf.srch_type = 'url'
                SngInf.srch_trm = ''.join(term)
                temp_song = yd.YoutubeDL({'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}).extract_info(SngInf.srch_trm, download=False)

            else:
                SngInf.srch_type = 'srch'
                SngInf.srch_trm = 'ytsearch:' + ''.join(term)
                temp_song = yd.YoutubeDL({'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}).extract_info(SngInf.srch_trm, download=False)["entries"][0]

        else:
            SngInf.srch_trm = 'ytsearch:' + ' '.join(term)
            SngInf.srch_type = 'srch'
            temp_song = yd.YoutubeDL({'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}).extract_info(SngInf.srch_trm,download=False)["entries"][0]

        SngInf.title = temp_song["title"]
        SngInf.url = temp_song["original_url"]
        SngInf.uploader = temp_song["uploader"]
        SngInf.duration = temp_song["duration"]

        return SngInf

    def play_song(perhaps = None):

        if len(guild_data.que) <= 0:
            bot.loop.create_task(guild_data.voice.disconnect())
            guild_data.voice = None

        guild_data.CurrentSong = guild_data.que.pop(0)

        song = yd.YoutubeDL({'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}).extract_info(guild_data.CurrentSong.url, download=False)
        play_url = [i for i in song['formats'] if i['format_id'] == song['format_id']][0]['url']
        guild_data.voice.play(discord.FFmpegPCMAudio(play_url, **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}), after = play_song)

    if channel.guild is guild:
        # This connects the client to a particular guild. Also checks if already connected.
        if guild_data.voice is None:
            voice_data: VoiceClient = await channel.connect()
            guild_data.voice = voice_data

        #Song is added to que here.
        guild_data.que.append(initialize_info(term))
        if not guild_data.voice.is_playing():
            play_song()


@bot.command()
async def q(ctx: Context):
    '''
    Displays a que based on the guild id from context of command call
    :param ctx: Context of command call.
    :return:
    '''
    guild_id = ctx.author.guild.id
    guild_data = Guild_Q[guild_id]
    outstr = "------------ Now Playing ------------\n" + "0) " + guild_data.CurrentSong.__str__() + "------------ Now Playing ------------\n"
    for i, song in enumerate(guild_data.que):
        outstr = outstr + f"{i+1}) " + song.__str__()

    outstr = '```' + outstr + '```'

    await ctx.send(outstr)


@bot.command()
async def s(ctx: Context, skip: int = None):
    guild_id = ctx.author.guild.id
    guild_data = Guild_Q[guild_id]
    if len(guild_data.que) == 0:
        await guild_data.voice.disconnect()
        guild_data.voice = None

    if skip is None:
        guild_data.voice.stop()
        pass

    elif skip > len(guild_data.que):
        await ctx.send("Skipping more songs than those in que!")

    else:
        for i in range(skip-1):
            guild_data.que.pop(0)
            if len(guild_data.que) == 0:
                await guild_data.voice.disconnect()
                guild_data.voice = None

        guild_data.voice.stop()


with open('init.json', 'r') as f:
    data_dict = json.load(f)

@bot.command()
async def url(ctx: Context):
    guild_id = ctx.author.guild.id
    guild_data = Guild_Q[guild_id]

    guild_data.CurrentSong:SongInfo

    outstr: str = guild_data.CurrentSong.url
    await ctx.send(outstr)

bot.run(data_dict['token'])