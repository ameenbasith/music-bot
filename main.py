import discord
from discord.ext import commands
import youtube_dl
import asyncio

intents = discord.Intents.default()
intents.typing = False

# Enable the GUILD_MEMBERS and PRESENCE_INTENT privileged intents
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='$', intents=intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in info:
            info = info['entries'][0]
        url2 = info['url']
        return cls(discord.FFmpegPCMAudio(executable="ffmpeg", source=url2), data=info)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    # Replace 'YOUR_VOICE_CHANNEL_ID' with the ID of the voice channel you want the bot to join.
    voice_channel = bot.get_channel(777770716090204177)

    if voice_channel:
        vc = await voice_channel.connect()
        print(f'Joined {voice_channel}')


@bot.command(name='play', help='Play a song from YouTube or SoundCloud')
async def play(ctx, url):
    # Check if the user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command.")
        return

    print(f'Command recognized: !play {url}')  # Add this line for debugging

    # Get the voice channel of the user
    voice_channel = ctx.author.voice.channel

    # Check if the bot is already in a voice channel
    if ctx.voice_client is None:
        # Connect to the user's voice channel
        vc = await voice_channel.connect()
    else:
        # Use the existing voice connection
        vc = ctx.voice_client

    # Create an instance of YTDLSource and play the audio
    source = await YTDLSource.from_url(url, loop=bot.loop)
    vc.play(source)

    # Send a confirmation message
    await ctx.send(f'Now playing: {source.title}')


if __name__ == "__main__":
    bot.run("")
