import json
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import discord
from discord import VoiceClient
from discord.ext import commands
from discord.ext.commands import Context
import yt_dlp as yd


def reduce_secs(seconds: int):
    '''
    A helper function to convert seconds to a time-stamp
    :param seconds: int value of seconds
    :return:
    '''
    if seconds < 60:
        return f"00:{seconds:02}"

    else:
        minute = seconds // 60
        seconds = seconds - minute * 60

        return f"{minute:02}:{seconds:02}"

# Initialization of some things
description = '''A simple music bot created for fun. Part of the MaMa network.'''
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Setting our prefix for bot commands
bot = commands.Bot(command_prefix='\\', description=description, intents=intents)

# Dictionary Containing GuildInf Instances for each guild
Guild_Q: dict[int, 'GuildInf'] = {}

# ytDL Paramaters setup here
ytDL_params = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}


@dataclass
class SongInfo:
    """
    A class containing info on a song / argument passed to play:
    :var srch_trm - Search term to be passed to yt-dL
    :var srch_type - Tracks if search is a url search or a ytsearch
    :var title - Song title
    :var uploader - Uploder's Channel
    :var url - url to video
    :var duration - Length of song in seconds
    :var plying_url - URL used to launch a PCM audio stream
    :var seek_to - Time in seconds to seek to
    """
    seek_to: int = 0
    start_time: datetime = None
    srch_trm: str = field(default_factory=str)
    srch_type: str = field(default_factory=str)
    title: str = field(default_factory=str)
    uploader: str = field(default_factory=str)
    url: str = field(default_factory=str)
    duration: float = field(default_factory=float)
    plying_url: str = field(default_factory=str)

    def __str__(self):
        return f"Title: {self.title}\tUploaded by: {self.uploader}"


@dataclass
class GuildInf:
    """
    A class used to contain instance data from each guild the bot is a member of.
    :var voice - A VoiceClient object from discord.py. Used to establish connections to voice channels
    :var CurrentSong - Contains a SongInfo instance.
    :var looping - boolean value on whether to loop the queue
    :var que - List of SongInfo instances.
    """

    voice: VoiceClient = None
    CurrentSong: SongInfo = None
    looping: bool = field(default_factory=bool)
    que: list[SongInfo] = field(default_factory=list)
    name: str = field(default_factory=str)


@bot.event
async def on_ready():
    """
    Prints that the bot is ready and intializes the Guild_Q dictionary. A dictionary of GuildInf()
    :return: None
    """
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

    for guild in bot.guilds:
        Guild_Q[guild.id] = GuildInf()
        Guild_Q[guild.id].name = guild.name
    print('------')
    print(Guild_Q)


