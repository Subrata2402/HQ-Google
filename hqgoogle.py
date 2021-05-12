import discord
import webbrowser
from termcolor import colored
import datetime
import logging
import os
#import Google_Search
import time
from datetime import datetime
from pytz import timezone
from lomond import WebSocket
from unidecode import unidecode
import colorama
import requests
import json
import re
from bs4 import BeautifulSoup
from dhooks import Webhook, Embed
import aniso8601
from time import sleep
#pattern = []



webhook_url="https://discordapp.com/api/webhooks/838421331023233045/-AW8Pfv6d1wcHrn6npWAfTzmimAGFE-vxdjoHUiAjHmnTiXUe1OqpHDMOZghW8MrS15b"

we="https://discordapp.com/api/webhooks/838850742575824966/-DN36GNIQgY3cVaESJI8aEE88BCrXoxrZWT0Z97KDe1I7-p4Fru5-tOudRcmq8JhTnRr"


try:
    hook = Webhook(webhook_url)
except:
    print("Invalid WebHook Url!")


try:
    hq = Webhook(we)
except:
    print("Invalid WebHook Url Lol")



def show_not_on():
    colorama.init()
    # Set up logging
    logging.basicConfig(filename="data.log", level=logging.INFO, filemode="w")

    # Read in bearer token and user ID
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "BTOKEN.txt"), "r") as conn_settings:
        settings = conn_settings.read().splitlines()
        settings = [line for line in settings if line != "" and line != " "]

        try:
            BEARER_TOKEN = settings[0].split("=")[1]
        except IndexError as e:
            logging.fatal(f"Settings read error: {settings}")
            raise e

    print("getting")
    main_url = f"https://api-quiz.hype.space/shows/now?type="
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}",
               "x-hq-client": "Android/1.3.0"}
    # "x-hq-stk": "MQ==",
    # "Connection": "Keep-Alive",
    # "User-Agent": "okhttp/3.8.0"}

    try:
        response_data = requests.get(main_url).json()
    except:
        print("Server response not JSON, retrying...")
        time.sleep(1)

    logging.info(response_data)

    if "broadcast" not in response_data or response_data["broadcast"] is None:
        if "error" in response_data and response_data["error"] == "Auth not valid":
            raise RuntimeError("Connection settings invalid")
        else:
            print("Show not on.")
            tim = (response_data["nextShowTime"])
            tm = aniso8601.parse_datetime(tim)
            x =  tm.strftime("%H:%M:%S [%d/%m/%Y] ")
            x_ind = tm.astimezone(timezone("Asia/Kolkata"))
            x_in = x_ind.strftime("%d/%m/%Y")
            x_i = x_ind.strftime("%H:%M")
    
            prize = (response_data["nextShowPrize"])
            time.sleep(5)
            print(x_in)
            print(prize)
            embed=discord.Embed(title=f"➜〢Date – {x_in}\n➜〢Time – {x_i}AM\n➜〢Prize Money – {prize}", color=0x000000)
            hq.send(embed=embed)



def show_active():
    main_url = 'https://api-quiz.hype.space/shows/now'
    response_data = requests.get(main_url).json()
    return response_data['active']


def get_socket_url():
    main_url = 'https://api-quiz.hype.space/shows/now'
    response_data = requests.get(main_url).json()

    socket_url = response_data['broadcast']['socketUrl'].replace('https', 'wss')
    return socket_url


