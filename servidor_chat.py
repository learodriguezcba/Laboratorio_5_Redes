import socket
import sys
import select
import Queue
from os import listdir
import os
from os.path import isfile, join


arglen=len(sys.argv)
if arglen<2:
    print('Ejemplo: python2 servidor_chat.py 5000')
    exit()

puerto=int(sys.argv[1])

#Se crea un socket TCP/IP con tipo UDP
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Se declara la variable donde se almacenara el nombre del cliente
clientes=[]

#En esta variable se van a encolar los mensajes que vengan desde el cliente
cola_de_mensajes = {}

#Se asigna "puerto" a la variable servidor (Socket)
servidor.bind(("", puerto))

#Se habilita al socket para recibir conexiones
servidor.listen(1)

print ('Esperando para conectarse')

#Se crea una variable que almacenara lo que se escriba por teclado desde el servidor
teclado=sys.stdin

#Se crea una variable que contendra lo que vendra del teclado y lo que vendra del socket
entradas=[teclado, servidor]

#Se crea la variable "mensaje" que contendra lo que se enviara al cliente
mensaje = ""

client_address=""

#Se crea el timer
timeout=600

#s es un elemento de la lista listo_leer
s=0

while True:
    
    #Esta funcion es para monitorear un conjunto de descriptores de sockets y avisar
    #cuales tienen datos para leer, para escribir, o que produjeron excepciones 
    #listo_leer, listo_escribir y _err. Son listas file descriptor

    listo_leer, listo_escribir, _err = select.select(entradas, [], [], timeout)
    
    #Si listo_leer no esta vacia, entonces la recorre con un for para leer lo que contiene 
    if not listo_leer==[]:
        for s in listo_leer:
            #Si s, que es un elemento de listo_leer viene del teclado, usa readline para leer
            #lo que contiene, luego lo imprime en pantalla y por ultimo lo envia"""
            if s is teclado:
                mensaje = teclado.readline()
                connection.sendall(mensaje)

            elif s is servidor:
                #Se ejecuta la funcion accept() que queda en estado de espera
                #hasta que el cliente intente conectarse.
                #El socket se vincula a una direccion y queda escuchando las conexiones.
                #El valor de retorno es una tupla donde connection es un nuevo objeto 
                #socket que se puede usar para enviar y recibir datos, y client_address es la
                #direccion vinculada al socket en el otro extremo de la conexion
                connection, client_address = s.accept()
                print 'Nueva conexion desde el IP '+ str(client_address),
                
                #Se setea el socket del cliente en 0 para que no se bloquee y el servidor
                #siga ejecutandose
                connection.setblocking(0)
                
                #A la lista "entradas" se le agrega un socket descriptor de la nueva conexion recibida                        
                entradas.append(connection)
                
                #Se agrega al diccionario "cola_de_mensajes" una cola especifica para ese cliente
                cola_de_mensajes[connection] = Queue.Queue()
        
            else:
                #Se guarda en "recibido" lo que llega al puerto 
                recibido = s.recv(puerto)
                
                #Se verifica si lo que llega al puerto es el texto "quit", en cuyo caso se envia
                #un aviso al cliente y se procede a cerrar la conexion, se borran la lista de entrada
                if str(recibido) == "quit\n":
                    print ("El cliente ha finalizado  el chat")
                    s.sendall('Cerrando la conexion')
                    s.close()
                    clientes.pop(entradas.index(s)-2)
                    entradas.remove(s)
                    break
                
                #Se verifica si lo que llega al puerto incluye el texto "username", en ese caso divide
                #el texto en partes y toma el nombre del cliente
                elif recibido.find("username") > (-1):
                    lista1 = recibido.split(" ")
                    clientes.append(lista1[1])
                    print clientes[-1]
                
                #Se verifica si lo que llega al puerto incluye el texto "get", en ese caso divide
                #el texto en partes y toma el nombre del archivo que el cliente solicita
                #para luego enviarlo
                elif recibido.find("get") > (-1):
                    lista2 = recibido.split(" ")
                    nombre_de_archivo = lista2[1]
                    print ("El cliente" + clientes[entradas.index(s)-2] + "solicita el archivo "+ nombre_de_archivo)
                    
                    #Se establece la ruta donde se almacena el archivo y se corrobora su existencia
                    archivo = os.getcwd()+"/Archivos_compartidos/"+nombre_de_archivo
                    archivo = archivo.rstrip("\n")
                    print (archivo)
                    existe = os.path.isfile(archivo)
                    print (existe)
                    
                    #Si efectivamente el archivo existe, se procede a enviarlo
                    if existe == True:
                        f = open(archivo, "rb")
                        content = f.read(1024)
                        while content:
                                s.sendall(content)
                                content = f.read(1024)
                        
                        f.close()
                        print("El archivo se envio correctamente")
                    else:
                        #En caso de que el archivo no exista, se envia mensaje de error para el
                        #el servidor y el cliente
                        print ("El cliente solicito un archivo inexistente")
                        s.sendall(chr(2))
                        #s.sendall("El archivo solicitado es inexistente\n")

                #Se verifica si lo que llega al puerto es el texto "list", si es asi 
                #se usa la funcion para mostrar el listado de archivos de una carpeta
                elif str(recibido) == "list\n":
                    print ("Se le envia al cliente el listado de archivos")
                    ruta = os.getcwd()+"/Archivos_compartidos"
                    #Se crea la lista vacia "archivosl". Luego se recorre el directorio, si
                    #si encuentran archivos, se agregan sus nombres dentro de "archivosl"
                    #Una vez creada la lista, se la envia al cliente
                    archivosl=[]
                    archivoss="Contenido del Directorio:\n"
                    for arch in listdir(ruta):
                        if isfile(join(ruta, arch)):
                            archivosl.append(arch)
                    archivoss += '\n'.join(archivosl)
                    s.send(archivoss)
                else: 
                    #En caso de que no se reciba la palabra "quit", imprime el mje en pantalla, 
                    #junto con el nombre del cliente, luego lo agrega a la cola correspondiente en el diccionario de mensajes 
                    print clientes[entradas.index(s)-2] + ": " + str(recibido)
                    cola_de_mensajes[s].put(recibido)
    else:
        print ('Cerrando conexion')
        break

    for s in listo_escribir:
        try:
            #Se saca el mensaje a enviar de la cola ubicada dentro del diccionario 
            #cola_de_mensajes y se envia ese mensaje al cliente"""  
            siguente_msj = cola_de_mensajes[s].get_nowait()
            
        except Queue.Empty:
            print ('La cola de salida para'+ s.getpeername() + 'esta vacia')
            #salidas.remove(s)
        else:
            print ('Enviando'+ siguente_msj + 'a '+ s.getpeername())
            s.send(siguente_msj)