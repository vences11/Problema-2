import socket
import threading
import logging
import time
from FTP import *
from os import listdir
from os.path import isfile, join
bufferSize = 512
logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-2s) %(message)s',)

def ls(ruta = 'imgS/.'):
    return [arch for arch in listdir(ruta) if isfile(join(ruta, arch))]


def servirPorSiempre(TCPServerSocket,FTP):
    print("servidor listo para atender clientes")
    try:
        while True:
            Client_conn=FTP.sConect(TCPServerSocket)
            thread_read = threading.Thread(name='Server', target=Atender, args=[Client_conn])
            thread_read.start()
    except Exception as e:
        print(e)

def Atender(conn):
     time.sleep(1)
     FTP.sLogin(conn)
     time.sleep(1)
     FTP.sDIR(conn)
     time.sleep(1)
     FTP.sSET(conn)
     time.sleep(1)
     FTP.sCLOSE(conn)

HOST ='192.168.0.26' #Direccion del servidor
PORT =21  #Puerto del servidor
threading.current_thread().setName("Server")
FTP=protocoloTFP('admin','user')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen()
    print("El servidor FTP está disponible y en espera de solicitudes")
    servirPorSiempre(TCPServerSocket,FTP)