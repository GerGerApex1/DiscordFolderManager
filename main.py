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
        # after: [0, 2, 1, 3, 4, 5, 6, 7, 8]
        # before [1, 0, 2, 3, 4, 5, 6, 7, 8]
        # server_list: {0: WebElement}
        updatedOrder = currentOrder.copy()
        print(old, after)
        for i in range(len(after)):
            if old[i] != after[i]:
                print(old[i], after[i])
                newItem1 = currentOrder[after[i]]
                oldItem1 = currentOrder[old[i]]
                # old to new updatedOrder 
                print(oldItem1, newItem1)
                updatedOrder[old[i]] = newItem1
                # new to old 
                updatedOrder[after[i]] = oldItem1
        print(f"""
                        CURRENT ORDER
        {currentOrder}
                        NEW ORDER
        {updatedOrder} 
        """)
        discord_guild_info.rearrangeServers(loginwindow.discordTokenLineEdit.text(), list(updatedOrder.values()))
    def login_event():
        folders = discord_guild_info.getDiscordGuildFolders(loginwindow.discordTokenLineEdit.text())
        if "message" in folders:
            print('Something gone wrong. ' +  folders['message'])
        else:
            main_window = loginwindow.mainWindow
            t = common.CustomThread(target=download_folder, args=(
            loginwindow.discordTokenLineEdit.text(), folders))
            main_window.setConfirmButtonEvent(rearrangeServer)
            t.start()
            list = t.join()
            print(list)
            nonlocal currentOrder
            currentOrder = getOrderList(folders, loginwindow.discordTokenLineEdit.text())
            addImageToGui(main_window, list)    # type: ignore
            main_window.show()
    loginwindow.login_button.clicked.connect(login_event)
    if credentials_manager.is_available():
        loginwindow.saved_token(credentials_manager.get_token())
    loginwindow.show()
    app.exec_() 
def getOrderList(folders, authToken):
    data = {}
    data1 = discord_guild_info.getGuildFolders(folders, authToken)
    for i in data1:
        print(str(i['index']))
        data[i['index']] = folders["guild_folders"][i['index']]
    print(data)
    return data
def addImageToGui(window: qt_window.ClassWindow, serverList: list):
    for x in serverList:
        print('added image')
        print(x['filename'])
        print(x)
        window.addServer(x["filename"], x["serverName"], x["index"])



def download_folder(auth,userGuildFolderSettings ):
    folder_path = tempfile.mkdtemp(prefix="DiscordServerManager-")
    print(auth)
    folderData = discord_guild_info.getGuildFolders(userGuildFolderSettings, auth)
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
        print(f"test: {imageFile}")
        fileList.append(
            {"filename": f"{folder_path}\\{imageFile}", "serverName": serverName, 'index': index})
    
    return fileList


def exit_event(path):
    print("Detected Program Exit.")
    shutil.rmtree(path)


def downloadIconImage(url, folder_path):
    resp = discord_guild_info.downloadImage(url)
    fileName = url.split('/')[-2]
    print(resp.url, folder_path)
    if resp.status_code == 200:
        print('sucess')
        with open(os.path.join(folder_path, f"{fileName}.jpeg"), "wb") as f:
            shutil.copyfileobj(resp.raw, f)


if __name__ == "__main__":
    main()
