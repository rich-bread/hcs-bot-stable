import discord
from discord.ext import commands
from module.json_module import open_json
from module.discord_module import custom_embed

class send_log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.discord_settings = open_json('settings/discordsettings.json')

    async def success(self, content):
        print(content)
        guild_id = self.discord_settings["server"]
        guild = self.bot.get_guild(guild_id)
        admin_log_channel = discord.utils.get(guild.channels, id=self.discord_settings["admin"]["channel"]["log"])
        command_log_channel = discord.utils.get(guild.channels, id=self.discord_settings["command"]["channel"]["log"])
        await admin_log_channel.send(embed=custom_embed.success(content))
        await command_log_channel.send(embed=custom_embed.success(content))
        

    async def error(self, content):
        print(content)
        guild_id = self.discord_settings["server"]
        guild = self.bot.get_guild(guild_id)
        admin_log_channel = discord.utils.get(guild.channels, id=self.discord_settings["admin"]["channel"]["log"])
        command_log_channel = discord.utils.get(guild.channels, id=self.discord_settings["command"]["channel"]["log"])
        await admin_log_channel.send(embed=custom_embed.error(content))
        await command_log_channel.send(embed=custom_embed.error(content))