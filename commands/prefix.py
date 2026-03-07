from lib.library import *

class Prefix(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('prefix.py loaded')

    setup_group = app_commands.Group(name="setup", description="Set up the music box room.")
            
    @setup_group.command(name="music", description="Setting up a music box room.")
    async def box_music(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return

        user_member = guild.get_member(interaction.user.id)
        bot_member = guild.me  # ดึงข้อมูลตัวบอทแบบ Dynamic

        if not user_member or not bot_member:
            return

        # ตรวจสอบสิทธิ์ผู้ใช้ (Admin หรือ Manage Guild หรือเป็นเจ้าของเซิร์ฟเวอร์)
        user_is_admin = any(role.permissions.administrator for role in user_member.roles)
        user_can_manage = any(role.permissions.manage_guild for role in user_member.roles)
        is_owner = (interaction.user.id == guild.owner_id)

        if is_owner or user_is_admin or user_can_manage:
            # ตรวจสอบสิทธิ์บอท (ต้องเป็น Admin)
            bot_is_admin = any(role.permissions.administrator for role in bot_member.roles)

            if bot_is_admin:
                with sqlite3.connect("data/music.db") as db:
                    cursor = db.cursor()
                    cursor.execute("SELECT channel_id FROM db_box_music WHERE guild_id = ?", (guild.id,))
                    fetch_one = cursor.fetchone()

                    if fetch_one:
                        try:
                            channel_to_delete = discord.utils.get(guild.text_channels, id=int(fetch_one[0]))
                            if channel_to_delete:
                                await channel_to_delete.delete()
                        except Exception as e:
                            logging.warning(f"Failed to delete channel: {e}")
                        
                        channel = await guild.create_text_channel("Name Channel")
                        embed = discord.Embed(title="", description="**Music Box**", color=discord.Color(value=0xF68B71))
                        embed.set_author(name="Music Box | Ready to play 🌙", icon_url=interaction.user.display_avatar.url)
                        message = await channel.send(embed=embed)
                        
                        cursor.execute("UPDATE db_box_music SET channel_id = ?, message_id = ? WHERE guild_id = ?", (channel.id, message.id, guild.id))
                        db.commit()
                    else:
                        channel = await guild.create_text_channel("Name Channel")
                        embed = discord.Embed(title="", description="**Music Box**", color=discord.Color(value=0xF68B71))
                        embed.set_author(name="Music Box | Ready to play 🌙", icon_url=interaction.user.display_avatar.url)
                        message = await channel.send(embed=embed)
                        
                        cursor.execute("INSERT INTO db_box_music (channel_id, guild_id, message_id) VALUES (?, ?, ?)", (channel.id, guild.id, message.id))
                        db.commit()

                embed = discord.Embed(color=discord.Colour.green())
                embed.set_author(icon_url="https://cdn.discordapp.com/emojis/1054627529849323601.gif", name="The system has successfully created the music box room.")
                await interaction.response.send_message(embed=embed)  

            else:
                embed = discord.Embed(color=discord.Colour.red())
                embed.add_field(name="Please grant the following permissions for the bot to function properly", value="```Administrator```", inline=False)
                await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(color=discord.Colour.red())
            embed.add_field(name="You need to have the following permissions to use this command", value="```Manage Server```", inline=False)
            await interaction.response.send_message(embed=embed)
         
async def setup(bot):
    await bot.add_cog(Prefix(bot))