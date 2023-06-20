from dataclasses import dataclass, field
from typing import Optional
import discord
from discord import VoiceClient
from discord.ext import commands
import random
import yt_dlp as yd
from discord.ext.commands import Context
import json


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


# def play_song(GuildInf: GuildInf):
#     if len(GuildInf.que) == 0:
#         return
#     GuildInf.CurrentSong = GuildInf.que.pop()
#     song = yd.YoutubeDL({'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}).extract_info(GuildInf.CurrentSong, download=False)
#     url = [i for i in song['formats'] if i['format_id'] == song['format_id']][0]['url']
#     GuildInf.voice.play(discord.FFmpegPCMAudio(url, **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}), after=help_play())


@dataclass
class GuildInf:
    '''
    A class used to contain instance data from each guild the bot is a member of.
    :var voice - A VoiceClient object from discord.py. Used to establish connections to voice channels
    :var CurrentSong - Contains a songinfo instance. (Currently Song info is a yt-url)
    :var que - List of songinfo instances.
    '''
    voice: VoiceClient = None
    CurrentSong: str = field(default_factory=str)
    que: list[str] = field(default_factory=list)


@bot.event
async def on_ready():
    '''
    Prints that the bot is ready and intializes the Guild_Q dictionary
    :return: None
    '''
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    for guild in bot.guilds:
        Guild_Q[guild.id] = GuildInf()
    print('------')
    print(Guild_Q)


@bot.command()
async def p(ctx: Context, term: str):
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


    def play_song(perhaps = None):
        if len(guild_data.que) == 0:
            return
        guild_data.CurrentSong = guild_data.que.pop()
        song = yd.YoutubeDL({'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}).extract_info(guild_data.CurrentSong, download=False)
        if "ytsearch" in guild_data.CurrentSong:
            song = song['entries'][0]
        url = [i for i in song['formats'] if i['format_id'] == song['format_id']][0]['url']
        guild_data.voice.play(discord.FFmpegPCMAudio(url, **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}), after = play_song)

    if channel.guild is guild:
        # This connects the client to a particular guild. Also checks if already connected.
        if guild_data.voice is None:
            voice_data: VoiceClient = await channel.connect()
            guild_data.voice = voice_data


        guild_data.que.append(term)
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
    await ctx.send(f"The url's are {guild_data.que}")


@bot.command()
async def s(ctx: Context):
    guild_id = ctx.author.guild.id
    guild_data = Guild_Q[guild_id]
    if len(guild_data.que) == 0:
        await guild_data.voice.disconnect()
        guild_data.voice = None

    guild_data.voice.stop()

with open('init.json', 'r') as f:
    data_dict = json.load(f)

bot.run(data_dict['token'])