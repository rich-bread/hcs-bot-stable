import discord
from discord.ext import commands
from module.json_module import open_json

#bot起動時に'discord_settings.json'に記入された設定が有効であるか確認する
class when_ready(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener(name='on_ready')
    async def check_valid_discord_settings(self):
        try:
            #Discord設定を開く
            settings = open_json('settings/discord_settings.json')

            #サーバーIDからサーバーが有効か確認
            guild_id = settings["server"]
            guild = self.bot.get_guild(guild_id)
            if guild == None:
                raise Exception(
                    f"サーバーID: {guild_id}\n"+
                    "エラー: 有効なIDではありません。設定し直してください"
                )

            #カテゴリIDからカテゴリが有効か確認
            category_id_list = [
                settings["admin"]["category"],
                settings["command"]["category"]
            ]
            for category_id in category_id_list:
                category = discord.utils.get(guild.categories, id=category_id)
                if category == None:
                    raise Exception(
                        f"カテゴリID: {category_id}\n"+
                        "エラー: 有効なIDではありません。設定し直してください"
                    )
            
            #チャンネルIDからチャンネルが有効か確認
            channel_id_list = [
                settings["admin"]["channel"]["log"],
                settings["admin"]["channel"]["icon"],
                settings["command"]["channel"]["command"],
                settings["command"]["channel"]["log"]
            ]
            for channel_id in channel_id_list:
                channel = discord.utils.get(guild.channels, id=channel_id)
                if channel == None:
                    raise Exception(
                        f"チャンネルID: {channel_id}\n"+
                        "エラー: 有効なIDではありません。設定し直してください"
                    )
            
            #ロールIDからロールが有効か確認
            role_id_list = [
                settings["role"]["to_use"]
            ]
            for role_id in role_id_list:
                role = discord.utils.get(guild.roles, id=role_id)
                if role == None:
                    raise Exception(
                        f"ロールID: {role_id}\n"+
                        "エラー: 有効なIDではありません。設定し直してください"
                    )

        except Exception as e:
            print(e)
            await self.bot.close()
        
        else:
            print("Discord設定: 有効")

def setup(bot):
    return bot.add_cog(when_ready(bot))
    