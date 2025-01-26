import discord
from discord.ext import commands
from discord.utils import get
import requests
from openai import OpenAI


intents=discord.Intents.default()
intents.message_content = True
intents.voice_states = True
threshold = 1

client = commands.Bot(intents=intents, command_prefix="!")

DISCORD_TOKEN = "[Discord Token]"
FFMPEG_PATH = 'ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'


aiClient = OpenAI()

#Reply = False
voice_clients = {}
channels = {}
voices = {}
botenabled = {}
Speaker = {}

messageQueue = []

def checkMessageQueue(message):
    if len(messageQueue) >= 1:
        text = messageQueue[0]
        messageQueue.remove(text)
        voice_client = voice_clients[message.guild.id]
        tts_url = get_tts_path(text, message)
        if tts_url:
            response = requests.get(tts_url)
            with open("output.mp3", "wb") as f:
                f.write(response.content)
            voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source="output.mp3"), after=lambda e: checkMessageQueue(message))


def botResponse(text, author):
    print(text)
    sendMessage = author + ": " + text

    contentMessage = "You are called brian. The messages you will be sent will always take the form of [name]: [message], where name is the author of the message and message is the message you will respond to. you will respond according to these profiles about different authors, if someone doesn't have a profile you will just act as a friend. each new profile is on a new line; \n Nexy: she is your submissive pet that loves to be degraded, you should answer her like you're her owner and degrade her as much as you can. \n Nobo: a girl that wants to be talked to in a sassy tone. \n Gris: he's french so respond in french. \n Syn: he's big strong gym bro, talk to him in gym metaphors. he loves to get drunk. He's super cute \n Barou: he is an idiot this means you should gaslight him whenever possible. \n Shiro: she is always stinky so treat her this way. \n Kato: he is welsh so you should speak to him in a welsh accent. \n roselicious: she loves to be flirted with, so be as flirty as possible with her. \n Sora: He's everyone's boyfriend so treat him like he's your boyfriend. \n itskurai: he's an australian, you should comment on this as much as possible at try to speak in an australian accent. \n Ghenka: he loves to be called 'king'. Treat him like he's your best friend, like you're bro. \n Auri: She is Sora's girlfriend, so you should act extremely jealous around her. \n Nyata: Please act like xal'atath from world of warcraft when you are responding to her. treat her like she's your submissive brat. \n KamuiStrife: his nickname is kana, he is a cute little kitty cat, please communicate to him this way. \n Protein: He's super cool swedish guy, but always doing ERP"

    completion = aiClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": contentMessage},
            {
                "role": "user",
                "content": sendMessage
            }
        ]
    )

    reply = completion.choices[0].message.content
    return reply

def get_tts_path(text, message):
    url = ""
    voice = "Brian"
    try:
        voice = voices[message.guild.id + message.author.id]
        url = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={text}"
    except:
        url = f"https://api.streamelements.com/kappa/v2/speech?voice=Brian&text={text}"
    response = requests.get(url)
    if response.status_code == 200:
        return url
    else:
        print("failed to get url:", response.status_code, response.text)
        return None


def checkHTTP(text, i):
    http = "https://"
    hold = ""

    if text[i] == "h":
        for x in range(8):
            if (text[i + x] == http[x]):
                hold += text[i + x]
            
        if hold == http:
            print("link")
            return True
    print("no Link")
    return False

