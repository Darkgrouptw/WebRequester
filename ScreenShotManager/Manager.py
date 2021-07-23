from bs4 import BeautifulSoup

class Manager:
    @staticmethod
    def Transfor(Response) -> str:
        bs = BeautifulSoup(Response.text, "html.parser")
        trList = bs.find_all("tr")
        # print(trList[20].encode("utf8").decode("cp950", "ignore"))