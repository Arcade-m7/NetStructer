# NetStructer

First, i made this module to earn some money to change my 4Gram Pc so if you can support us on https://www.buymeacoffee.com/Arcade.m7 , if you can't np enjoy. 

## Module Description:

This module implements a TCP-based communication system with symmetric encryption (using the Fernet encryption scheme). It facilitates secure communication between clients and servers, managing file transfers and session handling over encrypted channels. The module offers functionality for both sides of a connection (client and server) and includes tools for file management, session tracking, encryption, and custom error handling.

# Encrypted Communication Module
This Python module provides a flexible and secure way to handle encrypted data transfers over a network using TCP connections. It simplifies the process of sending and receiving encrypted data while supporting temporary file storage and session management. The module is designed to handle large files, streams of data, and ensures secure communication using modern encryption standards.

## Features
* Encrypted Communication: All data transferred between clients and servers is encrypted using the Fernet encryption protocol from the Cryptography library, ensuring secure transmission.
* TCP-Based Communication: Built around TCP sockets for reliable network communication.
* Temporary Data Storage: Uses NamedTemporaryFile to efficiently store large amounts of data without overloading system memory.
* Session Management: Tracks and manages active sessions, allowing data to be associated with specific clients.
* Compressed Transfers: Data is compressed before transmission, making it more bandwidth-efficient for large transfers.
* Customizable Buffer Size: The module allows you to specify buffer sizes for reading and writing data, optimizing for different network conditions.
* Error Handling: Includes error classes for server initialization issues and buffer overflow prevention.

## Installation

```bash
pip install NetStructer
```


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

## Server.listen_on function

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
	
## other example of Server.listen_on function

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

## Features in Detail
1. Encrypted Data Transfers:
  * Data is securely encrypted using Fernet, making it unreadable to unauthorized entities.
2. Temporary File Storage:
  * Large chunks of data are temporarily stored using NamedTemporaryFile to avoid consuming too much memory.
3. Session Management:
  * Easily manage multiple client sessions through the Container class that tracks client connections.
4. Efficient Data Handling:
  * Data is compressed before sending, which speeds up transmission and reduces bandwidth usage.
5. Customizable:
  * The module allows you to adjust chunk sizes, timeouts, and encryption keys as needed.

## Finaly
i work hard for this module so please suport us or just leave a star with you
