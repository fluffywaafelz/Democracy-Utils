import discord
import json
import aiohttp
from discord.ext import commands, tasks
from commands.news import setup_news_commands
from config import presence, status, bot_token, webhook_url, d_color, SETTINGS
from utils.fetch_posts import get_latest_post, format_content


# Function to ensure the JSON file exists
def ensure_json_file(filename):
    try:
        with open(filename, 'r') as f:
            pass
    except FileNotFoundError:
        with open(filename, 'w') as f:
            json.dump([], f)

# Function to load channels from channels.json
def load_channels():
    ensure_json_file('channels.json')
    with open('channels.json', 'r') as f:
        return json.load(f)

class DemocracyUtilsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="?!", intents=intents)
        self.tree.error(self.on_tree_error)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        await self.change_presence(activity=presence, status=status)
        setup_news_commands(self)  # Setting up news commands
        fetch_posts.start()
        
    async def on_message(self, message):
        # Process message here
        await self.process_message_for_webhook(message)
        await self.process_commands(message)
        
    async def on_tree_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            embed = discord.Embed(title="No Permission", color=d_color, description="""
                                  You do not have permission to execute this command!""")
            await interaction.response.send_message(embed=embed,ephemeral=True)
        else:
            raise error

    async def process_message_for_webhook(self, message):
        channels = load_channels()
        if str(message.channel.id) in channels:
            webhook_url = "https://discord.com/api/webhooks/1262309376597950486/avJYdaTliq4_K1SDIb7DX1I8fcvut8JBz6ECk1hva0MBpavCkU2wvq0_X-5q6EO7nat0"
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(webhook_url, session=session)
                server_icon = message.guild.icon.url if message.guild.icon else None
                server_name = message.guild.name

                content = message.content.replace("@", "") if message.content else None
                embeds = [embed.to_dict() for embed in message.embeds] if message.embeds else None

                if embeds:
                    await webhook.send(
                        content=content,
                        username=server_name,
                        avatar_url=server_icon,
                        embeds=[discord.Embed.from_dict(embed) for embed in embeds]
                    )
                else:
                    await webhook.send(
                        content=content,
                        username=server_name,
                        avatar_url=server_icon
                    )

bot = DemocracyUtilsBot()

@bot.command()
async def sync_commands(ctx):
    """Sync all slash commands in all guilds."""
    await bot.tree.sync()
    print("Command Tree Synced") 
    await ctx.send("All slash commands have been synchronized.")

@tasks.loop(seconds=3)  # Check every 3 seconds (adjust as needed)
async def fetch_posts():
    for (channel_id, forum_id), settings in SETTINGS.items():
        channel = bot.get_channel(channel_id)
        if channel:
            title, content, author_name, post_time, avatar_url, view_url, attachments = get_latest_post(forum_id)
            if title and content:
                embed = discord.Embed(title=title, description=format_content(content), color=settings['color'])
                embed.set_thumbnail(url=settings['thumbnail'])
                embed.set_footer(icon_url=avatar_url, text=f" {author_name} • Today at {post_time.strftime('%H:%M')}")
                embed.add_field(name="View Thread", value=f"[Link]({view_url})", inline=False)

                # Handle attachments
                image_set = False  # To keep track if we have set an image
                for attachment in attachments:
                    if attachment.get('is_video', False) or attachment.get('is_audio', False):
                        # Add video or audio as a field
                        embed.add_field(name="Attachment", value=f"[Link]({attachment['direct_url']})", inline=False)
                    elif 'thumbnail_url' in attachment:
                        # If it's an image and no image has been set yet, set it
                        if not image_set:
                            embed.set_image(url=attachment['thumbnail_url'])
                            image_set = True
                        else:
                            # Add additional images as fields
                            embed.add_field(name="Additional Image", value=f"[Link]({attachment['thumbnail_url']})", inline=True)

                await channel.send(embed=embed)

bot.run(bot_token)
