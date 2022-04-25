import os

import discord


async def doesMemberExist(ctx) -> bool:
    filePathMember = os.path.join(os.path.dirname(os.path.realpath(__file__)), "members", "{}.pickle".format(ctx.author.id))
    if not os.path.isfile(filePathMember):
        embed = discord.Embed(title="Oups ! You dont have any data store on the server", description="Please run the command /update_wish_history url")
        embed.set_image(url="https://c.tenor.com/lceyY93l6_YAAAAC/mihoyo-genshin.gif")
        await ctx.respond(embed=embed)
        return False
    return True