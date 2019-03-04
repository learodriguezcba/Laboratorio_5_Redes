import socket
import sys
import select

arglen=len(sys.argv)
if arglen<3:
    print('Ejemplo: python2 cliente_chat.py 0.0.0.0 5000')
    exit()

addr = sys.argv[1]
port = int(sys.argv[2])

timeout_in_seconds=60
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print ('conectando a %s puerto %d' % (addr, port))

#Se solicita al cliente que ingrese su nombre
nombre = raw_input("Nombre de usuario: ")

cliente.connect((addr,port))
cliente.sendall('username ' + nombre)

teclado=sys.stdin
entradas=[cliente, teclado]
"""Se crea una bandera para mantener el While principal en ejecucion"""
flag=1

while flag==1:
    #Esta funcion es para monitorear un conjunto de descriptores de sockets y avisar
    #cuales tienen datos para leer, para escribir, o que produjeron excepciones 
    #ready, _out y _err son listas file descriptor
    
    ready, _out, _err = select.select(entradas, [], [], timeout_in_seconds)
    
    for elem in ready:

        if elem == teclado:
            respuesta = teclado.readline()
            #print ("Servidor> "+respuesta)
            cliente.sendall(respuesta)
            """Si se envia la palabra "cerrar" al servidor, se cierra el cliente"""
            if str(respuesta) == "quit\n":
                cliente.close()
                print("Sesion finalizada")
                """La bandera en 0 corta la ejecucion del while principal"""
                flag=0
                """Se cierra el ciclo for"""
                break
            if str(respuesta).find("get") > (-1):
                solicitud = respuesta.split(" ")
                archivo = solicitud[1]

                input_data = cliente.recv(1024)
                if input_data == chr(2):
                        print("El archivo no existe")
                else:
                    f = open(archivo, "wb")
                    cliente.settimeout(1)
                    while True:
                        # Recibir datos del cliente.
                        try:
                            f.write(input_data)
                            input_data = cliente.recv(1024)
                        except socket.timeout:
                            print("Archivo recibido correctamente")
                            f.close()
                            break
        elif elem == cliente:
            respuesta = cliente.recv(1024)
            print ("Servidor> "+respuesta)