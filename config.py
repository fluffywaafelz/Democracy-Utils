import discord

presence = discord.Activity(type=discord.ActivityType.watching, name="the news")
status = discord.Status.online
d_color = discord.Color.from_rgb(66, 135, 245)
news_channel_id = 754622580777812130
bot_token = ''
webhook_url = ""
staff_roles = [1108337969397502042, 686103866298728473]
XENFORO_API_URL = ''
XENFORO_API_KEY = ''

# Mapping of Discord channel IDs to their respective forum IDs
# Define settings per channel and forum node ID
SETTINGS = {
    (716623940864180245, 2053): {
        'color': discord.Color.pink(),
        'thumbnail': 'https://i.imgur.com/1xiWDK3.png'
    },
    (716623940864180245, 2054): {
        'color': discord.Color.pink(),
        'thumbnail': 'https://i.imgur.com/1xiWDK3.png'
    },
    (1264131687923716096, 2052): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOJ.png'
    },
    (1264130631315750942, 2044): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOE.png'
    },    
    (1264130919950979182, 2045): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOH.png'
    },    
    (1264131687923716096, 2052): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOJ.png'
    },    
    (1085216910158868511, 2048): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DCT.png'
    },    
    (1264130466961817610, 2047): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOC.png'
    },    
    (1264130466961817610, 2047): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOC.png'
    }, 
    (1264130784235749407, 21): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DHS.png'
    }, 
    (1264131119025225828, 25): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DPA.png'
    }, 
    (1264131295886184519, 26): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOI.png'
    }, 
    (1264131536631107628, 126): {
        'color': discord.Color.blue(),
        'thumbnail': 'https://www.democracycraft.net/images/Seal_DOS.png'
    }, 
    # Add more mappings as needed
}