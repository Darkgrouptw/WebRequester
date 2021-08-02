from requests import cookies
from FormDataManager import Manager as FDM
from VPNManager.Manager import VPNManager as VPN
from datetime import datetime, timedelta
from ScreenShotManager import Manager as SSM
import sys
import os
import re
import schedule
import time

# 時間間隔多久，打卡一次
TimeOffsetMins = 2
TimeIntervalMins = 30
TimeFormat = "%Y-%m-%d %H:%M:%S"

# 運作的變數
Cookies = cookies
IsFinishToday = False

# 系統相關設定
UsingVPN = True
Version = "0.1-beta2"

# 截圖參數
ScreenShotLocation = "./ScreenShots/"
ScreenShotFormat = "%Y%m%d_%H%M%S"


if len(sys.argv) <= 2:
    print("要給兩個參數，帳號 & 密碼")
    os.system("PAUSE")
    sys.exit()

#region Helper Function
def __PrintSplitLine():
    Result = ""
    for i in range(0, 10):
        Result += "-"
    print(Result)

# 登入頁面
def LoginProcess():
    global Cookies
    LoginM = FDM.Manager("http://tpehr.wkec.com/ehrportal/LoginFOrginal.asp")
    LoginM.AddParams("op", "act")
    LoginM.AddParams("lmethod", 3)
    LoginM.AddParams("companyno", 47088673)
    LoginM.AddParams("companyid", 1)
    LoginM.AddParams("username", sys.argv[1])
    LoginM.AddParams("password", sys.argv[2])
    Response = LoginM.Post()
    Cookies = Response.cookies

# 上班打卡
def PunchInProcess():
    # 連線
    if UsingVPN:
        VPN.Connect()
        __PrintSplitLine()

    # 重新要一次 Cookie
    LoginProcess()

    CardDataM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_Default.asp", Cookies)
    CardDataM.AddParams("OP", "Insert")
    CardDataM.AddParams("hidCARD_TYPE", "0")
    Response = CardDataM.Post(Cookies)
    PunchInTime = datetime.now()
    if Response.status_code == 200 and __ScreenShot(Response, PunchInTime, 0):
        print(PunchInTime.strftime(TimeFormat) + " 上班打卡成功 !!")
    else:
        print("上班打卡失敗 !!")
    
    # 斷開
    if UsingVPN:
        VPN.Discount()
        __PrintSplitLine()

# 下班卡
def PunchOutProcess():
    # 連線
    if UsingVPN:
        VPN.Connect()
        __PrintSplitLine()
    
    # 重新要一次 Cookie
    LoginProcess()

    CardID = __GetCardID(1)
    CardDataM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_Default.asp", Cookies)
    CardDataM.AddParams("hidCARD_TYPE", "1")
    if CardID != -1:
        CardDataM.AddParams("OP", "Update")
        CardDataM.AddParams("hidCARD_DATA_ID", CardID)
        CardDataM.AddParams("hidCARD_DATA_ID_Q", CardID)
    else:
        CardDataM.AddParams("OP", "Insert")
    Response = CardDataM.Post(Cookies)

    PunchOutTime = datetime.now()
    if Response.status_code == 200 and __ScreenShot(Response, PunchOutTime, 1):
        print(PunchOutTime.strftime(TimeFormat) + " 下班打卡成功 !!")
    else:
        print("下班打卡失敗 !!")

    # 斷開
    if UsingVPN:
        VPN.Discount()
        __PrintSplitLine()
        
# 最後一次的下班卡
def PunchOutProcess_Final():
    global IsFinishToday
    PunchOutProcess()
    IsFinishToday = True

# 拿卡片 ID
def __GetCardID(Type):
    CardData_CheckM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_Check.asp?strCARD_TYPE=1", Cookies=Cookies)
    ScriptLang = CardData_CheckM.Soup.find_all("script")
    if (len(ScriptLang) != 4):
        return -1

    p = re.compile("\d+")
    return int(p.findall(str(ScriptLang[2]))[0])

# 截圖
def __ScreenShot(Response, CurrentDate, Type):
    ScreenShotHTML = SSM.Manager.Transfor(Response)
    if ScreenShotHTML is not None:
        # 創建資料夾
        if not os.path.isdir(ScreenShotLocation):
            os.mkdir(ScreenShotLocation)

        File = open(ScreenShotLocation + CurrentDate.strftime(ScreenShotFormat) + "_" + str(Type) + ".html", "w", encoding="UTF-8")
        File.write(ScreenShotHTML)
        File.close()
        return True
    else:
        return False
#endregion


# 版本資訊
__PrintSplitLine()
__PrintSplitLine()
print("Duke 打卡工具小幫手 V" + Version + "")
__PrintSplitLine()
__PrintSplitLine()

