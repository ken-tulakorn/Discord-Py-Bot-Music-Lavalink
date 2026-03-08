from lib.library import *

class MusicControllerView(discord.ui.View):
    def __init__(self, player, bot: commands.Bot) -> None:
        super().__init__(timeout=None)
        self.player = player
        self.value = 30
        self.bot = bot

    async def check_user_voice(self, interaction: discord.Interaction) -> bool:
        if interaction.user.voice is None or interaction.user.voice.channel != self.player.channel:
            embed = discord.Embed(color=discord.Colour.red())
            embed.add_field(name="You must be in the same room as the bot to use the commands.", value="", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    
    @discord.ui.button(style=discord.ButtonStyle.primary, label="", emoji="<a:music_loop:1193130011172032523>", custom_id="loop_all", row=1)
    async def btn_loop_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        try:
            if self.player:
                self.player.queue.mode = wavelink.QueueMode.loop_all
                embed = discord.Embed(color=discord.Colour.brand_green())
                embed.add_field(name="You have successfully used the loop all command.", value="", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred. Please try again later.", ephemeral=True)
            logging.error(f"Error in btn_loop_all: {e}")

    @discord.ui.button(style=discord.ButtonStyle.primary, label="", emoji="<a:music_clear:1193130005232889977>", custom_id="clear", row=1)
    async def btn_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        if self.player:
            self.player.queue.clear()
            self.player.queue.mode = wavelink.QueueMode.normal
            await self.player.stop()
            embed = discord.Embed(color=discord.Colour.brand_green())
            embed.add_field(name="You have successfully used the clear command.", value="", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="", emoji="<a:Untitleddesignunscreen11:1203253448464797707>", custom_id="skip", row=1)
    async def btn_skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        if self.player:
            if self.player.queue:
                await self.player.skip(force=True)
                embed = discord.Embed(color=discord.Colour.brand_green())
                embed.add_field(name="You have successfully used the skip command.", value="", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(color=discord.Colour.red())
                embed.add_field(name="No more songs in the queue to skip.", value="", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="", emoji="<a:downloadunscreen1:1203273373753417728>", custom_id="loop", row=1)
    async def btn_loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        if self.player:
            self.player.queue.mode = wavelink.QueueMode.loop
            embed = discord.Embed(color=discord.Colour.brand_green())
            embed.add_field(name="You have successfully used the loop command.", value="", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="", emoji="<a:download1unscreen:1203356639990652979>", custom_id="filter", row=2)
    async def btn_filter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        if self.player:
            embed = discord.Embed(color=discord.Colour.brand_green())
            embed.add_field(name="You have successfully used the filter command.", value="", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="", emoji="<a:bass1:1041620050743930910>", custom_id="base", row=2)
    async def btn_base(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        if self.player:
            embed = discord.Embed(color=discord.Colour.brand_green())
            embed.add_field(name="You have successfully used the base command.", value="", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.primary, label="", emoji="<a:music_pause:1193130015408259112>", custom_id="pause", row=2)
    async def btn_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        if self.player:
            await self.player.pause(not self.player.paused)
            embed = discord.Embed(color=discord.Colour.brand_green())
            if self.player.paused:
                embed.add_field(name="You have successfully used the pause command.", value="", inline=False)
            else:
                embed.add_field(name="You have successfully used the resume command.", value="", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(style=discord.ButtonStyle.red, label="", emoji="<a:unscreen:1203119910805311588>", custom_id="disconnect", row=2)
    async def btn_disconnect(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_user_voice(interaction): return
        if self.player:
            await self.player.disconnect()
            with sqlite3.connect("data/music.db") as db:
                cursor = db.cursor()
                cursor.execute("UPDATE db_music SET bool = 'False' WHERE guild_id = ?", (interaction.guild.id,))
                db.commit()
            await interaction.response.send_message("Disconnected.", ephemeral=True)          

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.player = None
        
    async def webhook(self) -> None :
        connect_wavalink = [wavelink.Node(uri="ws://127.0.0.1:yourport", password="yourpassword")]
        await wavelink.Pool.connect(nodes=connect_wavalink, client=self.bot, cache_capacity=100)

    async def online_wavelink(self, payload: wavelink.NodeReadyEventPayload) -> None:
        logging.info(f"Wavelink connected: {payload.node!r} Resumed: {payload.resumed}")
        
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player: return
        track: wavelink.Playable = payload.track
        self.player = player
    
        embed = discord.Embed(title="", color=discord.Color(value=0xFC89EB))
        embed.set_author(name=f"Music is playing {track.title}", icon_url=self.bot.user.display_avatar.url)
        
        remaining_seconds = track.length / 1000
        future_time = datetime.now() + timedelta(seconds=remaining_seconds)
        unix_timestamp = int(future_time.timestamp())
        
        embed.add_field(name="Play songs by", value=f"<@{self.bot.user.id}>", inline=True)
        embed.add_field(name="Sound room", value=f"<#{player.channel.id}>", inline=True)
        embed.add_field(name="Music will end in", value=f"<t:{unix_timestamp}:R>", inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.set_thumbnail(url=track.artwork)
        
        if player.queue:
            embed.add_field(name="Next song", value="", inline=False) 
            for i, playlist_list in enumerate(player.queue[:1], start=1):
                embed.add_field(name="", value=f"```{playlist_list}```", inline=False)
        else:
            embed.add_field(name="Next song", value="```No more songs to play```", inline=False)

        with sqlite3.connect("data/music.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT channel_id FROM db_music WHERE guild_id = ?", (player.guild.id,))
            fetch_one = cursor.fetchone()
            channel = self.bot.get_channel(int(fetch_one[0])) if fetch_one else None

            if channel:
                try:
                    cursor.execute("SELECT message_playing FROM db_music WHERE guild_id = ?", (player.guild.id,))
                    fetch_one_message_playing = cursor.fetchone()
                    if fetch_one_message_playing:
                        try:
                            message = await channel.fetch_message(int(fetch_one_message_playing[0]))
                            await message.delete()
                        except discord.NotFound:
                            pass
                        except discord.Forbidden:
                            pass
                except Exception as e:
                    logging.warning(f"Error handling playing message: {e}")

                message = await channel.send(embed=embed, view=MusicControllerView(player, self.bot))
                cursor.execute("UPDATE db_music SET message_playing = ? WHERE guild_id = ?", (message.id, player.guild.id))

                cursor.execute("SELECT channel_id, message_id FROM db_box_music WHERE guild_id = ?", (player.guild.id,))
                box_data = cursor.fetchone()
                
                if box_data:
                    box_channel = self.bot.get_channel(int(box_data[0]))
                    if box_channel:
                        if player.queue:
                            queue_len = len(player.queue)
                            embeds = discord.Embed(title="", description=f"🎤 **Playing {track.title} Currently, there are {queue_len} songs in the queue.**", color=discord.Color(value=0xFF9999))
                        else:
                            embeds = discord.Embed(title="", description=f"🎤 **Playing song {track.title} in the moment**", color=discord.Color(value=0xFF9999))
                        embeds.set_author(name="Music Box | Ready to play 🌙", icon_url=self.bot.user.display_avatar.url)
                        
                        try:
                            edited_message = await box_channel.fetch_message(int(box_data[1]))
                            await edited_message.edit(embed=embeds)
                        except:
                            new_msg = await box_channel.send(embed=embeds)
                            cursor.execute("UPDATE db_box_music SET message_id = ? WHERE guild_id = ?", (new_msg.id, player.guild.id))
            db.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        print('music.py loaded')
        await self.webhook()
        success_count = 0
        failure_count = 0

        with sqlite3.connect("data/music.db") as db:
            cursor = db.cursor()
            for guild in self.bot.guilds:
                try:
                    cursor.execute("UPDATE db_music SET bool = 'False' WHERE guild_id = ?", (guild.id,))
                    db.commit()

                    cursor.execute("SELECT channel_id, message_id FROM db_box_music WHERE guild_id = ?", (guild.id,))
                    box_data = cursor.fetchone()

                    if box_data:
                        channel = self.bot.get_channel(int(box_data[0]))
                        if channel:
                            edited_message = await channel.fetch_message(int(box_data[1]))
                            embed = discord.Embed(title="", description="**No music is currently playing**", color=discord.Color(value=0xF68B71))
                            embed.set_author(name="Music Box | Ready to play 🌙", icon_url=self.bot.user.display_avatar.url)

                            messages_to_delete = [msg async for msg in channel.history(limit=None) if str(msg.id) != str(box_data[1])]
                            delete_tasks = [msg.delete() for msg in messages_to_delete]
                            if delete_tasks:
                                await asyncio.gather(*delete_tasks)
                            
                            await edited_message.edit(embed=embed)
                            success_count += 1
                        else:
                            failure_count += 1
                    else:
                        failure_count += 1
                except Exception as e:
                    logging.error(f'Error updating database for guild {guild.id}: {e}')
                    failure_count += 1

        print(f'Processing complete: {success_count} guilds updated successfully, {failure_count} failures.')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        member = message.guild.me
        if not member: return

        is_admin = any(role.permissions.administrator for role in member.roles)

        if is_admin:
            with sqlite3.connect("data/music.db") as db:
                cursor = db.cursor()
                cursor.execute("SELECT channel_id FROM db_box_music WHERE guild_id = ?", (message.guild.id,))
                fetch_one = cursor.fetchone()
                
                if fetch_one and message.channel.id == int(fetch_one[0]):
                    music_query = message.content
                
                    player = cast(wavelink.Player, message.guild.voice_client)  
                    tracks: wavelink.Search = await wavelink.Playable.search(music_query)
                    
                    if not tracks:
                        await message.delete()
                        embed = discord.Embed(color=discord.Colour.red())
                        embed.add_field(name="No tags were found matching that search term. Please try again.", value="", inline=False)
                        message_notify = await message.channel.send(embed=embed)
                        await asyncio.sleep(10)
                        await message_notify.delete()
                        return

                    if not player:
                        try:
                            player = await message.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
                        except AttributeError:
                            await message.delete()
                            embed = discord.Embed(color=discord.Colour.red())
                            embed.add_field(name="Please join a voice channel before using the music bot commands.", value="", inline=False)
                            message_notify = await message.channel.send(embed=embed)
                            await asyncio.sleep(10)
                            await message_notify.delete()
                            return
                    else:
                        if message.author.voice.channel.id != player.channel.id:
                            await message.delete()
                            embed = discord.Embed(color=discord.Colour.red())
                            embed.add_field(name="Please join the same voice channel as the bot before using the music bot commands.", value="", inline=False)
                            message_notify = await message.channel.send(embed=embed)
                            await asyncio.sleep(10)
                            await message_notify.delete()
                            return
                        
                    player.autoplay = wavelink.AutoPlayMode.partial

                    if not hasattr(player, "home"):
                        player.home = message.channel

                    cursor.execute("SELECT channel_id FROM db_music WHERE guild_id = ?", (message.guild.id,))
                    if cursor.fetchone():
                        cursor.execute("UPDATE db_music SET channel_id = ? WHERE guild_id = ?", (message.channel.id, message.guild.id))
                    else:
                        cursor.execute("INSERT INTO db_music (channel_id, guild_id) VALUES (?, ?)", (message.channel.id, message.guild.id))
                    db.commit()
                    
                    if isinstance(tracks, wavelink.Playlist):
                        added: int = await player.queue.put_wait(tracks)
                        embed = discord.Embed(color=discord.Color.brand_green())
                        embed.set_author(name=f"Add a song to a playlist named {tracks.name} quantity {added} songs added to the list.", icon_url=message.author.display_avatar.url)
                        embed.add_field(name="Used by", value=f"<@{message.author.id}>", inline=True)
                        embed.add_field(name="Artist", value=f"[{tracks[0].author}]({tracks[0].uri})", inline=True)
                        await message.channel.send(embed=embed)
                    else:
                        track: wavelink.Playable = tracks[0]
                        await player.queue.put_wait(track)
                        embed = discord.Embed(color=discord.Color.brand_green())
                        embed.set_author(name=f"Add {track.title} to the queue.", icon_url=message.author.display_avatar.url)
                        embed.add_field(name="Used by", value=f"<@{message.author.id}>", inline=True)
                        embed.add_field(name="Artist", value=f"[{track.author}]({track.uri})", inline=True)
                        await message.channel.send(embed=embed)

                    try:
                        await message.delete()
                    except discord.HTTPException:
                        pass

                    if not hasattr(player, "playing_member_ids"):
                        player.playing_member_ids = []
                    player.playing_member_ids.append(message.author.id)

                    if not player.playing:
                        await player.play(player.queue.get(), volume=30)
        else:
            embed = discord.Embed(color=discord.Colour.red())
            embed.add_field(name="Please grant the following permissions for the bot to function properly", value="```Administrator```", inline=False)
            message_notify = await message.channel.send(embed=embed)
            await asyncio.sleep(10)
            await message_notify.delete()

    @app_commands.command(name="play", description="Play music by bot")
    @app_commands.describe(music="Specify the song title or provide a link.")
    async def play(self, interaction: discord.Interaction, *, music: str) -> None:
        guild = interaction.guild
        if not guild: return
        
        member = guild.me
        if not member: return
        
        is_admin = any(role.permissions.administrator for role in member.roles)

        if is_admin:
            player = cast(wavelink.Player, guild.voice_client)  
            tracks: wavelink.Search = await wavelink.Playable.search(music)

            if not tracks:
                embed = discord.Embed(color=discord.Colour.red())
                embed.add_field(name="No tracks found matching your search. Please try again.", value="", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if not player:
                try:
                    player = await interaction.user.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
                except AttributeError:
                    embed = discord.Embed(color=discord.Colour.red())
                    embed.add_field(name="Please join a voice channel before using the music bot.", value="", inline=False)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            else:
                if interaction.user.voice.channel.id != player.channel.id:
                    embed = discord.Embed(color=discord.Colour.red())
                    embed.add_field(name="Please join the same voice channel as the bot before using the music bot.", value="", inline=False)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
            player.autoplay = wavelink.AutoPlayMode.partial

            if not hasattr(player, "home"):
                player.home = interaction.channel
            
            with sqlite3.connect("data/music.db") as db:
                cursor = db.cursor()
                cursor.execute("SELECT channel_id FROM db_music WHERE guild_id = ?", (guild.id,))
                if cursor.fetchone():
                    cursor.execute("UPDATE db_music SET channel_id = ? WHERE guild_id = ?", (interaction.channel.id, guild.id))
                else:
                    cursor.execute("INSERT INTO db_music (channel_id, guild_id) VALUES (?, ?)", (interaction.channel.id, guild.id))
                db.commit()

            if isinstance(tracks, wavelink.Playlist):
                track: wavelink.Playable = tracks[0]
                added: int = await player.queue.put_wait(tracks)
                embed = discord.Embed(color=discord.Color.brand_green())
                embed.set_author(name=f"Add a song to a playlist named {tracks.name} quantity {added} songs added to the list.", icon_url=interaction.user.display_avatar.url)
                embed.add_field(name="Use command by", value=f"<@{interaction.user.id}>", inline=True)
                await interaction.response.send_message(embed=embed)
            else:
                track: wavelink.Playable = tracks[0]
                await player.queue.put_wait(track)
                embed = discord.Embed(color=discord.Color.brand_green())
                embed.set_author(name=f"Add a song to the queue named {track.title}.", icon_url=interaction.user.display_avatar.url)
                embed.add_field(name="Use command by", value=f"<@{interaction.user.id}>", inline=True)
                embed.add_field(name="Artist", value=f"[{track.author}]({track.uri})", inline=True)
                await interaction.response.send_message(embed=embed)

            if not hasattr(player, "playing_member_ids"):
                player.playing_member_ids = []
            player.playing_member_ids.append(interaction.user.id)

            if not player.playing:
                await player.play(player.queue.get(), volume=30)

            try:
                await interaction.message.delete()
            except discord.HTTPException:
                pass
        else:
            embed = discord.Embed(color=discord.Colour.red())
            embed.add_field(name="Please grant the following permissions so that the bot can function.", value="```Admin```", inline=False)
            await interaction.response.send_message(embed=embed) 
        
    @commands.Cog.listener()
    async def on_wavelink_player_update(self, payload: wavelink.PlayerUpdateEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if player.playing:
            with sqlite3.connect("data/music.db") as db:
                cursor = db.cursor()
                cursor.execute("UPDATE db_music SET bool = 'True' WHERE guild_id = ?", (player.guild.id,))
                db.commit()
        
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        with sqlite3.connect("data/music.db") as db:
            cursor = db.cursor()
            cursor.execute("UPDATE db_music SET bool = 'False' WHERE guild_id = ?", (player.guild.id,))
            db.commit()
        
        await asyncio.sleep(20)

        with sqlite3.connect("data/music.db") as db:
            cursor = db.cursor()
            cursor.execute("SELECT bool FROM db_music WHERE guild_id = ?", (player.guild.id,))
            fetch_one = cursor.fetchone()

            if fetch_one and fetch_one[0] == "True":
                return

        if player.queue.mode == wavelink.QueueMode.normal:
            await player.disconnect()
            with sqlite3.connect("data/music.db") as db:
                cursor = db.cursor()
                cursor.execute("UPDATE db_music SET bool = 'False' WHERE guild_id = ?", (player.guild.id,))
                db.commit()
                    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user:
            if before.channel is not None and after.channel is None:
                with sqlite3.connect("data/music.db") as db:
                    cursor = db.cursor()
                    cursor.execute("SELECT channel_id, message_id FROM db_box_music WHERE guild_id = ?", (member.guild.id,))
                    box_data = cursor.fetchone()

                    if box_data:
                        channel = self.bot.get_channel(int(box_data[0]))
                        message_id_to_keep = int(box_data[1])
                        
                        embed = discord.Embed(title="", description="**No music is currently playing**", color=discord.Color(value=0xF68B71))
                        embed.set_author(name="Music Box | Ready to play 🌙", icon_url=self.bot.user.display_avatar.url)
                        
                        def check(message):
                            return message.id != message_id_to_keep

                        if channel:
                            await channel.purge(limit=None, check=check)
                            try:
                                edited_message = await channel.fetch_message(message_id_to_keep)
                                await edited_message.edit(embed=embed)
                            except discord.NotFound:
                                pass

                    cursor.execute("UPDATE db_music SET bool = 'False' WHERE guild_id = ?", (member.guild.id,))
                    db.commit()
            return

        if self.bot.voice_clients:
            for voice_client in self.bot.voice_clients:
                if voice_client.channel == before.channel:
                    if len(before.channel.members) == 1:
                        await asyncio.sleep(20)
                        if len(before.channel.members) == 1:
                            await voice_client.disconnect()
                            with sqlite3.connect("data/music.db") as db:
                                cursor = db.cursor()
                                cursor.execute("UPDATE db_music SET bool = 'False' WHERE guild_id = ?", (member.guild.id,))
                                db.commit()
                    break

async def setup(bot):
    await bot.add_cog(Music(bot))


