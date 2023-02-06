import sys 
sys.path.append('src/')
import common
import discord_guild_info
import credentials_manager
import multiprocessing

from functools import partial
import json

import atexit
import shutil
import os
import tempfile
import asyncio
import qt_window
from PyQt5 import QtWidgets, QtGui
from PyQt5 import QtWidgets

def main():
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('discord-font.tff')
    app.setStyleSheet("QLabel{font-size:13pt;}")
    loginwindow = qt_window.LoginWindow()
    currentOrder = {}
    def rearrangeServer(old, after):
        updatedOrder = [i['orig_data'] for i in after]
        discord_guild_info .rearrangeServers(loginwindow.getToken(), updatedOrder)
        folders = discord_guild_info.getDiscordGuildFolders(loginwindow.getToken())
        currentOrder.update(getOrderList(folders, loginwindow.getToken()))  
        #currentOrder.update(updatedOrder)
    def login_event():
        folders = discord_guild_info.getDiscordGuildFolders(loginwindow.getToken())
        if "message" in folders:
            print('Something gone wrong. ' +  folders['message'])
        else:
            main_window = loginwindow.mainWindow
            t = common.CustomThread(target=download_folder, args=(
            loginwindow.getToken(), folders))
            main_window.setConfirmButtonEvent(rearrangeServer)
            t.start()
            list = t.join()
            print(list)
            nonlocal currentOrder
            currentOrder = getOrderList(folders, loginwindow.getToken())
            addImageToGui(main_window, list)    # type: ignore
            main_window.show()
            loginwindow.close()
    loginwindow.login_button.clicked.connect(login_event)
    if credentials_manager.is_available():
        loginwindow.saved_token(credentials_manager.get_token())
    loginwindow.show()
    sys.exit(app.exec_()) 
def getOrderList(folders, authToken):
    data = {}
    data1 = asyncio.run(discord_guild_info.getGuildFolders(folders, authToken))
    for i in data1:
        data[str(i['index'])] = folders["guild_folders"][i['index']]
    return data
def addImageToGui(window: qt_window.ClassWindow, serverList: list):
    for x in serverList:
        widgetData = { "index": x['index'], "orig_data": x["serverInfo"]}
        print(f"Added Image Filepath: {x['filename']}")
        window.addServer(x["filename"], x["serverName"], widgetData=widgetData)



def download_folder(auth,userGuildFolderSettings ):
    folder_path = tempfile.mkdtemp(prefix="DiscordServerManager-")
    folderData = asyncio.run(discord_guild_info.getGuildFolders(userGuildFolderSettings, auth))
    serverList = [item['iconURL'] for item in folderData]
    fileList = []
    threadpool = multiprocessing.Pool(os.cpu_count())
    partialFunc = partial(downloadIconImage, folder_path=folder_path)
    atexit.register(exit_event, folder_path)
    threadpool.map(partialFunc, serverList)
    threadpool.close()
    threadpool.join()
    for x in folderData:
        imageFile = x['iconURL'].split('/')[-2]
        serverName = x['name']
        index = x['index']
        fileList.append(
            {"filename": f"{folder_path}\\{imageFile}", "serverName": serverName, 'index': index, "serverInfo": x['serverInfo']})
    return fileList


def exit_event(path):
    print("Detected Program Exit.")
    shutil.rmtree(path)


def downloadIconImage(url, folder_path):
    resp = discord_guild_info.downloadImage(url)
    fileName = url.split('/')[-2]
    if resp.status_code == 200:
        print(f'Download of image {resp.url} is success.')
        with open(os.path.join(folder_path, f"{fileName}.jpeg"), "wb") as f:
            shutil.copyfileobj(resp.raw, f)


if __name__ == "__main__":
    main()