def messageTransform(messageText, messageAuthor):
    print(messageText)
    emoteStart = 0
    emoteEnd = 0
    linkStart = 0 
    linkEnd = 0
    transformedMesage = messageText

    if transformedMesage == "":
        transformedMesage = "image"

    ##detecting and removing emotes from the message
    for i in range(len(transformedMesage)):
        if i < len(transformedMesage):
            if transformedMesage[i] == "<":
                print(f"EmoteStart:{i}")
                for j in range(len(transformedMesage)):
                    if j < len(transformedMesage):
                        if transformedMesage[j] == " " and j > i:
                            break
                        elif transformedMesage[j] == ">" and j > i:
                            print(f"emoteEnd:{j}")
                            emoteStart = i
                            emoteEnd = j

                            oldMessage = transformedMesage
                            transformedMesage = ""
                            for x in range(len(oldMessage)):
                                if x < emoteStart or x > emoteEnd:
                                    transformedMesage += oldMessage[x]
                            break

    if transformedMesage == "":
        transformedMesage = "Emote"
    
    ##detecting and removing links from the message
    for i in range(len(transformedMesage)):
        if i < len(transformedMesage) and i+7 < len(transformedMesage):
            if checkHTTP(transformedMesage, i):
                for j in range(len(transformedMesage)):
                    if j < len(transformedMesage):
                        if (transformedMesage[j] == " " and j > i) or j >= len(transformedMesage)-1:
                            linkStart = i
                            linkEnd = j
                
                            oldMessage = transformedMesage
                            transformedMesage = ""
                            for x in range(len(oldMessage)):
                                if x < linkStart or x > linkEnd:
                                    transformedMesage += oldMessage[x]
                            break
            
    
    if transformedMesage == "":
        transformedMesage = "link"

    ##detecting and removing spoilers from the message
    for i in range(len(transformedMesage)):
        if i < len(transformedMesage) and i+1 < len(transformedMesage):
            if transformedMesage[i] == "|" and transformedMesage[i + 1] == "|":
                for j in range(len(transformedMesage)):
                    if j < len(transformedMesage) and j+1< len(transformedMesage):
                        if transformedMesage[j] == "|" and transformedMesage[j + 1] == "|" and (j != i and j != i+1):
                            spoilerStart = i
                            spoilerEnd = j+1

                            oldMessage = transformedMesage
                            transformedMesage = ""
                            spoilerInsert = False
                            for x in range(len(oldMessage)):
                                if x < spoilerStart or x > spoilerEnd:
                                    transformedMesage += oldMessage[x]
                                elif spoilerInsert == False:
                                    transformedMesage += "[spoiler]"
                                    spoilerInsert = True
                            break
    
    #if messageAuthor.name == "dennnie288":
        #transformedMesage = "I cute ♥"
        
    return transformedMesage
                    
        


