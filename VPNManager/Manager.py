import time
import os

class VPNManager:
    @staticmethod
    def Connect():
        os.popen("rasphone -d WinkingTest -f ./VPN.pbk")
    
    @staticmethod
    def Discount():
        os.popen("rasphone -H WinkingTest")
