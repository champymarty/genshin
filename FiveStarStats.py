import asyncio
from numpy import true_divide
from GenshinMember import GenshinMember
from constant import guildIds
import discord
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)
from discord.ext import commands, pages

from data import Data
from Util import doesMemberExist


class FiveStarsStats(commands.Cog):
    
    BANNER = ["Character banner", "Weapon Banner", "Permanent Banner", "Character + Permanent banner"]
    MAX_ITEM_FOR_EACH_PAGE = 10
    
    def __init__(self, bot: discord.Bot, data: Data):
        self.bot = bot
        self.data = data        



    def _generateHistory(self, list, fiveStarsList):
        if list is None:
            return
        else:
            goldPity = 0
            first5Star = False
            for wish in reversed(list):
                goldPity += 1
                if wish.rarity == 5:
                    fiveStarsList.append({
                        "name": wish.name,
                        "date": wish.time.strftime("%m/%d/%Y, %H:%M:%S"),
                        "pity": goldPity - 1,
                        "accurate": first5Star
                    })
                    goldPity = 0
                    first5Star= True
        
    def generateHistory(self, wishListMain, wishList2 = None):
        fiveStarsList = []
        self._generateHistory(wishListMain, fiveStarsList)
        self._generateHistory(wishList2, fiveStarsList)
        return fiveStarsList
    
    async def get_banners(ctx: discord.AutocompleteContext):
        return FiveStarsStats.BANNER
    
    def generatePages(self, fiveStarsList):
        pageList = []
        realCount = 1
        count = 0
        embedText = ""
        for fiveStarItem in fiveStarsList:
            if count < FiveStarsStats.MAX_ITEM_FOR_EACH_PAGE:
                embedText += "{}) {} in {} wish on {}".format(realCount, 
                                                fiveStarItem["name"], 
                                                fiveStarItem["pity"],
                                                fiveStarItem["date"])
                if fiveStarItem["accurate"]:
                    embedText += "\n"
                else:
                    embedText += "(Can be wrong, reached end of wish data)\n"
            if count >= FiveStarsStats.MAX_ITEM_FOR_EACH_PAGE or realCount == len(fiveStarsList):
                embed = discord.Embed(description=embedText)
                embed.set_footer(text="The bot can only get the wish made available by miHoYo")
                pageList.append(pages.Page(
                    embeds=[
                        embed
                    ],
                ))
                count = 0
                embedText = ""
            count += 1
            realCount += 1
        return pageList
        

    @slash_command(guild_ids=guildIds, description="Show your 5 and 4 stars pity for each banner")
    async def show_5_stars_stats(self, ctx: discord.ApplicationContext, 
                                 banner: discord.Option(str, "Pick a banner !", autocomplete=get_banners)):
        await ctx.defer()
        if not await doesMemberExist(ctx):
            return
        genshinMember: GenshinMember = self.data.getMember(ctx.author.id)
        if banner == FiveStarsStats.BANNER[0]:
            history = self.generateHistory(genshinMember.character_banner)
        elif banner == FiveStarsStats.BANNER[1]:
            history = self.generateHistory(genshinMember.weapon_banner)
        elif banner == FiveStarsStats.BANNER[2]:
            history = self.generateHistory(genshinMember.permanent_banner)
        elif banner == FiveStarsStats.BANNER[3]:
            history = self.generateHistory(genshinMember.character_banner, wishList2=genshinMember.permanent_banner)
        else:
            embed = discord.Embed(title="The banner option does not exits", description="Please enter a valid banner type: \n" + "\n".join(FiveStarsStats.BANNER))
            await ctx.respond(embed=embed)
            return
        history.sort(key=lambda x: x["pity"], reverse=False)
        if len(history) == 0:
            embed = discord.Embed(title="You dont have any 5 stars in that banner!", description="Lets pray for a 5 stars soon ! " + "\n")
            await ctx.respond(embed=embed)
            return
        paginator = pages.Paginator(pages=self.generatePages(history))
        await paginator.respond(ctx.interaction, ephemeral=False)
        await asyncio.sleep(60 * 5)
        await paginator.cancel()