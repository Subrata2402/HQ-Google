  
'''
using discord.py version 1.0.0a
'''
import discord
import asyncio
import re
import multiprocessing
import threading
import concurrent

#BOT_OWNER_ROLE = 'Runner' # change to what you need
#BOT_OWNER_ROLE_ID = "503197827556704268" 
  
g="https://discord.gg/qNNBVDq" 

 
oot_channel_id_list = []


answer_pattern = re.compile(r'(not|n)?([1-3]{1})(\?)?(cnf)?(\?)?$', re.IGNORECASE)

apgscore = 83
nomarkscore = 33
markscore = 13

async def update_scores(content, answer_scores):
    global answer_pattern

    m = answer_pattern.match(content)
    if m is None:
        return False

    ind = int(m[2])-1

    if m[1] is None:
        if m[3] is None:
            if m[4] is None:
                answer_scores[ind] += nomarkscore
            else: # apg
                if m[5] is None:
                    answer_scores[ind] += apgscore
                else:
                    answer_scores[ind] += markscore

        else: # 1? ...
            answer_scores[ind] += markscore

    else: # contains not or n
        if m[3] is None:
            answer_scores[ind] -= nomarkscore
        else:
            answer_scores[ind] -= markscore

    return True

class SelfBot(discord.Client):

    def __init__(self, update_event, answer_scores):
        super().__init__()
        global oot_channel_id_list
        #global wrong
        self.oot_channel_id_list = oot_channel_id_list
        self.update_event = update_event
        self.answer_scores = answer_scores

    async def on_ready(self):
        print("======================")
        print("DANGER TRIVIA || BOTS")
        print("Connected to discord.")
        print("User: " + self.user.name)
        print("ID: " + str(self.user.id))

    # @bot.event
    # async def on_message(message):
    #    if message.content.startswith('-debug'):
    #         await message.channel.send('d')

        def is_scores_updated(message):
            if message.guild == None or \
                str(message.channel.id) not in self.oot_channel_id_list:
                return False

            content = message.content.replace(' ', '').replace("'", "")
            m = answer_pattern.match(content)
            if m is None:
                return False

            ind = int(m[2])-1

            if m[1] is None:
                if m[3] is None:
                    if m[4] is None:
                        self.answer_scores[ind] += nomarkscore
                    else: # apg
                        if m[5] is None:
                            self.answer_scores[ind] += apgscore
                        else:
                            self.answer_scores[ind] += markscore

                else: # 1? ...
                    self.answer_scores[ind] += markscore

            else: # contains not or n
                if m[3] is None:
                    self.answer_scores[ind] -= nomarkscore
                else:
                    self.answer_scores[ind] -= markscore

            return True

        while True:
            await self.wait_for('message', check=is_scores_updated)
            self.update_event.set()

