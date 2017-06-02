import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
import sys
import datetime
import asyncio
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open

class PatchParser(telepot.aio.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(PatchParser, self).__init__(*args, **kwargs)
        self._lastpatch = datetime.date(2017, 4, 10) #Add database for the last patch
        self._notesurl = []

    async def hots(self):
        #Getting the information from the site
        url = "http://us.battle.net/heroes/en/blog/"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        print("Getting the information from the " + url)

        patchlist = []
        for link in soup.find_all('a'):
            href = link.get('href')
            if href != None:
                if "ptr" in href and not "#" in href or "patch" in href and not "#" in href:
                    patchlist.append(href)
        for i in range(len(patchlist)):
            dates = patchlist[i].split("-")
            date = dates[-3:]
            latestpost = datetime.date(int(date[2]), int(date[0]), int(date[1]))
            if latestpost > self._lastpatch:
                self._lastpatch = latestpost
                notesUrl = "http://us.battle.net"+patchlist[i]
                await self.sender.sendMessage(notesUrl)
                self._notesurl.append(notesUrl)
                await self.sender.sendMessage("To access these patch notes type /note"+str(self._notesurl.index(notesUrl)))
    

    async def post_patch_notes(self, index):
        if len(self._notesurl) == 0:
            print("No notes stored")
        elif 0 <= index < len(self._notesurl):
            notesUrl = self._notesurl[index]
            parsed = await self.parse_notes(notesUrl)
            msglist = await self.formatmsg(parsed)
            for k in range(len(msglist)):
                await self.sender.sendMessage(msglist[k])
                print("NEW MESSAGE SENT \nLenght: " + str(len(msglist[k]))) 
        else:
            print("There are no notes for this index")

    async def on_chat_message(self, msg):
        command = msg["text"]
        if command == "/hots":
            await self.hots()
        elif "/note" in command:
            index = command.replace("/note", "").strip()
            if index.isdigit():
                await self.post_patch_notes(int(index))                


    async def parse_notes(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        response = requests.get(url, headers=headers)
        only_class_article = SoupStrainer(class_="article__wrapper--left")
        soup = BeautifulSoup(response.text, "lxml", parse_only=only_class_article).text
        print("Getting the information from the " + url)
        patchlist = soup.split("img")
        patchlist.pop()
        parsed = str(patchlist[0]).replace("Return to Top", "").replace("\n\n\n\n", "\n").replace("\n\n\n\n", "\n").rstrip()
        return parsed

    async def formatmsg(self, msg):
        splitlist = msg.split("\n\n")
        msglist = [""]
        j = 0
        for k in range(len(splitlist)):
            if len(msglist[j])+len(splitlist[k]) <= 3500:
                msglist[j] = str(msglist[j] + "\n\n" + splitlist[k])
                
            else:
                msglist.append(splitlist[k])
                j = msglist.index(splitlist[k])
        return msglist


with open ("token.txt", "r") as tokenfile:
    token = tokenfile.read().rstrip()

bot = telepot.aio.DelegatorBot(token, [
    pave_event_space()(
        per_chat_id(), create_open, PatchParser, timeout=600),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()