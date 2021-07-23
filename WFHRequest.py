from requests import cookies
from FormDataManager import Manager as FDM
from VPNManager.Manager import VPNManager as VPN
from datetime import datetime, timedelta
from ScreenShotManager import Manager as SSM
import sys
import os
import re

# 時間間隔多久，打卡一次
TimeOffsetMins = 5
TimeIntervalMins = 30


if len(sys.argv) <= 2:
    print("要給兩個參數，帳號 & 密碼")
    os.system("PAUSE")
    exit()

#region Helper Function
def __PrintSplitLine():
    Result = ""
    for i in range(0, 10):
        Result += "-"
    print(Result)

# 上班打卡
def PunchInProcess(Cookies):
    CardDataM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_Default.asp", Cookies)
    CardDataM.AddParams("OP", "Update")
    CardDataM.AddParams("hidCARD_TYPE", "0")
    Response = CardDataM.Post(Cookies)
    PunchInTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    if Response.status_code == 200 and __ScreenShot(Response, PunchInTime + " _0"):
        print(PunchInTime + " 上班打卡成功 !!")
    else:
        print("上班打卡失敗 !!")

# 下班卡
def PunchOutProcess(Cookies):
    CardID = __GetCardID(Cookies, 1)
    CardDataM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_Default.asp", Cookies)
    CardDataM.AddParams("hidCARD_TYPE", "1")
    if CardID != -1:
        CardDataM.AddParams("OP", "Update")
        CardDataM.AddParams("hidCARD_DATA_ID", CardID)
        CardDataM.AddParams("hidCARD_DATA_ID_Q", CardID)
    else:
        CardDataM.AddParams("OP", "Insert")
    Response = CardDataM.Post(Cookies)

    PunchOutTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    if Response.status_code == 200 and __ScreenShot(Response, PunchOutTime + " _1"):
        print(PunchOutTime + " 下班打卡成功 !!")
    else:
        print("下班打卡失敗 !!")
    # pass

# 拿卡片 ID
def __GetCardID(Cookies, Type):
    CardData_CheckM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_Check.asp?strCARD_TYPE=1", Cookies=Cookies)
    ScriptLang = CardData_CheckM.Soup.find_all("script")
    if (len(ScriptLang) != 4):
        return -1

    p = re.compile("\d+")
    return int(p.findall(str(ScriptLang[2]))[0])

# 截圖
def __ScreenShot(Response, Location):
    print(SSM.Manager.Transfor(Response))
    return True
#endregion

# 抓取打卡的資訊
# 登入
#region
# VPN.Connect()
LoginM = FDM.Manager("http://tpehr.wkec.com/ehrportal/LoginFOrginal.asp")
LoginM.AddParams("op", "act")
LoginM.AddParams("lmethod", 3)
LoginM.AddParams("companyno", 47088673)
LoginM.AddParams("companyid", 1)
LoginM.AddParams("username", sys.argv[1])
LoginM.AddParams("password", sys.argv[2])
Response = LoginM.Post()
Cookies = Response.cookies
print(Cookies.get_dict())
# FDM.Manager.DebugFile(Response.text)

# 今天日期
__PrintSplitLine()
Today = datetime.now()
TodayString = Today.strftime("%Y-%m-%d")
print("日期:", TodayString)
#endregion

# 接者進打卡頁面
# 1. 拿取目前的打卡列表
# 2. 如果沒有打上班卡，立即幫忙打上班卡
# 3. 如果打了上班卡，接下來每隔 30 分鐘會幫忙打卡一次 (延遲五分鐘 的每隔30分)
# 3.5 可能考慮截圖，避免有打卡但沒有成功
# 4. 如果打卡到最後一個時候
DoesWorkStart = False
WorkStartTime = datetime.now()
DoesWorkEnd = False
WorkEndTime = datetime.now()

# 1.
#region
PersonalM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_DataList.asp", Cookies)
TableData = PersonalM.Soup.find_all("nobr")
__PrintSplitLine()
print("上班時間列表：")
for i in range(0, len(TableData), 2):
    print(TableData[i].text + " " + TableData[i + 1].text)
    if TableData[i].text.find(TodayString) != -1 and TableData[i + 1].text == "上班":
        DoesWorkStart = True
        WorkStartTime = datetime.strptime(TableData[i].text, "%Y-%m-%d %H:%M:%S")
    elif TableData[i].text.find(TodayString) != -1 and TableData[i + 1].text == "下班":
        DoesWorkEnd = True
        WorkEndTime =  datetime.strptime(TableData[i].text, "%Y-%m-%d %H:%M:%S")
__PrintSplitLine()
#endregion

# 2.
#region
Schedule = []
if not DoesWorkStart:
    PunchInProcess(Cookies)

print("本日上班打卡時間：")
print(WorkStartTime)
print()
WorkStartTime +=  timedelta(minutes=TimeOffsetMins)
FinalWorkTime = WorkStartTime + timedelta(hours=9.25)
#endregion

# 3.
# 先把所有上班的打卡時間加入
#region
for i in range (int(9.25 * 60 / TimeIntervalMins)):
    WorkStartTime += timedelta(minutes=TimeIntervalMins)
    Schedule.append(WorkStartTime)
Schedule.append(FinalWorkTime)
for i in range(len(Schedule) - 1, -1, -1):
    if Schedule[i] < Today:
        Schedule.pop(i)

# 顯示接下來要打卡的時間
for i in range(len(Schedule)):
    print(Schedule[i])
PunchOutProcess(Cookies)
#endregion

# 3.
# 