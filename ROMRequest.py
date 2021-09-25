from sys import set_asyncgen_hooks
import requests
from bs4 import BeautifulSoup
from requests.api import post
from tqdm import tqdm
import os
import time

MainPage = "https://www.planetemu.net/roms/apple-ii-games"
DownloadPage = "https://www.planetemu.net/php/roms/download.php"
resp = requests.get(MainPage)
resp.encoding = "utf-8"


# 抓取全部的首頁
print("Fetch Main Page Title")
soup = BeautifulSoup(resp.text, "html.parser")
TitleLink = soup.find_all("td", class_="menuroms letters")[0].find_all("a")
for i in tqdm(range(len(TitleLink))):
    TitleLink[i] = TitleLink[i].get("href").split("?")[1]
TitleLink = TitleLink[7:]
# print(TitleLink)

# 抓所有的 List
print("Fetch All Catalog Download")
DownloadLinks = []
for i in tqdm(range(len(TitleLink))):
    singleResp = requests.get(MainPage + "?" + TitleLink[i])
    singleResp.encoding = "utf-8"
    
    singleSoup = BeautifulSoup(singleResp.text, "html.parser")
    Items = singleSoup.find_all("tr", class_=["rompair", "romimpair"])

    # 更新
    for j in range(len(Items)):
        DownloadLinks.append({
            "Catalog": TitleLink[i].split("=")[-1],
            "Item": Items[j].select("a")[0].get("href").split("/")[-1]
        })

# 抓取所有的 IDList
IDList = []
print("Fetch All ID")
for i in tqdm(range(len(DownloadLinks))):
    MainPage = MainPage.replace("roms", "rom")
    resp = requests.get(MainPage + "/" + DownloadLinks[i]["Item"])
    resp.encoding = "utf-8"

    soup = BeautifulSoup(resp.text, "html.parser")
    ID = soup.find("input", attrs={"type": "hidden", "name": "id"}).get("value")

    # 抓取 ID
    IDList.append({
        "Catalog": DownloadLinks[i]["Catalog"],
        "ID": ID,
    })

# 開始抓所有的檔案
print("Downloading Files")
if not os.path.exists("./Roms"):
    os.mkdir("./Roms")
for i in tqdm(range(len(IDList))):
    SaveDirectory = os.path.join("./Roms", str(IDList[i]["Catalog"]))
    if not os.path.exists(SaveDirectory):
        os.mkdir(SaveDirectory)

    # 寫檔案
    while True:
        FileRequest = requests.post(DownloadPage, {"id": IDList[i]["ID"]}, stream=True)
        print(FileRequest.url)
        print(FileRequest.headers)
        print(IDList[i]["ID"])

        if len(FileRequest.url) > len("https://www.planetemu.net/php/roms/download.php") and "content-disposition" in FileRequest.headers:
            FileName = FileRequest.headers["content-disposition"].replace("attachment; filename=\"", "")[:-1]
            FileRequest.raise_for_status()
            File = open(os.path.join(SaveDirectory, FileName), "wb")
            for chunk in FileRequest.iter_content(chunk_size=8192):
                File.write(chunk)
            File.close()
            break
        else:
            time.sleep(1)