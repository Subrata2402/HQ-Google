import discord, time, requests, json
from unidecode import unidecode
from datetime import datetime

webhook_url = "https://discord.com/api/webhooks/1009531446358188224/d6Ci6RO__ev00Gj4jmElQKL1S9imgiUY9dQ2GHFZbiXb0YYK29bZ7BwkyCx3TcRQ3JtA" # put here webhook url
bearer_token = "" # put here HQ Trivia bearer token
icon_url = "" # put here HQ icon url
pattern = list()

hook = discord.Webhook.from_url(webhook_url, adapter = discord.RequestsWebhookAdapter())

main_url = "https://api-quiz.hype.space/shows/now"
headers = {"Authorization": "Bearer " + bearer_token}

def show_not_on():
	response_data = requests.get(main_url).json()
	if not response_data.get("broadcast"):
		if "error" in response_data and response_data["error"] == "Auth not valid":
			raise RuntimeError("Connection settings invalid")
		else:
			print("Show is not live")
			
def show_active():
	response_data = requests.get(main_url).json()
	return response_data['active']

def connect_websocket():
	response_data = requests.get(main_url).json()
	socket_url = response_data['broadcast']['socketUrl'].replace('https', 'wss')
	websocket = WebSocket(socket_url, headers = headers)
	answer_ids, options = [], []
	google_question = "https://google.com/search?q="
	question, question_number, total_question = None, 0, 0
	for msg in websocket.connect(ping_rate = 5):
		if msg.name == "text":
			message_data = json.loads(msg.text)
			
			if message_data['type'] != 'interaction':
				pass

			elif message_data['type'] == 'question':
				question = message_data['question']
				question_number = message_data['questionNumber']
				total_question = message_data['questionCount']
				options = [unidecode(ans["text"].strip()) for ans in message_data["answers"]]
				answer_ids = [ans["answerId"] for ans in message_data["answers"]]
				raw_question = str(question).replace(" ", "+")
				google_question = "https://google.com/search?q=" + raw_question
				u_options = "+or+".join(options)
				raw_options = str(u_options).replace(" ", "+")
				search_with_all = "https://google.com/search?q=" + raw_question + "+" + raw_options
				
				embed = discord.Embed(color = discord.Colour.random())
				embed.title = f"Question {question_number} out of {total_question}"
				embed.description = f"[{question}]({google_question})\n\n[Search with all options]({search_with_all})"
				for index, option in enumerate(options):
					embed.add_field(name = f"Option - {index+1}", value = f"[{option.strip()}]({google_question + '+' + str(option).strip().replace(' ', '+')})", inline = False)
				embed.set_footer(text = "HQ Trivia")
				embed.set_thumbnail(url = icon_url)
				embed.timestamp = datetime.utcnow()
				hook.send(embed = embed)
				
				r = requests.get(google_question)
				res = str(r.text)
				count_options = [res.count(option) for option in options]
				max_count = max(count_options)
				description = ""
				for index, count_option in enumerate(count_options):
					if max_count != 0 and count_option == max_count:
						description += f"{index+1}. {options[iindex]} : {count_option} ✅\n"
					else:
						description += f"{index+1}. {options[iindex]} : {count_option}\n"
				embed = discord.Embed(title = "__Google Results -１__", description = description, color = discord.Colour.random())
				hook.send(embed = embed)

			elif message_data['type'] == 'answered':
				name = message_data["username"]
				ans_id = message_data["answerId"]
				for index, answer_id in enumerate(answer_ids):
					if ans_id == answer_id:
						embed = discord.Embed(title = f"{name} went Option - {index+1}", color = discord.Colour.random())
						hook.send(embed = embed)

			elif message_data["type"] == "questionClosed":
				embed = discord.Embed(title = "⏰ | Time's Up!", color = discord.Colour.random())
				hook.send(embed = embed)

			elif message_data["type"] == "questionSummary":
				for index, answer in enumerate(message_data["answerCounts"]):
					if answer["correct"]:
						option = answer["answer"]
						ans_num = index + 1
				pattern.append(str(ans_num))
				advance_players = message_data['advancingPlayersCount']
				eliminate_players = message_data['eliminatedPlayersCount']
				ans = 1500/advance_players
				payout = float("{:.2f}".format(ans))
				total_players = advance_players + eliminate_players
				percentAdvancing = (advance_players*100)/total_players
				pA = float("{:.2f}".format(percentAdvancing))
				percentEliminated = (eliminate_players*100)/total_players
				pE = float("{:.2f}".format(percentEliminated))
				
				embed = discord.Embed(
					title = f"Question {question_number} out of {total_question}",
					description = f"[{question}]({google_question})",
					color = discord.Colour.random(),
					timestamp = datetime.utcnow()
					)
				embed.add_field(name = "Correct Answer :-", value = f"Option {ans_num}. {option}", inline = False)
				embed.add_field(name = "Status :-",
					value = f"Advancing Players : {advance_players} ({pA}%)\nEliminated Players : {eliminate_players} ({pE}%)\nCurrent Payout : ${payout}",
					inline = False
				)
				embed.add_field(name = "Ongoing Pattern :-", value = f"{pattern}", inline = False)
				embed.set_footer(text = "HQ Trivia")
				embed.set_thumbnail(url = icon_url)
				hook.send(embed = embed)

			elif message_data["type"] == "gameSummary":
				winn = message_data['numWinners']
				prizeMoney = str(message_data["winners"][0]["prize"])
				embed=discord.Embed(title = "__Game Summary !__", description = f"● Payout : {prizeMoney}\n● Total Winners : {winn}\n● Prize Money : {self.prize}", color = discord.Colour.random())
				embed.set_thumbnail(url = icon_url)
				embed.set_footer(text = "HQ Trivia")
				embed.timestamp = datetime.utcnow()
				hook.send(embed = embed)

while True:
	if show_active():
		connect_websocket()
	else:
		show_not_on()
		time.sleep(300)
