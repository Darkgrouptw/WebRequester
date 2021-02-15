from FormDataManager import Manager as FDM
from datetime import date
import sys
import os

if len(sys.argv) <= 3:
    print("要給三個參數，帳號 & 密碼 & 專案名稱(CT=>2679、HAZ=>2682)")
    os.system("PAUSE")
    exit()

LoginM = FDM.Manager("https://tp-epm.winkingworks.com/Login.aspx")
LoginM.FetchParamsByID("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
LoginM.AddParams("Account", sys.argv[1])
LoginM.AddParams("Password", sys.argv[2])
LoginM.AddParams("ImageButton1.x", "-1")
LoginM.AddParams("ImageButton1.y", "-1")
Response = LoginM.Post()
Cookies = Response.cookies
print(Cookies.get_dict())

# 填寫今天的進度
# CT => 2679
# HAZ => 2682
Today = date.today().strftime("%Y-%m-%d")
TodayM = FDM.Manager("https://tp-epm.winkingworks.com/Works/WorksAdd.aspx?Date=" + Today, Cookies)
TodayM.FetchParamsByID("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION")
TodayM.AddParams("ctl00$ContentPlaceHolder1$ProjectDDL", sys.argv[3])
TodayM.AddParams("ctl00$ContentPlaceHolder1$WorkHoursDDL", 8)
TodayM.AddParams("ctl00$ContentPlaceHolder1$WorkTypeDDL", 1)
TodayM.AddParams("ctl00$ContentPlaceHolder1$Button1", "提報")
TodayM.AddParams("__VIEWSTATEENCRYPTED", "")
TodayM.AddParams("__ASYNCPOST", False)
Response = TodayM.Post(Cookies)

#  成功判定
if Response.status_code == 200:
    print("成功提報工時 !!")
else:
    print("失敗 !!")

# print(Response.status_code)
# print(Response.content)
# print(Response.status_code)
print("")
os.system("PAUSE")