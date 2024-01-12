import os
import time
import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
from random import randint
import threading
import re
from discordwebhook import Discord
import requests
import json
from file import loadjson, loadtxt, savetxt, savejson
import pickle
from dotenv import load_dotenv

load_dotenv()
TOKEN=os.environ['TOKEN']
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event#init処理
async def on_ready():
    print("起動したンゴねぇ")
    await tree.sync()#スラッシュコマンドを同期
  
    


@client.event
async def on_member_join(member):
  guild = client.get_guild(int(os.environ['serverid']))
  member = guild.get_member(int(member.id))
  await member.edit(nick="透明人間")


@tree.command(name="tokumei",description="DMへの送信のON/OFF")
async def selfsend(ctx:discord.Interaction):
  data = dict(loadjson("dm.json"))
  key = str(ctx.user.id)
  keydata=list(data.keys())
  if key in keydata:
    
    del data[key]
    savejson("dm.json",data)
    await ctx.response.send_message("OFFりました",ephemeral=True)
  else:
    data[key] = "on"
    savejson("dm.json",data)
    await ctx.response.send_message("ONになりました",ephemeral=True)
  

@tree.command(name="chatai",description="beta")
async def chatai(ctx:discord.Interaction,message:str):
  await ctx.response.send_message("BOT：" + talk_api(message))

@tree.command(name="otayori",description="開発者へのお便り")
@discord.app_commands.describe(
    text="送信したい内容を入力してください"
)
async def otayori(ctx:discord.Interaction,text:str):
  webhook= Discord(url=os.environ['otayoriwebhook']) 
  webhook.post(content=text)
  await ctx.response.send_message("お便りありがとう！送信に成功しました！")

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  else:
    DMchannel="Direct Message with Unknown User"
    messagechannel=str(message.channel)
    if (messagechannel==DMchannel):
      if message.attachments:
        print("attach")
        for attachment in message.attachments:
            attachment = str(attachment).split('?')
            print(attachment[0]+"att")
            if attachment[0].endswith(('.jpg', '.png', '.gif')):
                channel = client.get_channel(int(os.environ['onephotochid']))
                ichimai=await channel.fetch_message(int(os.environ['onephotoid']))
                await ichimai.edit(content=attachment[0])
                print(attachment)
      else:
        channel = client.get_channel(int(int(os.environ['fulltokumeiid'])))
        embedcolor=0x37393E
        embed = discord.Embed(description=message.content,color=embedcolor)
        await channel.send(embed=embed)
        guild = client.get_guild(int(os.environ['serverid']))
        my_dict =loadjson("dm.json")
        useridlist=list(my_dict.keys())
        for key in useridlist:
          member = guild.get_member(int(key))
          await member.send(embed=embed)
        print(f"匿名雑談で{message.author}が{message.content}と発言")
        f = open('log.txt', 'a')
        f.write(f"匿名雑談で{message.author}が{message.content}と発言\n")
        f.close()
    if (messagechannel=="リアクションガチャ"):
          from emojis import emojilist
          CustomEmoji=emojilist()
          while len(CustomEmoji) != 1:
             CustomEmoji=emojilist()
          await message.add_reaction(str(CustomEmoji))
    if (messagechannel=="言葉の軽さ"):
       k = open('karuilog.txt', 'a')
       k.write(f"言葉の軽さで{message.author}が{message.content}と発言\n")
       k.close()
       time.sleep(0.75)
       if "おたより" in message.content:
         webhook= Discord(url=os.environ['otayoriwebhook']) 
         webhook.post(content=message.content)
       await message.delete()
    if (messagechannel=="忘却雑談"):
        with open('boukyakulist.pickle', mode='br') as fi:
          b = pickle.load(fi)
        b.append(message.id)
        with open('boukyakulist.pickle', mode='wb') as fo:
          pickle.dump(b, fo)
    if (messagechannel=="連帯言葉の重み"):
      now = datetime.datetime.now()
      after_six_hours = now + datetime.timedelta(hours=6)
      nextomomi=str(after_six_hours.strftime("%H:%M"))
      savetxt("omomitime.txt",nextomomi)
      guild = message.guild
      role = guild.get_role(int(os.environ['roleid']))
      await message.channel.set_permissions(role,send_messages=False)
      embed = discord.Embed(description="ロック中", timestamp=after_six_hours)
      send=await message.channel.send(embed=embed)
      sendid = str(send.id)
      savetxt("omomimessage.txt",sendid)

    if client.user in message.mentions:
      await message.reply(talk_api(message.content))
    if (messagechannel=="一生に一度しか書き込めないチャンネル"):
      await message.channel.set_permissions(message.author, send_messages=False)
    if message.content=="すべてを忘れよう。今すぐ。":
      await task()
      await message.reply("DONE!!!")
      message.reply("夢か…")
    if message.content=="重み確認しろ":
      now = datetime.datetime.now()
      nowtime = now.strftime("%H:%M")
      if str(nowtime)==loadtxt("omomitime.txt"):
        channel = client.get_channel(int(int(os.environ['omomiid'])))
        guild = client.get_guild(int(os.environ['serverid']))
        role = guild.get_role(int(os.environ['roleid']))
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = True
        await channel.set_permissions(role, overwrite=overwrite)
        dmid=loadtxt("omomimessage.txt")
        delmessage=await channel.fetch_message(dmid)
        await message.reply("success")
        await delmessage.delete()
      else:await message.reply("nothing")
      if str(nowtime)==str("3:00") or str(nowtime)==str("9:00") or str(nowtime)==str("15:00") or str(nowtime)==str("21:00"):
        await task()
        message.channel.send("ハッ！夢か…")       
    if message.content=="重み解除しろ":
      channel = client.get_channel(int(int(os.environ['omomiid'])))
      guild = client.get_guild(int(os.environ['serverid']))
      role = guild.get_role(int(os.environ['roleid']))
      overwrite = channel.overwrites_for(role)
      overwrite.send_messages = True
      await channel.set_permissions(role, overwrite=overwrite)
      dmid=loadtxt("omomimessage.txt")
      delmessage=await channel.fetch_message(dmid)
      await message.reply("success")
      await delmessage.delete()
      
      

async def task():
  channel = client.get_channel(int(int(os.environ['boukyakuid'])))
  with open('boukyakulist.pickle', mode='br') as fi:
          b = pickle.load(fi)
  for item in b:
    print(item)
    delmessage=await channel.fetch_message(item)
    await delmessage.delete()
    time.sleep(0.1)
  b=[]
  with open('boukyakulist.pickle', mode='wb') as fo:
          pickle.dump(b, fo)



def talk_api(message):
  apikey = int(os.environ['talkapikey'])
  talk_url = "https://api.a3rt.recruit.co.jp/talk/v1/smalltalk"
  if os.environ['botid'] in message:
    message=message[22:]
  payload = {"apikey": apikey, "query": message}
  print(message)
  response = requests.post(talk_url, data=payload)
  try:
      return response.json()["results"][0]["reply"]
  except:
      print(response.json())
      error=dict(response.json())
      error=list(error.values())
      error=error[1]
      if "empty" in response:output=f"AI「…」(エラーコード:{error}"
      else:output=f"AI「…」(エラーコード:{error})"

      return output

client.run(TOKEN)
