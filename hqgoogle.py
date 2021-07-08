import discord
import webbrowser
from termcolor import colored
import datetime
import logging
import os
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
pattern = []


webhook_url="https://discordapp.com/api/webhooks/838421331023233045/-AW8Pfv6d1wcHrn6npWAfTzmimAGFE-vxdjoHUiAjHmnTiXUe1OqpHDMOZghW8MrS15b"



try:
    hook = Webhook(webhook_url)
except:
    print("Invalid WebHook Url!")



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
               "x-hq-client": "Android/1.50.0"}
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
            embed.set_footer(text="HQ Google")
            embed.timestamp = datetime.utcnow()



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
            if message_data['type'] != 'interaction':
                print(message_data)

            if message_data['type'] == 'question':
                question = message_data['question']
                qcnt = message_data['questionNumber']
                Fullcnt = message_data['questionCount']
                answers = [unidecode(ans["text"]) for ans in message_data["answers"]]
                real_question = str(question).replace(" ","+")
                google_query = "https://google.com/search?q="+real_question
                option1=f"{answers[0]}"
                option2=f"{answers[1]}"
                option3=f"{answers[2]}"
                opt = str(f"{option1} {option2} {option3}").replace(" ","+")
                swa = "https://google.com/search?q="+real_question+"+"+opt
                embed=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**\n\n[Search with all options]({swa})", color=0x000000)
                embed.add_field(name="**Option -１**", value=f"**[{option1}]({google_query})**", inline=True)
                embed.add_field(name="**Option -２**", value=f"**[{option2}]({google_query})**", inline=True)
                embed.add_field(name="**Option -３**", value=f"**[{option3}]({google_query})**", inline=True)
                embed.set_footer(text="HQ Google")
                embed.timestamp = datetime.utcnow()
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/775385127021969418/816118599869005866/1200px-HQ_logo.svg.png")
                hook.send(embed=embed)

                r = requests.get(swa)
                soup = BeautifulSoup(r.text, 'html.parser')
                response = soup.find_all("span", class_="st")
                res = str(r.text)
                countoption1 = res.count(option1)
                countoption2 = res.count(option2)
                countoption3 = res.count(option3)
                maxcount = max(countoption1, countoption2, countoption3)
                sumcount = countoption1+countoption2+countoption3
                
                if countoption1 == maxcount:
                    embed2=discord.Embed(title=f"**__Google Results !__**", description=f"**１. {option1} :** **{countoption1}** ✅\n**２. {option2} :** **{countoption2}**\n**３. {option3} :** **{countoption3}**", color=0x000000)
                    hook.send(embed=embed2)
                    
                elif countoption2 == maxcount:
                    embed2=discord.Embed(title=f"**__Google Results !__**", description=f"**１. {option1} :** **{countoption1}**\n**２. {option2} :** **{countoption2}** ✅\n**３. {option3} :** **{countoption3}**", color=0x000000)
                    hook.send(embed=embed2)
                    
                else:
                    embed2=discord.Embed(title=f"**__Google Results !__**", description=f"**１. {option1} :** **{countoption1}**\n**２. {option2} :** **{countoption2}**\n**３. {option3} :** **{countoption3}** ✅", color=0x000000)
                    hook.send(embed=embed2)
                    
                hook.send("*")
                r = requests.get(swa)
                soup = BeautifulSoup(r.text , "html.parser")
                result = soup.find("div" , class_='BNeawe').text
                if option1 in result:
                    embed=discord.Embed(title=f"**__Option １. {option1}__**", description=result, color=0x000000)
                    hook.send(embed=embed)
                elif option2 in result:
                    embed=discord.Embed(title=f"**__Option ２. {option2}__**", description=result, color=0x000000)
                    hook.send(embed=embed)
                elif option3 in result:
                    embed=discord.Embed(title=f"**__Option ３. {option3}__**", description=result, color=0x000000)
                    hook.send(embed=embed)
                else:
                    pass

                r = requests.get(google_query)
                soup = BeautifulSoup(r.text , "html.parser")
                result = soup.find("div" , class_='BNeawe').text
                if option1 in result:
                    embed=discord.Embed(title=f"**__Option １. {option1}__**", description=result, color=0x000000)
                    hook.send(embed=embed)
                elif option2 in result:
                    embed=discord.Embed(title=f"**__Option ２. {option2}__**", description=result, color=0x000000)
                    hook.send(embed=embed)
                elif option3 in result:
                    embed=discord.Embed(title=f"**__Option ３. {option3}__**", description=result, color=0x000000)
                    hook.send(embed=embed)
                else:
                    embed=Embed(title=f"**__Direct Search Result !__**", description=result, color=0x000000)
                    hook.send(embed=embed)


            elif message_data["type"] == "questionClosed":
                embed=discord.Embed(title="⏰ **| Time's Up!**", color=0x000000)
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
                    pattern.append("1")
                    embd=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**", color=0x000000)
                    embd.add_field(name="**Correct Answer :-**", value=f"**Option １. {correct}**")
                    embd.add_field(name="**Status :-**", value=f"**● Advancing Players : {advancing} ({pA}%)**\n**● Eliminated  Players : {eliminated} ({pE}%)\n● Current Payout : ${payout}**", inline=True)
                    embd.add_field(name="**Ongoing Pattern :-**", value=f"**pattern**")
                    embd.set_footer(text="HQ Google")
                    embd.timestamp = datetime.utcnow()
                    hook.send(embed=embd)
                elif option2 == correct:
                    pattern.append("2")
                    embd=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**", color=0x000000)
                    embd.add_field(name="**Correct Answer :-**", value=f"**Option ２. {correct}**")
                    embd.add_field(name="**Status :-**", value=f"**● Advancing Players : {advancing} ({pA}%)**\n**● Eliminated  Players : {eliminated} ({pE}%)\n● Current Payout : ${payout}**", inline=True)
                    embd.add_field(name="**Ongoing Pattern :-**", value=f"**pattern**")
                    embd.set_footer(text="HQ Google")
                    embd.timestamp = datetime.utcnow()
                    hook.send(embed=embd)
                else:
                    pattern.append("3")
                    embd=discord.Embed(title=f"**Question {qcnt} out of {Fullcnt}**",  description=f"**[{question}]({google_query})**", color=0x000000)
                    embd.add_field(name="**Correct Answer :-**", value=f"**Option ３. {correct}**")
                    embd.add_field(name="**Status :-**", value=f"**● Advancing Players : {advancing} ({pA}%)**\n**● Eliminated  Players : {eliminated} ({pE}%)\n● Current Payout : ${payout}**", inline=True)
                    embd.add_field(name="**Ongoing Pattern :-**", value=f"**pattern**")
                    embd.set_footer(text="HQ Google")
                    embd.timestamp = datetime.utcnow()
                    hook.send(embed=embd)
                
            elif message_data["type"] == "gameSummary":
                winn = message_data['numWinners']
                prizeMoney = str(message_data["winners"][0]["prize"])
                print(message_data)
                embed=discord.Embed(title="**__Game Summary !__**",description=f"**● Payout : {prizeMoney}\n● Total Winners : {winn}\n● Prize Money : $5,000**", color=0x000000)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/737764195743039488/737768505935659178/giphy1.gif")
                embed.set_footer(text="HQ Google")
                embed.timestamp = datetime.utcnow()
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

        token = get_auth_token()
        if token == 'None':
            print('Please enter a valid auth token.')
        else:
            connect_websocket(url, token)

    else:
        show_not_on()
        time.sleep(300)
