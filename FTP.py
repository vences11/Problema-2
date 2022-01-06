import socket
import threading
import logging
from pathlib import Path
import time
from os import listdir
from os.path import isfile, join
import shutil
bufferSize = 512
logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-2s) %(message)s',)


def ls(ruta = 'imgS/.'):
    return [arch for arch in listdir(ruta) if isfile(join(ruta, arch))]

class protocoloTFP(object):
    def __init__(self,p='null',u='null'):
        self.pw=p
        self.user=u

    def cLogin(self,TCPClientSocket,p,u):
        logging.debug("Mandando comando : Login\n")
        TCPClientSocket.send(str("Login").encode('utf-8'))
        Mensaje = str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
        if str(Mensaje)=='ok':
            p = input("\nIngrese usuario: ")
            TCPClientSocket.send(str("USER," + p).encode('utf-8'))
            Mensaje = str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
            logging.debug(Mensaje)
            c = input("\nIngrese Contraseña: ")
            TCPClientSocket.send(str("PASS," + c).encode('utf-8'))
            Mensaje = str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
            if int(Mensaje) == 230:
                logging.debug('Server ' + Mensaje + " : Usuario conectado")
            else:
                logging.debug('Server ' + Mensaje + " : Usuario o contraseña incorrectas")
                self.sCLOSE(TCPClientSocket)



    def sLogin(self, conn):
        Mensaje = str(conn.recv(bufferSize).decode('utf-8'))
        conn.send(str('ok').encode('utf-8'))
        logging.debug(Mensaje)
        u = str(conn.recv(bufferSize).decode('utf-8'))
        coman, U = u.split(',')
        logging.debug('recibio: '+coman+' respuesta: 231')
        conn.send(str('Server  231: necesita contraseña').encode('utf-8'))
        p = str(conn.recv(bufferSize).decode('utf-8'))
        coman, P = p.split(',')
        if str(U)==self.user and str(P)==self.pw:
              logging.debug('recibio: ' + coman + ' respuesta: 230')
              conn.send(str('230').encode('utf-8'))
        else:
              logging.debug('recibio: ' + coman + ' respuesta: 530')
              conn.send(str('530').encode('utf-8'))
              self.sCLOSE(conn)



    def cConect(self,TCPClientSocket,HOST,PORT):
        TCPClientSocket.connect((HOST, PORT))
        logging.debug("Mandando comando : Conect")
        TCPClientSocket.send(str('CONECT').encode('utf-8'))
        Mensaje= str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
        logging.debug(Mensaje)

    def sConect(self,TCPClientSocket):
        conn, addr = TCPClientSocket.accept()
        print("Conectando")
        Mensaje = str(conn.recv(bufferSize).decode('utf-8'))
        conn.send(str('Server: 200').encode('utf-8'))
        logging.debug('recibio: ' + Mensaje + ",Respuesta: 200")

        return conn

    def cDIR(self, TCPClientSocket):
        logging.debug("Mandando comando DIR")
        TCPClientSocket.send(str('dir').encode('utf-8'))
        mensaje = str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
        logging.debug(mensaje)
        dir = str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
        time.sleep(1)
        print(dir)


    def sDIR(self, conn):
        Mensaje = str(conn.recv(bufferSize).decode('utf-8'))
        logging.debug('recibio: ' +Mensaje+",Respuesta: 200")
        conn.send(str('Server: 200').encode('utf-8'))
        dir=str(ls())
        conn.send(str(dir).encode('utf-8'))


    def cCLOSE(self, TCPClientSocket):
        logging.debug("Mandando comando CLOSE")
        TCPClientSocket.send(str('CLOSE').encode('utf-8'))
        mensaje = str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
        logging.debug(mensaje)

    def sCLOSE(self, conn):
        Mensaje = str(conn.recv(bufferSize).decode('utf-8'))
        logging.debug('recibio: ' +Mensaje+",Respuesta: 221")
        conn.send(str('Server: 221').encode('utf-8'))

    def mandar(self, conn,file):
        o='imgS/'+ file
        I = open(o,'r')
        #conn.send(str('250 ').encode('utf-8'))
        sendI = I.read(1024*5)
        EsendI = sendI.encode('utf-8')
        while EsendI:
            conn.sendall(EsendI)
            sendI = I.read(1024*5)
            EsendI = sendI.encode('utf-8')
            break
        logging.debug("Archivo enviado, Respuesta 250")
        time.sleep(2)

    def recibir(self, TCPClientSocket):
        while True:
            #rec = TCPClientSocket.recv(bufferSize).decode('utf-8').split()
            rec_num = 1
            name = 'transfer_'+str(rec_num)+'.txt'
            r = open(name, 'w')
            recibe_img = TCPClientSocket.recv(1024*5).decode('utf-8')
            while recibe_img:
               r.write(recibe_img)
               recibe_img = TCPClientSocket.recv(1024*5).decode('utf-8')
               break
            logging.debug("Archivo descargado: "+str(name))
            rec_num = rec_num + 1



    def cSET(self, TCPClientSocket):
        com = input("\n\nArchivos disponibles:")
        logging.debug("Mandando comando SET")
        TCPClientSocket.send(str('SET,'+ com).encode('utf-8'))
        mensaje = str(TCPClientSocket.recv(bufferSize).decode('utf-8'))
        logging.debug("Server :"+mensaje)

        if int(mensaje)==213:
            self.recibir(TCPClientSocket)

        else:
            self.sCLOSE(TCPClientSocket)

    def sSET(self, conn):
        Mensaje = str(conn.recv(bufferSize).decode('utf-8'))
        com,img =Mensaje.split(',')
        logging.debug('recibio: '+com+",Respuesta: 200")
        fileName = "imgS/" + str(img)
        fileObj = Path(fileName)
        if fileObj.is_file():
            logging.debug('Respuesta: 213, archivo existente')
            conn.send(str('213').encode('utf-8'))
            self.mandar(conn,img)

        else:
            logging.debug('Respuesta: 501,archivo no existente')
            conn.send(str('501').encode('utf-8'))