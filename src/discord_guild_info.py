import json
import requests
def getDiscordList(authToken):
    headers = {
        "Authorization": f"{authToken}"
    }
        # Make the request to the Discord API
    response = requests.get("https://discordapp.com/api/users/@me/guilds", headers=headers)
    # Print the status code of the response
    return response.json()
def getIconURL(guildId, icon, size = 200):

    return f"https://cdn.discordapp.com/icons/{guildId}/{icon}.jpeg?size={size}"
def _getGuildData(guildId, authToken):
    headers = { "Authorization": f"{authToken}" }
    guildData = requests.get(f"https://discord.com/api/v9/guilds/{guildId}", headers=headers)
    print(guildData.url)
    return guildData.json()
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
def getGuildFolders(dict1, authToken):
    serverFolderx = []
    for index, item in enumerate(dict1['guild_folders']):
        guildId = item['guild_ids'][0]
        print(guildId)
        guildData = _getGuildData(guildId, authToken)
        iconURL = getIconURL(guildId, guildData['icon'], 40)
        serverFolderx.append({
            "id": guildId,
            "name": guildData['name'],
            "iconURL": iconURL,
            "index": index
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

