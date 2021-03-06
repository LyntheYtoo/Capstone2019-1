"""
2019-05-10

상속 클래스
ThingsInfo
ThingsSerial
CommuHandler

이것이 하나의 Things 클래스

"""

import asyncio
from CommuHandler import ClientHandler
from test import ClientCommunication as tcp, ThingsSerial as serial


class ThingsMain():
    
    ip = "52.78.166.156"
    port = 22
    
    def __init__(self):
        pass
        

    def Serial_Read_after_Trans_Server(self):
        #arduino = serial.ThingsSerial("/dev/ttyUSB0", 9600) Raspberry
        arduino = serial.ThingsSerial("COM4", 9600) #Windows
        #handle = ClientHandler(self.ip, self.port)
     
        while True:
            message = arduino.Serial_readline();

            if message:
                handle = ClientHandler(self.ip, self.port)
                asyncio.run(tcp.tcp_echo_client(self.ip, self.port, message.decode("utf-8")))
            
            
begin = ThingsMain()
begin.Serial_Read_after_Trans_Server()

