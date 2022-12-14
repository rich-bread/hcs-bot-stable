import asyncio
import discord
from discord.ext import commands
from module.json_module import open_json
from module.discord_module import custom_embed
import database
from log import send_log

class icon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.discord_settings = open_json('settings/discordsettings.json')
        self.send_log = send_log(bot)

    #アイコン提出コマンド
    @commands.command(name='upload')
    async def upload_command(self, ctx):
        try:
            author = ctx.author #コマンド実行者
            role = discord.utils.get(ctx.guild.roles, id=self.discord_settings["role"]["to_use"]) #対象ロール
            frontdesk = await icon.create_frontdesk(self, ctx, role, author) #受付チャンネル
            if frontdesk == None:
                raise Exception
            await frontdesk.send(f"<@{author.id}>") #コマンド実行者にメンション
            await icon.upload_checker(self, ctx, frontdesk, author) #アイコン提出確認
        except Exception as e:
            print("エラー: アイコン提出コマンドを実行中にエラーが発生しました。エラー内容は以下の通り")
            print(e)
        finally:
            await frontdesk.send(embed=custom_embed.default("終了", "10秒後にこのチャンネルは削除されます"))
            await asyncio.sleep(10)
            await author.remove_roles(role)
            await frontdesk.delete()
    
    #受付チャンネルを作成
    async def create_frontdesk(self, ctx, role, author):
        try:
            channelName = self.discord_settings["command"]["frontdesk"]
            categoryId = self.discord_settings["command"]["category"]
            channel = await ctx.guild.create_text_channel(channelName)
            category = discord.utils.get(ctx.guild.channels, id=categoryId)
            await channel.edit(category=category)
            await channel.set_permissions(ctx.guild.default_role, read_messages=True, send_messages=False)
            await channel.set_permissions(role, read_messages=True, send_messages=False)
            await author.add_roles(role)
        except Exception as e:
            await send_log.error()
            print("エラー: 受付チャンネルを作成中にエラーが発生しました。エラー内容は以下の通り")
            print(e)
            return None
        else:
            return channel

    

    #ユーザから送信されたコマンドに画像が添付されているかの確認
    async def upload_checker(self, ctx, channel, author):
        try:
            #ユーザから送信されたメッセージに画像が添付されているかの確認
            try:
                message = ctx.message #メッセージ
                attachments = message.attachments #添付ファイルリスト
                #添付ファイルリストが0の場合、コマンドをはじく
                if len(attachments) == 0:
                    await channel.send(embed=custom_embed.error("画像が添付されていません。画像を添付したうえで再度コマンドの実行をお願いします"))
                    return
            except Exception as e:
                await send_log.error(
                    self, 
                    f"<@{author.id}>さんの画像添付確認中に予期せぬエラーが発生しました。このメッセージが送信されたら運営までご相談ください\n"+
                    f"エラー内容: {e}"
                )
                return

            #ユーザTwitterID確認
            try:
                #コマンド実行者のTwitterIDの入力
                title_userid = "実行者のTwitterID"
                content_userid = "このコマンドを実行しているユーザのTwitterIDを入力してください"
                authorid = await icon.await_message(self, channel, author, title_userid, content_userid)
                if authorid == None: return

                #待機メッセージ
                await channel.send(embed=custom_embed.waiting("有効なTwitterIDであるか確認中"))

                #コマンド実行者のTwitterID登録確認
                author_result = (await database.post_db('user_check', [authorid])).json()
                if author_result[0] != True:
                    await channel.send(embed=custom_embed.error("正しいTwitterIDを入力してください"))
                    return
            except Exception as e:
                await send_log.error(
                    self,
                    f"<@{author.id}>さんのユーザTwitterID確認中に予期せぬエラーが発生しました。このメッセージが送信されたら運営までご相談ください\n"+
                    f"エラー内容: {e}"
                )
                return
            else:
                await channel.send(embed=custom_embed.success("ユーザのTwitterIDを確認"))

            try:
                #コマンド実行者が所属するチームのリーダーのTwitterID入力
                title_leaderid = "チームリーダーのTwitterID"
                content_leaderid = "このコマンドを実行しているユーザが所属するチームのリーダーのTwitterIDを入力してください"
                leaderid = await icon.await_message(self, channel, author, title_leaderid, content_leaderid)
                if leaderid == None: return

                #待機メッセージ
                await channel.send(embed=custom_embed.waiting("有効なTwitterIDであるか確認中"))

                #チームリーダーのTwitterID登録確認
                leader_result = (await database.post_db('user_check', [authorid])).json()
                if leader_result[0] != True:
                    await channel.send(embed=custom_embed.error("正しいTwitterIDを入力してください"))
                    return
            except Exception as e:
                await send_log.error(
                    self,
                    f"<@{author.id}>さんのリーダーTwitterID確認中に予期せぬエラーが発生しました。このメッセージが送信されたら運営までご相談ください\n"+
                    f"エラー内容: {e}"
                )
                return
            else:
                await channel.send(embed=custom_embed.success("リーダーのTwitterIDを確認"))

            try:
                #待機メッセージ
                await channel.send(embed=custom_embed.waiting("コマンド実行者が指定リーダーのチームに所属しているか確認中"))

                #コマンド実行者が指定リーダーのチームに所属しているか確認
                idList = [authorid, leaderid]
                team_result = (await database.post_db('team_check', idList)).json()
                if team_result[0] != True:
                    await channel.send(embed=custom_embed.error("指定したリーダーのチームに所属していません"))
                    return
            except Exception as e:
                await send_log.error(
                    self,
                    f"<@{author.id}>さんの所属チーム確認中に予期せぬエラーが発生しました。このメッセージが送信されたら運営までご相談ください\n"+
                    f"エラー内容: {e}"
                )
                return
            else:
                await channel.send(embed=custom_embed.success("コマンド実行者がリーダーのチームに所属していることを確認"))

            #アイコン提出ログ記入
            try:
                iconUrl = attachments[0].url
                iconData = [authorid, iconUrl]
                await database.post_db('icon_upload', iconData)
                icon_channel = discord.utils.get(ctx.guild.channels, id=self.discord_settings["admin"]["channel"]["icon"])
                await icon_channel.send(f"<@{author.id}>のアイコン↓")
                await icon_channel.send(attachments[0].url)
            except Exception as e:
                await send_log.error(
                    self,
                    f"<@{author.id}>さんのアイコンログ記入中に予期せぬエラーが発生しました。このメッセージが送信されたら運営までご相談ください\n"+
                    f"エラー内容: {e}"
                )
                return

            #ロール付与
            try:
                roleInfo = (await database.get_db('hcsGiveRole', authorid, leaderid)).json()
                roleNameList = []
                roleNameList.append(roleInfo["大会ロール"])
                if roleInfo["リーダーロール"] == "あり":
                    roleNameList.append("チームリーダー")
                if roleInfo["ナンバリングロール"] != "":
                    roleNameList.append("Team"+str(roleInfo["ナンバリングロール"]))
                else:
                    admin_channel = discord.utils.get(ctx.guild.channels, id=self.discord_settings["admin"]["channel"]["log"])
                    await admin_channel.send(
                        embed=custom_embed.error(f"<@{author.id}>さんにチームナンバリングロールが付与できませんでした。手動での追加をお願いします")
                    )

                for roleName in roleNameList:
                    role = discord.utils.get(ctx.guild.roles, name=roleName)
                    await author.add_roles(role)

                log_channel = discord.utils.get(ctx.guild.roles, id=self.discord_settings["command"]["channel"]["log"])
                await log_channel.send(embed=custom_embed.success(f"<@{author.id}>さんにロールを付与しました"))
            except Exception as e:
                await send_log.error(
                    self,
                    f"<@{author.id}>さんのロール付与中に予期せぬエラーが発生しました。このメッセージが送信されたら運営までご相談ください\n"+
                    f"エラー内容: {e}"
                )
                return

        except Exception as e:
            print(e)
            await channel.send(embed=custom_embed.error("予期せぬエラーが発生しました。このメッセージが送信された場合は運営までご連絡ください"))

        else:
            return

    #ユーザからのメッセージを確認する関数
    async def check_message(self, channel, author):
        def check(m: discord.Message):
            return m.channel == channel and m.author.id == author.id
        try:
            message = await self.bot.wait_for('message', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            error = await channel.send(embed=custom_embed.error("待機時間内にメッセージが確認できませんでした"))
            return None
        else:
            return message.content

    #ユーザからのメッセージを待機する関数
    async def await_message(self, channel, author, title, content):
        bot_msg = await channel.send(embed=custom_embed.default(title, content))
        user_msg = await icon.check_message(self, channel, author)
        return user_msg

def setup(bot):
    return bot.add_cog(icon(bot))