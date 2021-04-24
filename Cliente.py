##
import socket
import hashlib
import os
import logging
from datetime import datetime


## Inicialización variables

host='127.0.0.1'
port=1233
SEPARATOR = "~"
BUFFER_SIZE = 32768
TIMEOUT = 3
nombre_Archivo=''

##
if not os.path.exists('ArchivosRecibidos'):
    os.makedirs('ArchivosRecibidos')
if not os.path.exists('Logs'):
    os.makedirs('Logs')


now=datetime.now()
filename='Logs/'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'-logCliente.txt'
logging.basicConfig(filename=filename, level=logging.DEBUG)

ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (host, port)

## Fúncion para hacer hashing del archivo
def hash_file(filename):
   h = hashlib.sha1()
   with open(filename,'rb') as file:
       chunk = 0
       while chunk != b'':
           chunk = file.read(1024)
           h.update(chunk)
   return h.hexdigest()

def TCP_Hash():
    s = socket.socket()
    port = 3000

    s.connect((host, port))
    hash = s.recv(BUFFER_SIZE).decode()
    if hash_file(nombre_Archivo)==hash:
        s.send('1'.encode())
        logging.info('Hash correcto')
    s.close()
## Estado actual del cliente
var = input('¿Esta el cliente listo para recibir(Opciones 0(No),1(Si)')
if var == "Si" or var == "1":
    ClientSocket.sendto("1".encode(), server_address)
else:
    exit()
## Recibimiento de datos del servidor
datos_iniciales, server = ClientSocket.recvfrom(BUFFER_SIZE)
datos_iniciales = datos_iniciales.decode().split('-')

## Creación de path donde se guarda el archivo
nombre_Archivo='ArchivosRecibidos/Cliente'+str(datos_iniciales[0])+'-Prueba-'+str(datos_iniciales[1])+'.txt'
datos_iniciales_2, server = ClientSocket.recvfrom(BUFFER_SIZE)
datos_iniciales_2 = datos_iniciales_2.decode().split('-')
# Logging
logging.info('Nombre de archivo recibido :'+str(datos_iniciales_2[0]))
logging.info('Tamaño real de archivo recibido :'+str(datos_iniciales_2[1]))
logging.info('Soy el cliente '+str(datos_iniciales[0]+' de '+str(datos_iniciales[1])+' conexiones'))
print('Nombre de archivo recibido :'+str(datos_iniciales_2[0]))
print('Tamaño real de archivo recibido :'+str(datos_iniciales_2[1]))
## Escritura de paquetes recibidos hacia archivo

ClientSocket.settimeout(TIMEOUT)
numBytesRecibidos = 0
numPaquetesRecibidos = 0
with open(nombre_Archivo, "wb") as f:
    tiempoInicio = datetime.now()
    try:
        while True:
            data, addr = ClientSocket.recvfrom(BUFFER_SIZE)
            if SEPARATOR in data.decode():
                numPaquetesRecibidos += 1
                text = data.decode().split(SEPARATOR)
                data = text[0].encode()
                numBytesRecibidos+= len(data)
                f.write(data)
                f.close()
                break
            numPaquetesRecibidos += 1
            print(numPaquetesRecibidos)
            numBytesRecibidos += len(data)
            f.write(data)  # write to the file the bytes we just received
    except:
        print()

tiempo_Final= datetime.now()
tiempoTotal=(tiempo_Final-tiempoInicio).microseconds


tamanio_Archivo=os.path.getsize(nombre_Archivo)
logging.info('Tamaño de archivo recibido: '+str(tamanio_Archivo)+' bytes')
logging.info('Tiempo recepción de archivo  :' + str(tiempoTotal) + ' microsegundos')
logging.info('Numero Paquetes Recibidos: '+str(numPaquetesRecibidos))
logging.info('Numero Bytes Recibidos: '+str(numBytesRecibidos/8))
print('Cerrrando socket...\n')
TCP_Hash()

