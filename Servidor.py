

import socket
import hashlib
from _thread import *
import time
import logging
import threading
from datetime import datetime
import os


## Inicialización variables
host='127.0.0.1'
port=1233
puerto_TCP=3000
ThreadCount=0
EstadoClientes=1
Clientes=[]
enviados=0
SEPARATOR = "~"
BUFFER_SIZE = 32768

## Inicialización Logging
if not os.path.exists('Logs'):
    os.makedirs('Logs')
now=datetime.now()
print('CREACIÓN LOG')
filename='./Logs/'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'-logServidor.txt'
logging.basicConfig(filename=filename, level=logging.DEBUG)

## Función para hallar el hash al archivo
def hash_file(filename):
   h = hashlib.sha1()
   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           chunk = file.read(1024)
           h.update(chunk)
   return h.hexdigest()

# Servidor comenzando, inicializacipon conexiones esperadas y archivo a enviar
print('Waiting for connection...')
NumeroConexiones=input('¿A cuántos clientes quiere enviar el archivo ?')
NumeroConexiones=int(NumeroConexiones)
Archivo_Tamaño=input('Que archivo quiere mandar? (Opciones posibles 100-250)')
if Archivo_Tamaño=='100':
    Archivo='Archivos/Archivo100.txt'
    tamanioArchivo = os.path.getsize(Archivo)
elif Archivo_Tamaño=='250':
    Archivo='Archivos/Archivo250.txt'
    tamanioArchivo = os.path.getsize(Archivo)
else:
    Archivo='Archivos/Archivo100'
    tamanioArchivo=os.path.getsize(Archivo)
    print('No se reconoce el archivo, se maneja el archivo de 100MB')
# Creación de flag para saber cuando ya hay los clientes necesarios
event = threading.Event()
print('Evento creado')
logging.info('Nombre de archivo enviado: '+Archivo)
logging.info('Tamaño de archivo enviado: '+str(tamanioArchivo/1048576)+' MB')
logging.info('Se envia el archivo a: '+str(NumeroConexiones)+' clientes')


print('\n Esperando las conexiones suficientes para enviar archivo')


# Creación socket servidor UDP
ServerSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Socket creado')
# Binding socket to host and port
try:
    ServerSocket.bind((host,port))
    print('Socked bind')
except socket.error as e:
    print(str(e))




## Función de envío archivo al cliente
def threaded_client(connection, i):
    global enviados
    while not event.isSet():
        event.wait(1)
    logging.info('Conexión realizada por el cliente  número'+str(i)+'con un socket que tiene la siguiente dirección'+str(connection))
    mensaje=str(Archivo)+'-'+str(tamanioArchivo)
    ServerSocket.sendto(mensaje.encode(), connection)
    numPaquetesEnviados = 0
    numBytesEnviados = 0
    f = open(Archivo, 'rb')
    # Lectura archivo
    l = f.read(BUFFER_SIZE)
    tiempo_Inicio = datetime.now()
    while (l):
        try:
            # Envio archivo
            ServerSocket.sendto(l,connection)
            numPaquetesEnviados+=1
            numBytesEnviados+=len(l)
            l = f.read(BUFFER_SIZE)
        except Exception:
            pass
    # Cierre archivo
    f.close()
    ServerSocket.sendto(SEPARATOR.encode(),connection)
    tiempo_Final = datetime.now()
    tiempo_Envio = tiempo_Final - tiempo_Inicio
    tiempo_Envio = tiempo_Envio.microseconds
    logging.info('Tiempo envio de archivo a cliente ' + str(i) + ':' + str(tiempo_Envio) + ' microsegundos')
    logging.info('Cantidad de bytes enviados'+str(numBytesEnviados/8))
    logging.info('Cantidad de paquetes enviados'+str(numPaquetesEnviados))
    enviados += 1
    print(enviados)

# Conexion activa a clientes e inicio de funciones
while True:
    if ThreadCount<NumeroConexiones:
        print('numeroConexionesMenor')
        data, address = ServerSocket.recvfrom(BUFFER_SIZE)
        if str(data.decode()) == str(EstadoClientes):
            Clientes.append(address)
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            ThreadCount += 1
            print(ThreadCount)
            mensaje=str(ThreadCount)+'-'+str(NumeroConexiones)
            ServerSocket.sendto(mensaje.encode(), address)
            start_new_thread(threaded_client, (address, ThreadCount,))
            print('Thread Number: ' + str(ThreadCount))
    if ThreadCount == NumeroConexiones:
        event.set()
    if enviados==NumeroConexiones:
        print('Se cierran conexiones')
        ServerSocket.close()
        break
ThreadCount = 0
print('intentando TCP')
s = socket.socket()
s.bind((host, puerto_TCP))
s.listen(5)
message = hash_file(Archivo)
print('Calculo hash')
print(message)
while True:
    if ThreadCount < NumeroConexiones:
        client, address = s.accept()
        ThreadCount += 1
        client.send(message.encode())
        data = client.recv(BUFFER_SIZE)
        data=data.decode()
        data=data.split('-')
        if str(data[0])==str(1):
            logging.info('Transferencia exitosa a cliente ' + str(data[1]))
            client.close()
        else:
            logging.info('Transferencia no exitosa a cliente ' + str(data[1]))
            client.close()
    if ThreadCount == NumeroConexiones:
        s.close()
        break




