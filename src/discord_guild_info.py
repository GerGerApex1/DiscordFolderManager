import json
import requests
import aiohttp
import asyncio
def getDiscordList(authToken):
    headers = {
        "Authorization": f"{authToken}"
    }
        # Make the request to the Discord API
    response = requests.get("https://discordapp.com/api/users/@me/guilds", headers=headers)
    # Print the status code of the response
    return response.json()
def getIconURL(guildId, icon, size = 200):
    if icon is None:
        return f"https://cdn.discordapp.com/icons/1070401234453942292/b69b54acdb19b6e418cebad354d7e17f.jpeg?size={size}"
    else:  
        return f"https://cdn.discordapp.com/icons/{guildId}/{icon}.jpeg?size={size}"
async def _getGuildData(guildId, authToken, clientSession: aiohttp.ClientSession):
    headers = { "Authorization": f"{authToken}" }
    async with clientSession.get(f"https://discord.com/api/v9/guilds/{guildId}", headers=headers) as guildData:
        print(f"Get request to {guildData.url} is success.")
        return await guildData.json()
def downloadImage(url):
    response = requests.get(url, stream=True)
    return response
def getDiscordGuildFolders(authToken): 
    headers = {
        "Authorization": f"{authToken}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://discordapp.com/api/users/@me/settings", headers=headers)
    return response.json()
async def getGuildFolders(dict1, authToken):
    serverFolderx = []
    print(dict1['guild_folders'])
    async with aiohttp.ClientSession() as session:
        tasks = [_getGuildData(guildId['guild_ids'][0], authToken, session) for guildId in dict1['guild_folders']]
        dataResponse = await asyncio.gather(*tasks)
        for index, item in enumerate(dataResponse):
            guildId = dict1['guild_folders'][index]['guild_ids'][0]
            iconURL = getIconURL(guildId, item['icon'], 40)
            serverFolderx.append({
                "id": guildId,
                "name": item['name'],
                "iconURL": iconURL,
                "index": index,
                "serverInfo": dict1['guild_folders'][index]
            })
    return serverFolderx
def rearrangeServers(authToken, newUpdate):
    headers = {
        "Authorization": f"{authToken}",
        "Content-Type": "application/json"
    }
    data = {
        "guild_folders": newUpdate
    }
    response =  requests.patch("https://discordapp.com/api/users/@me/settings", headers=headers, json=data)
    return response.status_code