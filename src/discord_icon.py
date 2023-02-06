from typing import Any, Callable, Iterable, Mapping
from PyQt5 import QtWidgets, QtGui
import qt_window
import common_func
import sys
import tempfile
import os
import shutil
import atexit
import src.discord_guild_info
from functools import partial
import multiprocessing
def getAllIcons(auth):
    folder_path = tempfile.mkdtemp(prefix="DiscordServerManager-")
    serverRawList = src.discord_guild_info.getDiscordList(auth)
    serverList = []
    fileList = []
    for x in serverRawList:
        icon = x['icon']
        id = x['id']
        serverList.append(src.discord_guild_info.getIconURL(id, icon, 80))
    threadpool = multiprocessing.Pool(os.cpu_count())
    partialFunc = partial(downloadIconImage, folder_path = folder_path)
    atexit.register(exit_event, folder_path)
    threadpool.map(partialFunc, serverList)
    threadpool.close()
    threadpool.join()
    for x in serverRawList:
        imageFile = x["id"]
        serveName = x['name']
        fileList.append({"filename": f"{folder_path}\\{imageFile}", "serverName": serveName})
    return fileList
def exit_event(path):
    print("Detected Program Exit.")
    shutil.rmtree(path)
def downloadIconImage(url, folder_path):
    resp = src.discord_guild_info.downloadImage(url)
    parts = url.split('/')
    # get the second-to-last element    
    fileName = parts[-2]
    print(resp.url, folder_path) 
    if resp.status_code == 200:
        print('sucess')
        with open(os.path.join(folder_path, f"{fileName}.jpeg"), "wb") as f:
            shutil.copyfileobj(resp.raw, f) 