class Bot(discord.Client):

    def __init__(self, answer_scores):
        super().__init__()
        self.bot_channel_id_list = []
        self.embed_msg = None
        self.embed_channel_id = None
        #global wrong
        self.answer_scores = answer_scores

        # embed creation
        #don't edit here
        self.embed=discord.Embed(colour=0xFBC0AC)
        self.embed.add_field(name=f"**__Erased__**", value="**Option =** <a:redload:772439692411011073>", inline=False) 


        #await self.bot.add_reaction(embed,':spy:')


    async def clear_results(self):
        for i in range(len(self.answer_scores)):
            self.answer_scores[i]=0

    async def update_embeds(self):
      #  global wrong

         

        one_check = ""
        two_check = ""
        three_check = ""
        not_answer = "?"
        

        lst_scores = list(self.answer_scores)
        

        highest = max(lst_scores)
        gif_ans = 'https://cdn.discordapp.com/attachments/716879425655799858/726460742924107897/unnamed.gif'
        not_answer = '**Option =** <a:redload:772439692411011073>'
        lowest = min(lst_scores)
        answer = lst_scores.index(highest)+1
        #best_answer= "⚠️"
        #global wrong             

        if highest > 0:
            if answer == 1:
                one_check = "** **✅** **"
                best_answer = ":one: <a:cit:764855340214779914>"
                gif_ans = "https://cdn.discordapp.com/attachments/725037079402119378/725037155298181160/709972997422841856.png"
            else:
                one_check = "❌ "
                not_answer = "**Option =** 1"
                

            if answer == 2:
                two_check = "** **✅** **"
                best_answer = ":two:<a:cit:764855340214779914>"
                gif_ans = "https://cdn.discordapp.com/attachments/725037079402119378/725037208624693278/709972999280787516.png"
            else:
                two_check = "❌"
                not_answer = "**Option =** 2"
                

            if answer == 3:
                three_check = "** **✅** **"
                best_answer = ":three: <a:cit:764855340214779914>"
                gif_ans = "https://cdn.discordapp.com/attachments/725037079402119378/725037316766433344/709973000195145728.png"
            else:
                three_check = "❌"
                not_answer = "**Option =** 3"
                
     

            

        #if lowest < 0:
           # if answer == 2:
             #   one_cheak = ":x:"
          #  if answer == 3:
         #       two_cheak = ":x:"
       #     if answer == 1:
         #       three_cheak = ":x:"
        
        self.embed.set_field_at(0, name="**__Erased__**", value=not_answer, inline=True) 


        if self.embed_msg is not None:
            await self.embed_msg.edit(embed=self.embed)

    async def on_ready(self):
        print("==============")
        print("DANGER TRIVIA || BOTS")
        print("Connected to discord.")
        print("User: " + self.user.name)
        print("ID: " + str(self.user.id))
        log=self.get_channel(77177111713553543)
        await log.send("> **HQ Eraser Bot is Updated** ✅")

        await self.clear_results()
        await self.update_embeds()
        await self.change_presence(activity=discord.Game(name='with '+str(len(set(self.get_all_members())))+' users'))
        await self.change_presence(activity=discord.Activity(type=1,name="HQ Eraser | Subrata#3297 !"))

    async def on_message(self, message):


        # if message is private
        if message.author == self.user or message.guild == None:
            return

        if message.content.lower() == "hr":
            await message.delete()
            
            self.embed_msg = None
            await self.clear_results()
            await self.update_embeds()
            self.embed_msg = \
                await message.channel.send('',embed=self.embed)
            #await self.embed_msg.add_reaction("✅")
            self.embed_channel_id = message.channel.id
       

          

        # process votes
        if message.channel.id == self.embed_channel_id:
            content = message.content.replace(' ', '').replace("'", "")
            updated = await update_scores(content, self.answer_scores)
            if updated:
                await self.update_embeds()

def bot_with_cyclic_update_process(update_event, answer_scores):

    def cyclic_update(bot, update_event):
        f = asyncio.run_coroutine_threadsafe(bot.update_embeds(), bot.loop)
        while True:
            update_event.wait()
            update_event.clear()
            f.cancel()
            f = asyncio.run_coroutine_threadsafe(bot.update_embeds(), bot.loop)
            #res = f.result()

    bot = Bot(answer_scores)

    upd_thread = threading.Thread(target=cyclic_update, args=(bot, update_event))
    upd_thread.start()

    loop = asyncio.get_event_loop()
    loop.create_task(bot.start('NzczOTI4NTc1NzAyNzk0MjUx.X6QXJw.r-U_XbSALwkVzSxK7zg0DTNytvU'))
    loop.run_forever()


def selfbot_process(update_event, answer_scores):

    selfbot = SelfBot(update_event, answer_scores)

    loop = asyncio.get_event_loop()
    loop.create_task(selfbot.start('NjYwMzM3MzQyMDMyMjQ4ODMy.X4xc9g.XML7C0hxrePba_yvU5zapQi3e6U',
                                   bot=False))
    loop.run_forever()

if __name__ == '__main__':

    # running bot and selfbot in separate OS processes

    # shared event for embed update
    update_event = multiprocessing.Event()

    # shared array with answer results
    answer_scores = multiprocessing.Array(typecode_or_type='i', size_or_initializer=4)

    p_bot = multiprocessing.Process(target=bot_with_cyclic_update_process, args=(update_event, answer_scores))
    p_selfbot = multiprocessing.Process(target=selfbot_process, args=(update_event, answer_scores))

    p_bot.start()
    p_selfbot.start()

    p_bot.join()
    p_selfbot.join()




 
 
