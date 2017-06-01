import requests
from bs4 import BeautifulSoup
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
                await self.sender.sendMessage("http://us.battle.net"+patchlist[i])


    async def on_chat_message(self, msg):
        command = msg["text"]
        if command == "/hots":
            await self.sender.sendMessage("Message is sent to you when patch notes are released")
            await self.hots()



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