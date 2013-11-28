#
# serial to websocket
# http://manticore.deadmediafm.org
#
# dependencies: websocket-client [included] , pySerial [manual install]
#
# instructions:
# 1.install pySerial [https://pypi.python.org/pypi/pyserial]
# 2.connect arduino
# 3.edit config variables [baud rate, device path]
# 4.python arduino.py
# 5.open http://intense-eyrie-9186.herokuapp.com


#==========
# libraries
#==========

import re
import serial
import threading
import time

from websocket import create_connection

#============
#   config
#============

webSocketURL = 'ws://intense-eyrie-9186.herokuapp.com'
webSocketDelay = 0.8 # 800 ms delay
arduinoDevice = '/dev/cu.usbserial-A7007btz'
arduinoBaud = 9600

#======
# code
#======

global SerialOut, dead, ThreadLock

ThreadLock = threading.Lock()
SerialOut = ""
dead = False

class WsThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ws = create_connection(webSocketURL)
        print "== init ws thread =="
    def run(self):
        global SerialOut,ThreadLock
        while (not dead):
            ThreadLock.acquire()
            tmpSer = SerialOut
            ThreadLock.release()
            self.ws.send(tmpSer)
            time.sleep(webSocketDelay)
                
class ArduinoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ser = serial.Serial(arduinoDevice, arduinoBaud, timeout=1)
        print "== init arduino thread =="
    def run(self):
        global SerialOut,ThreadLock
        while (not dead):
            SerialOut = self.ser.readline()
        self.ser.close()


if __name__ == "__main__":
    myWebsocket = WsThread()
    myArduino = ArduinoThread()
    myArduino.start()
    myWebsocket.start()
    
    raw_input("== enter to finish ==")
    
    dead = True
    
    myWebsocket.join()
    myArduino.join()

    print "== all thread has been terminated =="