@client.event
async def on_ready():
    print(f"logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    print(message.channel)
    if message.content == "!skip":
        if message.guild.id in voice_clients():
            voice_client = voice_clients[message.guild.id]
            if voice_client.is_playing():
                voice_client.stop()
    if message.content == "!join":
        if message.author.voice and message.author.voice.channel:
            channel = message.author.voice.channel
            if message.guild.id not in voice_clients:
                voice_client = await channel.connect()
                voice_clients[message.guild.id] = voice_client
                channels[message.guild.id] = channel
                botenabled[message.guild.id] = True
                await message.channel.send(f'Joined {channel}')
            else:
                await message.channel.send('I am already in a voice channel.')
        else:
            await message.channel.send('You are not in a voice channel.')

    elif message.content == "!leave":
        if message.guild.id in voice_clients:
            voice_client = voice_clients[message.guild.id]
            if voice_client.is_connected():
                await voice_client.disconnect()
                del voice_clients[message.guild.id]
                del channels[message.guild.id]
                del botenabled[message.guild.id]
                del Speaker[message.guild.id]
                await message.channel.send('Disconnected from the voice channel.')
            else:
                await message.channel.send('I am not connected to a voice channel. DO NOT kick the bot from vc in the future. use !leave')
                try:
                    del voice_clients[message.guild.id]
                except:
                    print("failed to delete voice client")
                try:
                    del channels[message.guild.id]
                except:
                    print("failed to delete channel")
                try:
                    del botenabled[message.guild.id]
                except:
                    print("failed to delete botenabled")
                try:
                    del Speaker[message.guild.id]
                except:
                    print("failed to delete speaker")
                await message.channel.send('Disconnected from the voice channel.')
        else:
            await message.channel.send('I am not in a voice channel.')

    elif message.content.startswith("!voice "):
        voice = message.content[len('!voice '):]
        print(voice)
        if voice == 'Brian' or voice == 'Justin' or voice == 'Emma' or voice == 'Matthew':
            voices[message.guild.id + message.author.id] = voice
            await message.channel.send(f"voice is now: {voice}")
        elif voice == 'Bella':
            voices[message.guild.id + message.author.id] = 'en-GB-Wavenet-A'
            await message.channel.send(f"voice is now: Bella")
    
    elif message.content.startswith('!guide') or message.content.startswith('!Guide'):
        guideEmbed = discord.Embed(title='Brian Bot Guide', color=0xff0000, description='A guide for the critically acclaimed brian bot')
        guideEmbed.add_field(name='!voice [voice Name]', value='*Bella\n*Brian\n*Justin\n*Emma\n*Matthew', inline=True)
        guideEmbed.add_field(name='!skip', value='Skips the current message can also just write "." in the chat', inline=True)
        guideEmbed.add_field(name="", value="", inline=False)
        guideEmbed.add_field(name='!join', value='use in vc text channel to connect to vc', inline=True)
        guideEmbed.add_field(name='!leave', value='Remove bot from all VCs', inline=True)
        await message.channel.send(embed=guideEmbed)

    elif message.content.startswith('!brian'):
        messagetext = message.content[len('!brian '):]
        messageauthor = message.author.name
        if message.author.nick != None:
            messageauthor = message.author.nick
        reply = botResponse(messagetext, messageauthor)
        await message.channel.send(reply)
        if message.guild.id in voice_clients and message.guild.id in channels:
            voiceclient = voice_clients[message.guild.id]
            vcChannel = channels[message.guild.id]
            tts_url = get_tts_path(reply, message)
            if tts_url:
                response = requests.get(tts_url)
                with open("output.mp3", "wb") as f:
                    f.write(response.content)
                voiceclient.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source="output.mp3"), after=lambda e: print("done", e))
            else:
                await message.channel.send("failed to generate tts")

    elif message.content.startswith('!Say'):
        if message.author.name == "nexyki":
            messagetext = message.content[len('!Say '):]
            voice_client = voice_clients[message.guild.id]
            await message.channel.send(messagetext)
            tts_url = get_tts_path(messagetext, message)
            if tts_url:
                response = requests.get(tts_url)
                with open("output.mp3", "wb") as f:
                    f.write(response.content)
                voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source="output.mp3"), after=lambda e: checkMessageQueue(message))
            else:
                await message.channel.send("Failed to generate tts")

    elif message.content.startswith('#'):
        print(f"{message.author.name} didn't use voice")

    else:
        if message.guild.id in voice_clients and message.guild.id in channels:
            voice_client = voice_clients[message.guild.id]
            vcChannel = channels[message.guild.id]
            if message.channel.name == vcChannel.name:
                if voice_client.is_connected():
                    author = message.author.name
                    if message.author.nick != None:
                        author = message.author.nick
                    messageText = message.content
                    messageText = messageTransform(messageText, message.author)

                    if message.guild.id in Speaker:
                        if Speaker[message.guild.id] == message.author.id:
                            text = messageText
                        else:
                            Speaker[message.guild.id] = message.author.id
                            text = f"{author} says: {messageText}"
                    else:
                        Speaker[message.guild.id] = message.author.id
                        text = f"{author} says: {messageText}"
                        
                    tts_url = get_tts_path(text, message)
                    if tts_url:
                        response = requests.get(tts_url)
                        with open("output.mp3", "wb") as f:
                            f.write(response.content)
                        voice_client.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source="output.mp3"), after=lambda e: checkMessageQueue(message))
                    else:
                        await message.channel.send("Failed to generate tts")
                else:
                    await message.channel.send('I am not connected to a voice channel. Use `!join` to invite me to your voice channel. (this could be an error please try !leave if so)')
             
    

client.run(DISCORD_TOKEN)