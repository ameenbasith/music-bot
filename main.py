import discord
from discord.ext import commands
import yt_dlp

# Load the Opus library (required for audio streaming in Discord)
discord.opus.load_opus('/opt/homebrew/bin/opusenc')

# Define your Discord token here
DISCORD_TOKEN = "INSERT TOKEN HERE"

# Initialize the bot with specified intents
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Define a class for audio source with volume control
class YTDLSource(discord.PCMVolumeTransformer):
    """
    Initialize a YTDLSource instance.

    :param source: The audio source to be transformed with volume control.
    :param data: Metadata about the source.
    :param volume: The initial volume level (0.0 to 2.0).
    """
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

@bot.command(name='play', help='To play a song')
async def play(ctx, url):
    """
    Play a song from a given URL in a voice channel.

    :param ctx: The context of the command.
    :param url: The URL of the song to be played.
    """
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
        }

        ydl = yt_dlp.YoutubeDL(ydl_opts)
        info_dict = ydl.extract_info(url, download=False)
        url2 = info_dict.get("url")

        if voice_channel.is_playing():
            voice_channel.stop()

        voice_channel.play(discord.FFmpegPCMAudio(url2))
        await ctx.send('**Now playing:** {}'.format(info_dict.get("title")))

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