def connect_websocket(socket_url, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}",
               "x-hq-client": "iPhone8,2"}


    websocket = WebSocket(socket_url)

    for header, value in headers.items():
        websocket.add_header(str.encode(header), str.encode(value))

    for msg in websocket.connect(ping_rate=5):
        if msg.name == "text":
            message = msg.text
            message = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", message)
            message_data = json.loads(message)

            if message_data['type'] == 'question':
                question = message_data['question']
                qcnt = message_data['questionNumber']
                Fullcnt = message_data['questionCount']
                answers = [unidecode(ans["text"]) for ans in message_data["answers"]]
                real_question = str(question).replace(" ","+")
                google_query = "https://google.com/search?q="+real_question
                id1 = message_data["answers"][0]["answerId"]
                id2 = message_data["answers"][1]["answerId"]
                id3 = message_data["answers"][2]["answerId"]

                embed=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**", color=0xff5733)
                embed.add_field(name="**Option -１**", value=f"**[{answers[0]}]({google_query})**", inline=True)
                embed.add_field(name="**Option -２**", value=f"**[{answers[1]}]({google_query})**", inline=True)
                embed.add_field(name="**Option -３**", value=f"**[{answers[2]}]({google_query})**", inline=True)
                #embed.set_footer(text="HQ Google")
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/775385127021969418/816118599869005866/1200px-HQ_logo.svg.png")
                hook.send(embed=embed)

                option1=f"{answers[0]}"
                option2=f"{answers[1]}"
                option3=f"{answers[2]}"
                r = requests.get("http://google.co.in/search?q=" + question + option1 + option2 + option3)
                soup = BeautifulSoup(r.text, 'html.parser')
                response = soup.find_all("span", class_="st")
                res = str(r.text)
                countoption1 = res.count(option1)
                countoption2 = res.count(option2)
                countoption3 = res.count(option3)
                maxcount = max(countoption1, countoption2, countoption3)
                sumcount = countoption1+countoption2+countoption3
                
                if countoption1 == maxcount:
                    embed2=discord.Embed(title=f"**__Google Search Results !__**", description=f"**１. {answers[0]} :** **{countoption1}** ✅\n**２. {answers[1]} :** **{countoption2}**\n**３. {answers[2]} :** **{countoption3}**", color=0x00FBFF)
                    #embed2.add_field(name="**Google Answer :-**", value=f"**Option １. {answers[0]}**")
                    #embed2.set_footer(text="HQ Google | HQ Friends")
                    hook.send(embed=embed2)
                    hook.send("*")
                elif countoption2 == maxcount:
                    embed2=discord.Embed(title=f"**__Google Search Results !__**", description=f"**１. {answers[0]} :** **{countoption1}**\n**２. {answers[1]} :** **{countoption2}** ✅\n**３. {answers[2]} :** **{countoption3}**", color=0x00FBFF)
                    #embed2.add_field(name="**Google Answer :-**", value=f"**Option ２. {answers[1]}**")
                    #embed2.set_footer(text="HQ Google | HQ Friends")
                    hook.send(embed=embed2)
                    hook.send("*")
                else:
                    embed2=discord.Embed(title=f"**__Google Search Results !__**", description=f"**１. {answers[0]} :** **{countoption1}**\n**２. {answers[1]} :** **{countoption2}**\n**３. {answers[2]} :** **{countoption3}** ✅", color=0x00FBFF)
                    #embed2.add_field(name="**Google Answer :-**", value=f"**Option ３. {answers[2]}**")
                    #embed2.set_footer(text="HQ Google | HQ Friends")
                    hook.send(embed=embed2)
                    hook.send("*")

                r = requests.get(google_query)
                soup = BeautifulSoup(r.text , "html.parser")
                result = soup.find("div" , class_='BNeawe').text
                if option1 in result:
                    embed=Embed(title=f"**__Option 1. {option1}__**", description=result, color=0x00ffff)
                    hook.send(embed=embed)
                elif option2 in result:
                    embed=Embed(title=f"**__Option 2. {option2}__**", description=result, color=0x00ffff)
                    hook.send(embed=embed)
                elif option3 in result:
                    embed=Embed(title=f"**__Option 3. {option3}__**", description=result, color=0x00ffff)
                    hook.send(embed=embed)
                else:
                    embed=Embed(title=f"**__Google Search Result !__**", description=result, color=0x00ffff)
                    hook.send(embed=embed)

            elif message_data['type'] == 'answered':
                name = message_data["username"]
                ansid = message_data["answerId"]
                if name == "Thensiharma":
                    name = "Friend - 1"
                elif name == "Samsamhs":
                    name = "Friend - 2"
                elif name == "bjki":
                    name = "Friend - 3"
                elif name == "maxi8654":
                    name = "Friend - 4"
                elif name == "Dsam8":
                    name = "Friend - 5"
                elif name == "rewarydgoubo123":
                    name = "Friend - 6"
                elif name == "Denver9052":
                    name = "Friend - 7"
                elif name == "adnan2512":
                    name = "Friend - 8"
                elif name == "deadshot0198":
                    name = "Friend - 9"
                elif name == "StanleyJacob":
                    name = "Friend - 10"
                elif name == "PowerFor5":
                    name = "Friend - 11"
                elif name == "Serenityi":
                    name = "Friend - 12"
                elif name == "Crashtastic14":
                    name = "Friend - 13"
                elif name == "Mikegrad05":
                    name = "Friend - 14"
                elif name == "theCDP":
                    name = "Friend - 15"
                elif name == "btoff49":
                    name = "Friend - 16"
                else:
                    name = name

                if ansid == id1:
                    embed = discord.Embed(title=f"**__{name}__**", description=f"**||Private Friend|| went Option - 1**", color=0x00ff00)
                    hook.send(embed=embed)
                elif ansid == id2:
                    embed = discord.Embed(title=f"**__{name}__**", description=f"**||Private Friend|| went Option - 2**", color=0x00ff00)
                    hook.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"**__{name}__**", description=f"**||Private Friend|| went Option - 3**", color=0x00ff00)
                    hook.send(embed=embed)

            elif message_data["type"] == "questionClosed":
                embed=discord.Embed(title="⏰ **| Time,s Up!**", color=0xa1fc03)
                hook.send(embed=embed)
                    
            elif message_data["type"] == "questionSummary":
                answer_counts = {}
                correct = ""
                for answer in message_data["answerCounts"]:
                    ans_str = unidecode(answer["answer"])
                    if answer["correct"]:
                        correct = ans_str
                advancing = message_data['advancingPlayersCount']
                eliminated = message_data['eliminatedPlayersCount']
                nextcheck = message_data['nextCheckpointIn']
                ans = (5000)/(int(advancing))
                payout = float("{:.2f}".format(ans))
                total = int(advancing) + int(eliminated)
                percentAdvancing = (int(advancing)*(100))/(int(total))
                pA = float("{:.2f}".format(percentAdvancing))
                percentEliminated = (int(eliminated)*(100))/(int(total))
                pE = float("{:.2f}".format(percentEliminated))
                
                if option1 == correct:
                   # option = int(1)
                    #pattern.append(option)
                    embd=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**", color=0x4286f4)
                    embd.add_field(name="**Correct Answer :-**", value=f"**Option 1️⃣. {correct}**")
                    embd.add_field(name="**Status :-**", value=f"**● Advancing Players : {advancing} ({pA}%)**\n**● Eliminated  Players : {eliminated} ({pE}%)\n● Current Payout : ${payout}**", inline=True)
                    #embd.add_field(name="**Current Pattern :-**", value=pattern)
                    #embd.set_footer(text=f"HQ Google | HQ Friends")
                    hook.send(embed=embd)
                elif option2 == correct:
                   # option = int(2)
                    #pattern.append(option)
                    embd=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**", color=0x4286f4)
                    embd.add_field(name="**Correct Answer :-**", value=f"**Option 2️⃣. {correct}**")
                    embd.add_field(name="**Status :-**", value=f"**● Advancing Players : {advancing} ({pA}%)**\n**● Eliminated  Players : {eliminated} ({pE}%)\n● Current Payout : ${payout}**", inline=True)
                   # embd.add_field(name="**Current Pattern :-**", value=pattern)
                    #embd.set_footer(text=f"HQ Google | HQ Friends")
                    hook.send(embed=embd)
                else:
                   # option = int(3)
                    #pattern.append(option)
                    embd=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**", color=0x4286f4)
                    embd.add_field(name="**Correct Answer :-**", value=f"**Option 3️⃣. {correct}**")
                    embd.add_field(name="**Status :-**", value=f"**● Advancing Players : {advancing} ({pA}%)**\n**● Eliminated  Players : {eliminated} ({pE}%)\n● Current Payout : ${payout}**", inline=True)
                    #embd.add_field(name="**Current Pattern :-**", value=pattern)
                    #embd.set_footer(text=f"HQ Google | HQ Friends")
                    hook.send(embed=embd)

            elif message_data["type"] == "gameSummary":
                winn = message_data['numWinners']
                prizeMoney = str(message_data["winners"][0]["prize"])
                print(message_data)
                embed=discord.Embed(title="**__Game Summary !__**",description=f"**● Payout : {prizeMoney}\n● Total Winners : {winn}\n● Prize Money : $5,000**",color=0x00FBFF)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/737764195743039488/737768505935659178/giphy1.gif")
                #embed.set_footer(text=f"HQ Google | HQ Friends")
                hook.send(embed=embed)
                




"""
def open_browser(question):

    main_url = "https://www.google.co.in/search?q=" + question
    webbrowser.open_new(main_url)
"""

def get_auth_token():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "BTOKEN.txt"), "r") as conn_settings:
        settings = conn_settings.read().splitlines()
        settings = [line for line in settings if line != "" and line != " "]

        try:
            auth_token = settings[0].split("=")[1]
        except IndexError:
            print('No Key is given!')
            return 'NONE'

        return auth_token

while True:
    if show_active():
        url = get_socket_url()
        #print('Connecting to Socket : {}'.format(url))
        #hook.send('Connecting to Socket : {}'.format(url))

        token = get_auth_token()
        if token == 'None':
            print('Please enter a valid auth token.')
        else:
            connect_websocket(url, token)

    else:
        show_not_on()
        time.sleep(300)
