from FormDataManager import Manager as FDM
from VPNManager.Manager import VPNManager as VPN
from datetime import date, datetime
import sys
import os

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
#endregion

# 抓取打卡的資訊
# 登入
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
Today = date.today().strftime("%Y-%m-%d")
print("日期:", Today)

# 接者進打卡頁面
# 1. 拿取目前的打卡列表
# 2. 如果沒有打上班卡，立即幫忙打上班卡
# 3. 如果打了上班卡，接下來每隔 30 分鐘會幫忙打卡一次 (延遲五分鐘 的每隔30分)
# 4. 如果打卡到最後一個時候
DoesWorkStart = False
WorkStartTime = datetime.now()
DoesWorkEnd = False
WorkEndTime = datetime.now()

# 1.
PersonalM = FDM.Manager("http://tpehr.wkec.com/ehrportal/DEPT/Personal_CardData_DataList.asp", Cookies)
TableData = PersonalM.Soup.find_all("nobr")
__PrintSplitLine()
print("上班時間列表：")
for i in range(0, len(TableData), 2):
    print(TableData[i].text + " " + TableData[i + 1].text)
    if TableData[i].text.find(Today) != -1 and TableData[i + 1].text == "上班":
        DoesWorkStart = True
        WorkStartTime = datetime.strptime(TableData[i].text, "%Y-%m-%d %H:%M:%S")
    elif TableData[i].text.find(Today) != -1 and TableData[i + 1].text == "下班":
        DoesWorkEnd = True
        WorkEndTime =  datetime.strptime(TableData[i].text, "%Y-%m-%d %H:%M:%S")
__PrintSplitLine()


# 2.
if DoesWorkStart:
    print("本日上班打卡時間：")
    print(WorkStartTime)

# LoginM = FDM.Manager("https://tp-epm.winkingworks.com/Login.aspx")
# LoginM.FetchParamsByID("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
# LoginM.AddParams("Account", sys.argv[1])
# LoginM.AddParams("Password", sys.argv[2])
# LoginM.AddParams("ImageButton1.x", "-1")
# LoginM.AddParams("ImageButton1.y", "-1")
# Response = LoginM.Post()
# Cookies = Response.cookies
# print(Cookies.get_dict())

# 填寫今天的進度
# CT => 2679
# HAZ => 2682
# Today = date.today().strftime("%Y-%m-%d")
# TodayM = FDM.Manager("https://tp-epm.winkingworks.com/Works/WorksAdd.aspx?Date=" + Today, Cookies)
# TodayM.FetchParamsByID("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
# TodayM.AddParams("ctl00$ContentPlaceHolder1$ProjectDDL", sys.argv[3])
# TodayM.AddParams("ctl00$ContentPlaceHolder1$WorkHoursDDL", 8)
# TodayM.AddParams("ctl00$ContentPlaceHolder1$WorkTypeDDL", 1)
# TodayM.AddParams("ctl00$ContentPlaceHolder1$Button1", "提報")
# TodayM.AddParams("__VIEWSTATEENCRYPTED", "")
# TodayM.AddParams("__ASYNCPOST", False)
# Response = TodayM.Post(Cookies)

#  成功判定
# if Response.status_code == 200:
#     print("成功提報工時 !!")
# else:
#     print("失敗 !!")

# print(Response.status_code)
# print(Response.content)
# print(Response.status_code)
# print("")
# os.system("PAUSE")