# 抓取打卡的資訊
# 登入
#region
if UsingVPN:
    VPN.Connect()
    __PrintSplitLine()
LoginProcess()
print(Cookies.get_dict())

# 今天日期
__PrintSplitLine()
Today = datetime.now()
TodayString = Today.strftime("%Y-%m-%d")
print("日期:", TodayString)
#endregion

# 接者進打卡頁面
# 0. 拿取目前的打卡列表
# 1. 先判斷是否是 假日 or 過中午十二點以後
# 2. 如果沒有打上班卡，立即幫忙打上班卡
# 3. 如果打了上班卡，接下來每隔 30 分鐘會幫忙打卡一次 (延遲五分鐘 的每隔30分)，並且截圖
# 4. 一直循環直到打完卡 Progress
# 5. pause
DoesWorkStart = False
WorkStartTime = datetime.now()
DoesWorkEnd = False
WorkEndTime = datetime.now()

# 0.
#region
PersonalM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_DataList.asp", Cookies)
TableData = PersonalM.Soup.find_all("nobr")
__PrintSplitLine()
print("上班時間列表：")
print("刷卡時間 上下班別")
for i in range(3, len(TableData), 2):
    print(TableData[i].text + " " + TableData[i + 1].text)
    if TableData[i].text.find(TodayString) != -1 and TableData[i + 1].text == "上班":
        DoesWorkStart = True
        WorkStartTime = datetime.strptime(TableData[i].text, TimeFormat)
    elif TableData[i].text.find(TodayString) != -1 and TableData[i + 1].text == "下班":
        DoesWorkEnd = True
        WorkEndTime =  datetime.strptime(TableData[i].text, TimeFormat)
__PrintSplitLine()
if UsingVPN:
    VPN.Discount()
    __PrintSplitLine()
#endregion

# 1. 
#region
# a. 是否 為假日
# b. 是否 中午十二點之後 
NeedCheckBoolean = False

# a.
if Today.weekday() >= 5:
    NeedCheckBoolean = True
    print ("今天為假日")
# b.
if Today.hour >= 12 and not DoesWorkStart:
    NeedCheckBoolean = True
    print ("目前時間為中午過後")

if NeedCheckBoolean:
    choose = input("請確定是否要執行打卡程式 (是請打'Y'):")
    if choose.lower() != "y":
        print("Bye Bye 祝你有美好的一天 ~~")
        os.system("PAUSE")
        sys.exit()
#endregion

# 2.
#region
ScheduleTimeList = []
if not DoesWorkStart:
    PunchInProcess()
    __PrintSplitLine()

print("本日上班打卡時間：")
print(WorkStartTime)
TempTime = WorkStartTime + timedelta(minutes=TimeOffsetMins)
FinalWorkTime = TempTime + timedelta(hours=9.25)
__PrintSplitLine()
#endregion

# 3.
# 先把所有上班的打卡時間加入
#region
for i in range (int(9.25 * 60 / TimeIntervalMins)):
    TempTime += timedelta(minutes=TimeIntervalMins)
    ScheduleTimeList.append(TempTime)
ScheduleTimeList.append(FinalWorkTime)
for i in range(len(ScheduleTimeList) - 1, -1, -1):
    if ScheduleTimeList[i] < Today:
        ScheduleTimeList.pop(i)

# 顯示接下來要打卡的時間
# 這裡有幾種情況
# 1. 有 Schdule 的時間 (代表表有排行程)
# 2. 沒打下班卡，等下班後才打開這個 程式
# 3. 有打下班卡，但總時間差，小於 9 個小時又 15 分 + TimeOffsetMins
# 4. 不用在打卡了
print("接下來打卡時間")
if len(ScheduleTimeList) > 0:
    # 1.
    for i in range(len(ScheduleTimeList)):
        AtTime = ScheduleTimeList[i].strftime("%H:%M:%S")
        print("# 在 " + AtTime + " 會自動打下班卡")

        if i != len(ScheduleTimeList) - 1:
            schedule.every().day.at(AtTime).do(PunchOutProcess)
        else:
            schedule.every().day.at(AtTime).do(PunchOutProcess_Final)
elif not DoesWorkEnd or (DoesWorkEnd and WorkEndTime - WorkStartTime < timedelta(hours=9.25) + timedelta(minutes=TimeOffsetMins)):
    # 2. && 3.
    IsFinishToday = True
    print("現在打下班卡")
    PunchOutProcess()
else:
    # 4.
    print("本日不用打卡了")
    IsFinishToday = True
__PrintSplitLine()
#endregion

# 4.
#region
while not IsFinishToday:
    schedule.run_pending()
    time.sleep(1)
#endregion

# 5.
print("下班囉!!")
os.system("PAUSE")