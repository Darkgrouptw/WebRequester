from os import rename
from bs4 import BeautifulSoup

class Manager:
    AppendTop = [
        "<table align='right' border='0' cellpadding='5' cellspacing='0' width='99%'>",
        "<tbody>",
        "<td bgcolor='#C9F1E9' height='200' valign='top'>",
        "<table>",
        "<table align='center' border='0' cellpadding='0' cellspacing='1' width='680' bgcolor='#C9F1E9'>"
    ]
    AppendEnd = [
        "</table>",
        "</td>",
        "</tr>",
        "</table>",
        "</td>",
        "</tbody>",
        "</table>"
    ]

    @staticmethod
    def Transfor(Response) -> str:
        bs = BeautifulSoup(Response.text, "html.parser")
        trList = bs.find_all("tr")

        # 抓取刷卡紀錄
        FindeIndex = -1
        for i in range(len(trList) - 2, 0, -1):
            if str(trList[i]).find("刷卡記錄完成！！") != -1:
                FindeIndex = i
                break
        
        # 把 HTML 儲存起來
        if FindeIndex != -1:
            OutputHTML = ""
            for i in range(len(Manager.AppendTop)):
                OutputHTML += Manager.AppendTop[i] + "\n"
            OutputHTML += str(trList[FindeIndex]) + "\n" + str(trList[FindeIndex + 1])
            for i in range(len(Manager.AppendEnd)):
                OutputHTML += Manager.AppendEnd[i] + "\n"
            return OutputHTML
        print("截圖工具有落差，抓不到資料")
        return None
