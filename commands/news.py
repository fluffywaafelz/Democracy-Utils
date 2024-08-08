import discord
from discord import app_commands
from discord.ext import commands
from utils.file_operations import ensure_json_file, load_channels, get_review_channel_id
from utils.news_operations import load_requests, save_request, create_request
import json
from config import d_color, news_channel_id, staff_roles


def setup_news_commands(bot):
    news_group = app_commands.Group(name="news", description="News related commands")
    
    def has_staff_role(interaction):  # Function to check if user has any staff role
        # Fetch the member to ensure roles are up-to-date
        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            return False
        user_roles = [role.id for role in member.roles]
        matching_roles = [role_id for role_id in staff_roles if role_id in user_roles]
        if matching_roles:
            return True
        else:
            embed = discord.Embed(title="No Permission", color=d_color, description="""
                                  You do not have permission to execute this command!""")
            interaction.response.send_message(embed=embed)
            return False
    
    @news_group.command(name="setreviewchannel", description="Set review channel for news articles.")
    @app_commands.check(has_staff_role) 
    async def news_setreviewchannel(interaction: discord.Interaction, channel: discord.TextChannel):
        
        try:
            with open('main.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        data['review_channel_id'] = channel.id

        with open('main.json', 'w') as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(f'Review channel set to {channel.mention}')

    @news_group.command(name="request", description="Send a request to link your news channel to #news")
    async def news_request(interaction: discord.Interaction, channelid: str, discord_invite: str):
        ensure_json_file('requests.json')
        ensure_json_file('channels.json')

        channels = load_channels()

        if str(channelid) in channels:
            await interaction.response.send_message("This news channel is already registered")
            return

        channel_id = int(channelid)

        try:
            channel = await bot.fetch_channel(channel_id)
            if not channel:
                raise discord.NotFound("Channel not found")

            guild = channel.guild
        except discord.errors.NotFound:
            embed = discord.Embed(title="Channel Not Found", color=d_color, description="The channel you inputted was not found. Ensure the channel ID is correct.")
            await interaction.response.send_message(embed=embed)
            return
        except discord.errors.Forbidden:
            embed = discord.Embed(title="Channel Not Found", color=d_color, description="The bot does not have access to the server where this channel is located. To invite the bot to your news server, click on the bot's profile and click 'Add App'")
            await interaction.response.send_message(embed=embed)
            return

        requests = load_requests()
        new_request = create_request(channel_id, discord_invite, interaction.user.id)
        requests.update(new_request)

        save_request(requests)

        request_id = list(new_request.keys())[0]
        embed = discord.Embed(
            title="News Registration Request",
            color=discord.Color.blue(),
            description=f"""
                A new request has been submitted to link a news company to <#754622580777812130>!
                **INFORMATION**
                > Channel: <#{channel_id}>
                > Discord Invite: [Discord Invite Link]({discord_invite})
                > Requester: <@{interaction.user.id}>
                > Request ID: `{request_id}`
                To accept this request, use `/news accept-request <id>` or deny with `/news deny-request <id>`."""
        )

        embed2 = discord.Embed(
            title="Request Sent",
            color=discord.Color.blue(),
            description="Your request has successfully been sent in and is under review!"
        )

        await interaction.response.send_message(embed=embed2, ephemeral=True)

        log_channel_id = get_review_channel_id()
        log_channel = bot.get_channel(log_channel_id)

        if log_channel:
            await log_channel.send(embed=embed)
        else:
            await interaction.response.send_message("Review channel not found, please report this to an administrator!", ephemeral=True)

    @news_group.command(name="accept-request", description="Accept a news registration request.")
    @app_commands.check(has_staff_role) 
    async def news_accept_request(interaction: discord.Interaction, request_id: str):
        ensure_json_file('channels.json')
        ensure_json_file('requests.json')

        with open('channels.json', 'r') as c:
            channels = json.load(c)

        requests = load_requests()
        request = requests.pop(request_id, None)

        if request:
            channel_id = request['channel_id']
            requester_id = request['requester_discord_id']
            channels[channel_id] = request_id

            with open('channels.json', 'w') as c:
                json.dump(channels, c, indent=4)

            save_request(requests)

            await interaction.response.send_message(f'Accepted request with ID: `{request_id}`')
            guild_name = bot.get_channel(channel_id).guild.name
            news_channel = bot.get_channel(news_channel_id)
            await news_channel.send(f"**{guild_name}** - <#{channel_id}> has been added to the newsfeed!")
        else:
            await interaction.response.send_message('Request not found. Either already accepted/denied or ID inputted incorrectly.')

    @news_group.command(name="deny-request", description="Deny a news registration request.")
    @app_commands.check(has_staff_role) 
    async def news_deny_request(interaction: discord.Interaction, request_id: str):
        ensure_json_file('requests.json')

        requests = load_requests()
        request = requests.pop(request_id, None)

        if request:
            save_request(requests)
            await interaction.response.send_message(f'Denied request with ID: `{request_id}`')
        else:
            await interaction.response.send_message('Request not found. Either already accepted/denied or ID inputted incorrectly.')

    @news_group.command(name="remove", description="Remove a news registration")
    @app_commands.check(has_staff_role) 
    async def news_remove(interaction: discord.Interaction, channel_id: str):
        ensure_json_file('channels.json')

        with open('channels.json', 'r') as f:
            channels = json.load(f)

        if channel_id in channels:
            user_channel = bot.get_channel(int(channel_id))
            guild_name = user_channel.guild.name
            news_channel = bot.get_channel(news_channel_id)
            del channels[channel_id]
            with open('channels.json', 'w') as f:
                json.dump(channels, f, indent=4)
            await interaction.response.send_message(f"Channel ID {channel_id} has been successfully removed.")
            await news_channel.send(f"**{guild_name}** - <#{channel_id}> has been removed from the newsfeed!")
        else:
            await interaction.response.send_message(f"The specified Channel ID was not found.")

    @news_group.command(name="list", description="List all news registrations.")
    async def news_list(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Registered Channels",
            color=discord.Color.blue()
        )
        ensure_json_file('channels.json')

        with open('channels.json', 'r') as f:
            channels = json.load(f)

        if channels:
            for channel_id, linked_channel_id in channels.items():
                try:
                    channel = await bot.fetch_channel(int(channel_id))
                    if channel:
                        guild_name = channel.guild.name
                        embed.add_field(
                            name=f"Guild: {guild_name}",
                            value=f"Channel ID: {channel_id}\nChannel Link: <#{channel_id}>",
                            inline=False
                        )
                except discord.errors.NotFound:
                    pass
        else:
            embed = discord.Embed(title="Registered News Channels", description="No channels registered.", color=d_color)

        await interaction.response.send_message(embed=embed)

    bot.tree.add_command(news_group)
