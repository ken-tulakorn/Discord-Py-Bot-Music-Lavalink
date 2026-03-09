from lib.library import *

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def load_extensions():
    folders = ['commands', 'event', 'music']
    for folder in folders:
        if os.path.exists(f'./{folder}'):
            for file in os.listdir(f'./{folder}'):
                if file.endswith('.py'):
                    await client.load_extension(f'{folder}.{file[:-3]}')

@client.command(name="play", aliases=["p", "เปิดเพลง"])
async def play(ctx: commands.Context, *, music: str) -> None:
    guild = ctx.guild
    if not guild:
        return

    member = guild.me
    if not member:
        return

    is_admin = any(role.permissions.administrator for role in member.roles)
    
    if is_admin:
        player = cast(wavelink.Player, ctx.voice_client)
        tracks: wavelink.Search = await wavelink.Playable.search(music)
       
        if not tracks:
            embed = discord.Embed(color=discord.Colour.red())
            embed.add_field(name="You need to be in the same audio room as the bot to add the music.", value="", inline=False)
            await ctx.send(embed=embed)
            return

        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True) 
            except AttributeError:
                embed = discord.Embed(color=discord.Colour.red())
                embed.add_field(name="You need to be in the same audio room as the bot to add the music.", value="", inline=False)
                await ctx.send(embed=embed)
                return
        else:
            if ctx.author.voice.channel.id != player.channel.id:
                embed = discord.Embed(color=discord.Colour.red())
                embed.add_field(name="You need to be in the same audio room as the bot to add the music.", value="", inline=False)
                await ctx.send(embed=embed)
                return

        player.autoplay = wavelink.AutoPlayMode.partial

        if not hasattr(player, "home"):
            player.home = ctx.channel

        async with aiosqlite.connect("data/music.db") as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT channel_id FROM db_music WHERE guild_id = ?", (ctx.guild.id,))
            fetch_one = await cursor.fetchone()
            
            if fetch_one:
                await cursor.execute("UPDATE db_music SET channel_id = ? WHERE guild_id = ?", (ctx.channel.id, ctx.guild.id))
            else:
                await cursor.execute("INSERT INTO db_music (channel_id, guild_id) VALUES (?, ?)", (ctx.channel.id, ctx.guild.id))
            await db.commit()

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            embed = discord.Embed(color=discord.Color.brand_green())
            embed.set_author(name=f"Added playlist '{tracks.name}' with {added} songs to the queue", icon_url=ctx.author.display_avatar.url)
            embed.add_field(name="Used by", value=f"<@{ctx.author.id}>", inline=True)
            await ctx.reply(embed=embed)
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            embed = discord.Embed(color=discord.Color.brand_green())
            embed.set_author(name=f"Added song '{track.title}' to the queue", icon_url=ctx.author.display_avatar.url)
            embed.add_field(name="Used by", value=f"<@{ctx.author.id}>", inline=True)
            embed.add_field(name="Artist", value=f"[{track.author}]({track.uri})", inline=True)
            await ctx.reply(embed=embed)

        if not hasattr(player, "playing_member_ids"):
            player.playing_member_ids = []
                
        player.playing_member_ids.append(ctx.author.id)

        if not player.playing:
            await player.play(player.queue.get(), volume=30)
    else:
        embed = discord.Embed(color=discord.Colour.red())
        embed.add_field(name=":tickets: Please grant the following permissions for the bot to function properly", value="```Administrator```", inline=False)
        await ctx.send(embed=embed)

async def main():
    TOKEN = os.getenv("DISCORD_API_TOKEN")
    if not TOKEN or TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print("Error: Please set your DISCORD_API_TOKEN in the .env file.")
        return
        
    await load_extensions()
    await client.start(TOKEN)

@client.event
async def on_ready(): 
    await client.tree.sync() 
    print("Success: Bot Online")

if __name__ == "__main__":
    asyncio.run(main())
