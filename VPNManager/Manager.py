import time
import os

class VPNManager:
    @staticmethod
    def Connect():
        buffer = os.popen("rasdial WinkingTest wk999 Wkec!999@2021 /PHONEBOOK:VPN.pbk", "r")
        contents = buffer.readlines()
        print("VPN Manager (Connected): ")
        for i in range(len(contents)):
            print(contents[i][:-1])
    
    @staticmethod
    def Discount():
        buffer = os.popen("rasdial WinkingTest /DISCONNECT", "r")
        contents = buffer.readlines()
        print("VPN Manager (Disconnected): ")
        for i in range(len(contents)):
            print(contents[i][:-1])