@bot.command()
async def p(ctx: Context, *term: str):
    """
    Takes a str term and plays a video from yt-dlp. Also responsible for connecting bot to a voice channel.
    :param ctx: discord.py object
    :param term: Search String
    :return: None
    """

    # A check for whether the command is sent by a user connected to a voice channel in the guild.
    if None is ctx.author.voice:

        return

    # Setting parameters for voice channels, server etc.
    channel = ctx.author.voice.channel
    guild = ctx.author.guild
    guild_id = ctx.author.guild.id

    guild_data = Guild_Q[guild_id]

    def initialize_info(term):
        '''
        Responsible for only extracting info about the youtube video requested.
        :param term: The search term passed to the '\p' command
        :return: None
        '''
        SngInf: SongInfo = SongInfo()
        temp_song = None

        # Upon an empty search i.e "\p" a random song from the below choice is picked.
        if len(term) == 0:
            SongList = ["https://youtu.be/QtaiyGHbhMc",  # Alucard
                        "https://youtu.be/sCQfTNOC5aE",  # In a sentimental mood
                        "https://youtu.be/oxzeDpBvxv4",  # Nardis
                        "https://youtu.be/WF-bLBMqIHY",  # COGS
                        "https://youtu.be/BnTW6fZz-1E",  # Cheeki Breeki
                        "https://youtu.be/mbgwJbpsRxg",  # Father O'Blivioni
                        "https://youtu.be/6XCByyFKklA",  # St. Alfonso
                        "https://youtu.be/C86rkb2QglQ",  # Move Me
                        "https://youtu.be/q-V8htEtAYI",  # Kill or be Killed
                        "https://youtu.be/FhRZS9B5pCk",  # GO GO! Sega Rally
                        "https://youtu.be/Aq7ddhSGOSE",  # Soft and Wet Prince
                        "https://youtu.be/bEeaS6fuUoA",  # Lovely Day
                        "https://youtu.be/lBYcOGkWEJY",  # Father Stretch My Hands
                        "https://youtu.be/q9BhRVzshgw",  # Harlequin
                        "https://youtu.be/1ih-Lsaf5oM",  # Speak Like a Child
                        "https://youtu.be/kFDPPl9yZvQ"
                        ]


            SngInf.srch_type = 'url'
            SngInf.srch_trm = random.choice(SongList)

            temp_song = yd.YoutubeDL(ytDL_params).extract_info(SngInf.srch_trm, download=False)
            # pass

        # Checks for whether a youtube search or youtube link
        elif len(term) == 1:
            if 'youtu.be ' in term[0]:
                SngInf.srch_type = 'url'
                SngInf.srch_trm = ''.join(term)
                temp_song = yd.YoutubeDL(ytDL_params).extract_info(SngInf.srch_trm, download=False)

            else:
                SngInf.srch_type = 'srch'
                SngInf.srch_trm = 'ytsearch:' + ''.join(term)
                temp_song = yd.YoutubeDL(ytDL_params).extract_info(SngInf.srch_trm, download=False)["entries"][0]

        else:
            SngInf.srch_trm = 'ytsearch:' + ' '.join(term)
            SngInf.srch_type = 'srch'
            temp_song = yd.YoutubeDL(ytDL_params).extract_info(SngInf.srch_trm, download=False)["entries"][0]

        SngInf.title = temp_song["title"]
        SngInf.url = temp_song["original_url"]
        SngInf.uploader = temp_song["uploader"]
        SngInf.duration = temp_song["duration"]

        return SngInf

    def play_song(perhaps=None):
        """
        Responsible for song playback and que management.
        :param perhaps:
        :return: None
        """
        if len(guild_data.que) <= 0:
            if guild_data.voice.is_playing():  # Checks to see if the bot is already playing a song
                pass

            guild_data.que = []
            bot.loop.create_task(guild_data.voice.disconnect())
            guild_data.voice = None
            guild_data.CurrentSong = None

        else:
            # The first song in the Que is removed and set as the currently playing song.
            guild_data.CurrentSong = guild_data.que.pop(0)

            song = yd.YoutubeDL(ytDL_params).extract_info(guild_data.CurrentSong.url, download=False)
            play_url = [i for i in song['formats'] if i['format_id'] == song['format_id']][0]['url']
            audio_src = discord.FFmpegPCMAudio(play_url, **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'})
            guild_data.voice.play(audio_src, after=play_song)
            guild_data.CurrentSong.start_time = datetime.now()


    if channel.guild is guild:
        # This connects the client to a particular guild. Also checks if already connected.
        if guild_data.voice is None:
            voice_data: VoiceClient = await channel.connect()
            guild_data.voice = voice_data

        # Song is added to queue here.
        guild_data.que.append(initialize_info(term))
        if not guild_data.voice.is_playing():
            play_song()


@bot.command()
async def q(ctx: Context):
    '''
    Displays a queue based on the guild id from context of command call
    :param ctx: Context of command call.
    :return:
    '''
    guild_id = ctx.author.guild.id
    guild_data = Guild_Q[guild_id]
    if guild_data.CurrentSong is None:
        await ctx.send('```' + "Nothing in Queue. Join a VC and use \\p to start listening" + '```')
        return

    time_elapsed = datetime.now() - guild_data.CurrentSong.start_time

    sep = "------------------------"
    np = " Now Playing "

    outstr = sep+np+sep + "\n" + "0) " + guild_data.CurrentSong.__str__() + f"Time elapsed: = {reduce_secs(round(time_elapsed.total_seconds()))}/{reduce_secs(round(guild_data.CurrentSong.duration))}" + '\n' + sep+np+sep + "\n"
    outstr = outstr + "\n" + sep + " Playing in Two More Weeks " + sep + "\n"
    for i, song in enumerate(guild_data.que):
        outstr = outstr + f"{i + 1}) " + song.__str__() + '\n'

    outstr = '```' + outstr + '```'

    await ctx.send(outstr)


@bot.command()
async def s(ctx: Context, skip: int = None):
    """
    Responsible for handling song skipping.
    :param ctx: Message context
    :param skip: How many songs to skip
    :return: None
    """
    if None is ctx.author.voice:
        return

    guild_id = ctx.author.guild.id
    guild_data = Guild_Q[guild_id]
    # if ctx.guild is
    if len(guild_data.que) == 0:
        await guild_data.voice.disconnect()
        guild_data.voice = None

    elif skip is None:
        guild_data.voice.stop()
        pass

    elif skip > len(guild_data.que):
        await ctx.send("Skipping more songs than those in queue!")

    else:
        for i in range(skip - 1):
            guild_data.que.pop(0)
            if len(guild_data.que) == 0:
                await guild_data.voice.disconnect()
                guild_data.voice = None

        guild_data.voice.stop()


@bot.command()
async def url(ctx: Context):
    """
    Displays url for currently playing track
    :param ctx: Message context
    :return: Message out to Discord Channel
    """
    guild_id = ctx.author.guild.id
    guild_data = Guild_Q[guild_id]

    outstr: str = guild_data.CurrentSong.url
    await ctx.send(outstr)


@bot.command()
async def r(ctx: Context, term: str):
    """
    Responsible for removing specific songs from the Guild Que
    :param ctx: Message context
    :param term: A str of numbers seperated by spaces
    :return: Message with removed song information
    """
    guild_id = ctx.author.guild.id
    guild_data:GuildInf = Guild_Q[guild_id]
    if len(term) == 0:
        pass

    else:
        if int(term)-1 <= len(guild_data.que):
            removed_song = guild_data.que.pop(int(term)-1)
            outstr = f"```Removed {removed_song.__str__()} from the queue```"
            await ctx.send(outstr)

with open('init.json', 'r') as f:
    data_dict = json.load(f)

bot.run(data_dict['token'])
