import os
import pickle
import genshin
from dotenv import load_dotenv
import xlsxwriter
from enum import Enum

class Banner(Enum):
    CHARACTER = 1
    PERMANENT = 2
    WEAPON = 3
    NOVICE = 4

class GenshinMember:
    def __init__(self, id):
        self.id = id
        self.permanent_banner = []
        self.novice_banner = []
        self.character_banner = []
        self.weapon_banner = []
        self.url = None
        self.hide_history = True
        self.ltuid = None
        self.ltoken = None

    
    async def updateWishList(self, url):
        load_dotenv()
        change = False
        if url is not None:
            self.url = url
            change = True
        try:
            cookies = {"ltuid": os.getenv("ltuid"), "ltoken": os.getenv("ltoken")}
            authkey = genshin.extract_authkey(self.url)

            client = genshin.GenshinClient(cookies)
            client.authkey = authkey
            
            result1 = await self._updateBanner(self.novice_banner, 100, client)
            result2 = await self._updateBanner(self.permanent_banner, 200, client)
            result3 = await self._updateBanner(self.character_banner, 301, client)
            result4 = await self._updateBanner(self.weapon_banner, 302, client)
        except Exception as e:
            raise e
        finally:
            await client.close()
        newWish = result1 or result2 or result3 or result4
        if change or newWish:
            self.saveData()
        return newWish
        
    async def _updateBanner(self, banner_list, banner_number, client):
        before_size = len(banner_list)
        async for wish in client.wish_history(banner_number):
            if before_size == 0:
                banner_list.append(wish)
            elif wish.time > banner_list[0].time:
                banner_list.append(wish)
            else:
                break
        if before_size != len(banner_list):
            banner_list.sort(key=lambda x: x.time, reverse=True)
            return True
        else:
            return False
        
    def _writeSheet(self, banner_list, banner_name, workbook, goldFormat, purpleFormat, pities):
        worksheet = workbook.add_worksheet(banner_name)
        worksheet.write(0, 0, "wish date")
        worksheet.write(0, 1,"name")
        worksheet.write(0, 2, "rarity")
        worksheet.write(0, 3, "type")
        
        worksheet.write(3, 5, "5 star pity")
        worksheet.write(4, 5, "4 star pity")
        worksheet.write(3, 6, pities[1])
        worksheet.write(4, 6, pities[0])
        i = 1
        for wish in banner_list:
            format = None
            if wish.rarity == 5:
                format = goldFormat
            elif wish.rarity == 4:
                format = purpleFormat
            worksheet.write(i, 0, wish.time.strftime("%m/%d/%Y, %H:%M:%S"), format)
            worksheet.write(i, 1, wish.name, format)
            worksheet.write(i, 2, wish.rarity, format)
            worksheet.write(i, 3, wish.type, format)
            i += 1
        
    def generateExcel(self):
        file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "excel", "{}.xlsx".format(self.id))
        workbook = xlsxwriter.Workbook(file)
        goldFormat = workbook.add_format({'bold': True})
        goldFormat.set_bg_color('#ffd700')
        
        purpleFormat = workbook.add_format({'bold': True})
        purpleFormat.set_bg_color('#b8a7ea')
        
        self._writeSheet(self.character_banner, "character_banner", workbook, goldFormat, purpleFormat, self.getPities(Banner.CHARACTER))
        self._writeSheet(self.weapon_banner, "weapon_banner", workbook, goldFormat, purpleFormat, self.getPities(Banner.WEAPON))
        self._writeSheet(self.permanent_banner, "permanent_banner", workbook, goldFormat, purpleFormat, self.getPities(Banner.PERMANENT))
        self._writeSheet(self.novice_banner, "novice_banner", workbook, goldFormat, purpleFormat, self.getPities(Banner.NOVICE))
        workbook.close()
        
    def saveData(self) -> None:
        file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "members", "{}.pickle".format(self.id))
        with open(file,'wb') as f:
            pickle.dump(self, f)
            
    def _getPities(self, wishList):
        goldPity = 0
        purplePity = 0
        purplePityCalculated = False
        goldPityCalculated = False
        for wish in wishList:
            if wish.rarity == 5:
                goldPityCalculated = True
            elif wish.rarity == 4:
                purplePityCalculated = True
            if not goldPityCalculated:
                goldPity += 1
            if not purplePityCalculated:
                purplePity += 1
            if goldPityCalculated and purplePityCalculated:
                break
        return [purplePity, goldPity]
            
    def getPities(self, banner : Banner):
        if banner == Banner.CHARACTER:
            return self._getPities(self.character_banner)
        elif banner == Banner.WEAPON:
            return self._getPities(self.weapon_banner)
        elif banner == Banner.PERMANENT:
            return self._getPities(self.permanent_banner)
        elif banner == Banner.NOVICE:
            return self._getPities(self.novice_banner)
        
        
