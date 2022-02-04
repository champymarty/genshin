from pydoc import describe
from GenshinMember import GenshinMember, Banner
import discord
import os
from dotenv import load_dotenv
from MarkdownDiscord import Effect, Message
from data import Data


# load .env variables
load_dotenv()

bot = discord.Bot()
data = Data()

guildIds = [833210288681517126] # test discord server
guildIds = None # force global commandsa

@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))
    
@bot.slash_command(guild_ids=guildIds, description="Update your wishes. Note: take 1h for your wish to register inside Mihoyo")
async def update_wish_history(ctx, url = None):
    await ctx.defer()
    member: GenshinMember = data.getMember(ctx.author.id)
    if member.url is None and url is None:
        embed = discord.Embed(title="You never provided a url !", description="Run the command /update_wish_history url (make sure you select the url attribut it should look like that: )")
        filePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pics", "help_no_url_ever_provided.png")
        file = discord.File(filePath, filename="help_no_url_ever_provided.png")
        embed. set_image(url="attachment://help_no_url_ever_provided.png")
        await ctx.respond(file=file, embed=embed)
        return
    try:
        if await member.updateWishList(url):
            embed = discord.Embed(title="Your genshin history was updated with new wishes !", description="May wish gods be in you favor")
            embed.set_image(url="https://c.tenor.com/-tkf9gymfiMAAAAd/barbara-genshin.gif")
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="No new wish could be found", description="New wishes can take up to 1 hour to register in Mihoyo server")
            embed.set_image(url="https://c.tenor.com/NXczgNVYW4sAAAAd/genshin-impact-eyes.gif")
            await ctx.respond(embed=embed)
    except Exception as e:
        if url is None:
            embed = discord.Embed(title="The url store in the server as expire", description="Please provide a valid url with the optionnal argument 'url' in this command ( Note: Each url expire after 24h )")
            embed.set_image(url="https://c.tenor.com/1wwB5yNC6dgAAAAd/genshin-impact.gif")
        else:
            embed = discord.Embed(title="The url you input is invalid", description="Please provide a valid url with the optionnal argument 'url' in this command ( Note: Each url expire after 24h )")
            embed.set_image(url="https://c.tenor.com/AlfMXCwnJscAAAAd/paimon-genshin-impact.gif")
        await ctx.respond(embed=embed)
    
@bot.slash_command(guild_ids=guildIds, description="Show your 5 and 4 stars pity for each banner")
async def show_pity(ctx):
    await ctx.defer()
    if not await doesMemberExist(ctx):
        return
    member: GenshinMember = data.getMember(ctx.author.id)
    embed = discord.Embed()
    embed.set_image(url="https://c.tenor.com/9nGsZuIiTnoAAAAC/barbara-barbaragenshin.gif")
    
    pities = member.getPities(Banner.CHARACTER)
    embed.add_field(name="Character Banner", value=getBannerPityString(pities[0], pities[1], 90, 75), inline=True)
    
    pities = member.getPities(Banner.WEAPON)
    embed.add_field(name="Weapon Banner", value=getBannerPityString(pities[0], pities[1], 80, 65), inline=True)
    
    pities = member.getPities(Banner.PERMANENT)
    embed.add_field(name="Permanent Banner", value=getBannerPityString(pities[0], pities[1], 90, 75), inline=False)
    
    await ctx.respond(embed=embed)
    
def getBannerPityString(fourStarPity, fiveStarPity, maxPity, softPity):
    messageContent = Message()
    messageContent.nextLine()
    messageContent.addLine("5 star pity: {}/{}".format(fiveStarPity, maxPity))
    messageContent.addLine("{} wish until soft pity".format(softPity - fiveStarPity), Effect.ITALIC)
    messageContent.addLine("{} wish until hard pity".format(maxPity - fiveStarPity), Effect.ITALIC)
    messageContent.nextLine()
    messageContent.addLine("4 star pity: {}/10".format(fourStarPity))
    return messageContent.getString()

@bot.slash_command(guild_ids=guildIds, description="Generate your complete wish history and send it in DM")
async def generate_wish_excel(ctx):
    await ctx.defer()
    if not await doesMemberExist(ctx):
        return
    member: GenshinMember = data.getMember(ctx.author.id)
    member.generateExcel()    
    filePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "excel", "{}.xlsx".format(member.id))
    await ctx.author.send("Here is your wish history ! If you did not run the command /update_wish_history, the excel will be generated with the last time you ran that command.", file=discord.File(filePath))
    embed = discord.Embed(title="Your genshin excel file was successfully generated", description="You should receive your excel file with your history in DM")
    embed.set_image(url="https://c.tenor.com/XaCdTAPtn1gAAAAC/yae-miko-yae-genshin.gif")
    await ctx.respond(embed=embed) 
    
    if os.path.exists(filePath):
        os.remove(filePath)
        
@bot.slash_command(guild_ids=guildIds, description="Delete all your data from the server.")
async def delete_my_data(ctx):
    await ctx.defer()
    filePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "members", "{}.pickle".format(ctx.author.id))
    if os.path.exists(filePath):
        os.remove(filePath)
        embed = discord.Embed(title="All the data was remove from the server", description="Please run the command /update_wish_history url if you want to track again your wish")
        await ctx.respond(embed=embed)
        return
    embed = discord.Embed(title="You dont gave any data on the bot", description="Please run the command /update_wish_history url if you want to track again your wish")
    await ctx.respond(embed=embed)
    
@bot.slash_command(guild_ids=guildIds, description="Get help")
async def help(ctx):
    await ctx.defer()
    embed = discord.Embed(title="Help center")
    description = Message()
    description.addLine("Run the command /update_wish_history url(optional if you already did the command and the link is still valid)")
    description.addLine("The get help on how to get the url, visit the help document: https://docs.google.com/document/d/145cPidFRGWqL9Ljv245PXg0P_go4Pz4Qh6b9gwCIXdg/edit?usp=sharing")
    embed.add_field(name="Update your wish history", value=description.getString(), inline=False)
    
    description = Message()
    description.addLine("Run the command /show_pity ")
    embed.add_field(name="Get your 5 and 4 star pity for all banner", value=description.getString(), inline=False)
    
    description = Message()
    description.addLine("Run the command /generate_wish_excel ")
    embed.add_field(name="Generate your complete wish history in all banner sent in DM", value=description.getString(), inline=False)
    
    description = Message()
    description.addLine("Run the command /delete_my_data ")
    embed.add_field(name="Delete all your data from the bot", value=description.getString(), inline=False)
    
    embed.set_footer(text="If you have any questions, join the Discord help server ! https://discord.com/invite/hRTHpB4HUC")
    await ctx.respond(embed=embed)

async def doesMemberExist(ctx) -> bool:
    filePathMember = os.path.join(os.path.dirname(os.path.realpath(__file__)), "members", "{}.pickle".format(ctx.author.id))
    if not os.path.isfile(filePathMember):
        embed = discord.Embed(title="Oups ! You dont have any data store on the server", description="Please run the command /update_wish_history url")
        embed.set_image(url="https://c.tenor.com/lceyY93l6_YAAAAC/mihoyo-genshin.gif")
        await ctx.respond(embed=embed)
        return False
    return True

bot.run(os.getenv("TOKEN"))