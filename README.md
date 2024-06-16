# NetStructer

First, i made this module to earn some money to change my 4Gram Pc so if you can support us on https://www.buymeacoffee.com/Arcade.m7 , if you can't np enjoy. 

The module facilitates secure communication between client and server applications over TCP/IP by providing classes and utilities for encryption, data transmission, error handling, and session management. 

The central component of the module is the Bridge class, which acts as a communication bridge between the client and server. It handles encryption and decryption of data sent over the network to ensure secure transmission. The Bridge class also provides methods for sending and receiving data buffers between client and server.

Encryption is handled by the _encryption class, which uses the Fernet encryption scheme from the cryptography library. It provides methods for encrypting and decrypting data using a specified encryption key.

Error handling is implemented through the Error class, which defines custom error types for handling server initialization errors and buffer data errors.

The module also includes a Server class for creating and managing server instances. The Server class initializes a socket server, listens for incoming connections, and handles communication sessions with client applications.

Additionally, the Container class offers a convenient interface for managing session data. It provides methods for storing, retrieving, and clearing session data associated with client connections.

Overall, this module offers a comprehensive solution for implementing secure client-server communication over TCP/IP, with features for encryption, error handling, and session management.

## Installation
You can install NetStructer using pip:
```bash
pip install NetStructer
```
## Features
add side way encryption and maybe more ...

**here a simple exmaple of NetStructer**

## Client Side
```python
from NetStructer import Bridge
addr = ('192.168.1.5',5000) # addr of the server thats you want to connect
bridge = Bridge.Link(addr)
bridge.SendBuffer(['hi im haytam',128,{b'gg':'gg'},{1,2,6,4},(False,True)])
bridge.SendBuffer('support us on https://www.buymeacoffee.com/Arcade.m7')
```

## Server Side

```python
from NetStrcuter impor Server

addr = ('192.168.1.5',5000) # address

server = Server(addr)
server.init()
server.listen()
	
#server.count()  return len of sessions
#server.all()  return all of the sessions
#server.get(parm) return parm value from the container | Note parm var must be the ip of the session thats you want to get
#server.pop(parm) return the value of parm and remove the session from container
#server.clear()  close the sessions
	
session = server.get('192.168.1.4') #the ip of the session
buff = session.RecvBuffer(size=1024*100,buffer_size=100000)# size like socket.recv(1024) default is 1024 | buffer_size it mean how mush well recv if the data biger then buffer_size well raise a Error.BufferDataError
print(buff) #['hi im haytam',128,{b'gg':'gg'},{1,2,6,4},(False,True)]
string = session.RecvBuffer()
print(string) #'support us on https://www.buymeacoffee.com/Arcade.m7'
```
	
```python
from NetStructer import Server , Bridge

addr = ('192.168.1.5',5000) # address
	
server = Server(addr)
server.init()
	
def func(socket,cont):
	while True: # note cont object is a dict 
		try:
			soc,addr = socket.accept()
			cont[addr[0]] = Bridge(soc)
		except:
			pass
	server.listen_on(func)
```
	
## Server.listen_on function

```Python
 sessions = []

def func(socket,_):
	while True:
		try:
			soc , addr = socket.accept()
			sessions.append(soc)
	except : pass
			
server.listen_on(func)
```

## Finally
if you like this project please leave a star with you
