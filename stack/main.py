#!/usr/bin/env python  
#encoding: utf-8
import socket, threading
from time import ctime
import db
import manager

SERVER = '127.0.0.1' #主机IP  
PORT = 8080 #端口号  
MAXTHREADS = 10
RECVBUFLEN = 1024

class ComunicateServer(threading.Thread):
    def __init__(self, clientsocket, address, num):
        threading.Thread.__init__(self)
        self.socket = clientsocket
        self.num = num
        self.address = address
        self.authFlag = 0
        self.username = ''
        self.passwd = ''
        self.host = ''
        print 'New thread [%d] started!' % self.num 
    
    def run(self):
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            commandList = data.split('@')
            command = commandList[0]
            
            #userauth: format--log@user@passwd
            if command == 'log':
                if self.authFlag == 1:
                    self.socket.send(2)
                else:
                    res = db.userAuth(commandList[1], commandList[2])
                    if res == None:
                        self.socket.send(0)
                    else:
                        self.username = commandList[1]
                        self.passwd = commandList[2]
                        self.host = res
                        self.socket.send(1)
            
            #userreg: format--reg@user@passwd
            if command == 'reg':
                if self.authFlag == 1:
                    self.socket.send(2)
                else:
                    username = commandList[1]
                    passwd = commandList[2]
                    res = db.userAdd(username, passwd)
                    self.socket.send(res)
            
            #flavor: format--flavor
            if command == 'flavor':
                if self.authFlag == 0:
                    self.socket.send(0)
                else:
                    res = manager.getFlavor(self.username, self.passwd, self.host)
                    self.socket.send(res)
            
            #image: format--img
            if command == 'img':
                if self.authFlag == 0:
                    self.socket.send(0)
                else:
                    res = manager.getImage(self.username, self.passwd, self.host)
                    self.socket.send(res)
            #createvm: formant--createvm@vmname@imagename@flavorname
            if command == 'createvm':
                if self.authFlag == 0:
                    self.socket.send(0)
                else:
                    vmname = commandList[1]
                    imagename = commandList[2]
                    flavorname = commandList[3]
                    res = manager.createVM(self.username, self.passwd, self.host, vmname, imagename, flavorname)
                    self.socket.send(res)
            
            self.socket.send('[%s] %s %s' % (ctime(), data, self.address))
        self.socket.close()

class ListenServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.socket = None
        print 'Start Listen....'
        
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((SERVER,PORT))
        self.socket.listen(2)
        num = 1
        while True:
            cs,address = self.socket.accept()
            comser = ComunicateServer(cs, address, num)
            comser.start()
            num += 1
            print 'Listen Next...'
        self.socket.close()

if __name__ == '__main__':
    asvr = ListenServer()
    asvr.start()
    asvr.join()