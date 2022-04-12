import datetime
from os import listdir
from os.path import join
import os
from discord.ext import commands, tasks
from discord.utils import get

class DataExpire(commands.Cog):
    def __init__(self):
        self.dataPath  = join(os.path.dirname(os.path.realpath(__file__)), "members")
        self.expirationTimedelta = datetime.timedelta(days=30)
        self.checkForExpireData.start()

    def cog_unload(self):
        self.checkForExpireData.cancel()


    @tasks.loop(seconds=60*60)
    async def checkForExpireData(self):
        filesDataPath = []
        for file in listdir(self.dataPath):
            realPath = join(self.dataPath, file)
            if os.path.isfile(realPath):
                filesDataPath.append(realPath)
                
        now = datetime.datetime.now()
        for fileDataPath in filesDataPath:
            createdTime = datetime.datetime.fromtimestamp(os.path.getctime(fileDataPath))
            if (now - createdTime) >= self.expirationTimedelta:
                os.remove(fileDataPath)
            
