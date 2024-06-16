from socket import socket
from threading import Thread
from cryptography.fernet import Fernet
from time import sleep
from zlib import compress , decompress
from tempfile import NamedTemporaryFile
from NetStructer.const import *
from NetStructer.tools import *
import pickle

__session__ = {}
#python -c "from NetStructer import Server ; from time import sleep ; server = Server(('',1968)) ; server.init() ; server.listen() ; sleep(5) ; user = server.all()[0] ; user.SendBuffer(list(range(1024*10))) ; server.release()"

class cl: pass

class Mandger:
	
	def __init__(self,file,encryption):
		self.__end_of_enc = b'<end_of_enc>' ; self.__enc = encryption ; self.__pos = 0
		self.__end_of_bytes = b'<end_of_bytes>' ; self.__counter = b'' ; self.__var = (self.__pos,0)
		if hasattr(file,'read'):
			self.file = file
		else:
			self.file = open(file,'rb').read()

	def get(self,chunk=MB):
		while True:
			data = self.file.read(chunk,position=self.__var)
			if self.__end_of_enc in (data:=self.__counter + data):
				index = data.find(self.__end_of_enc) ; self.__counter = b'' ; self.__pos += index + len(self.__end_of_enc) ; self.__var = (self.__pos,0)
				return pickle.loads(self.__enc.decrypt(decompress(data[:index])))
			elif self.__end_of_bytes == data:
				break
			else:
				self.__counter += data ; self.__var = (len(self.__counter)+self.__pos,0)

	def all(self,chunk=MB):
		while True:
			try:
				buffer = self.get(chunk)
				if buffer:
					yield buffer
				else:
					break
			except :
				pass

class Storage:

	def __init__(self) -> None:
		self.__file = NamedTemporaryFile()
		self.lengh = 0

	def write(self,buffer,whence=2):
		assert type(buffer) in [bytes,bytearray]
		self.seek(0,whence)
		self.lengh += len(buffer)
		self.__file.write(buffer)

	def truncate(self,post):
		self.__file.truncate(post)
		self.lengh = 0

	def flush(self):
		self.__file.flush()

	def close(self):
		self.__file.close()

	def seek(self,x,y=0):
		self.__file.seek(x,y)

	def read(self,size=-1,position=()):
		if position:
			self.seek(*position)
		return self.__file.read(size)
	
	def method(self,metho):
		if hasattr(self.__file,metho) :
			return getattr(self.__file,metho)
		
	def tell(self):
		return self.__file.tell()

class _encryption:

	def __init__(self,key=DEFAULT_ENC):
		self.__Key = Fernet(key)
		self.__code = key

	def encrypt(self,data:bytes):
		try:
			return self.__Key.encrypt(data)
		except:
			raise KeyError(f'bad key {self.__code}')

	def decrypt(self,data:bytes):
		try:
			return self.__Key.decrypt(data)
		except:
			raise KeyError(f'bad key {self.__code}')

class Bridge:

	def __init__(self,serv,enckey=DEFAULT_ENC,timeout=None):
		assert isTCP(serv),'Bridge accepts only TCP server'
		self.__server = serv ; self.__end_of_enc = b'<end_of_enc>'
		self.__end_of_bytes = b'<end_of_bytes>' ; self.__end_of_data = b'<end_of_data>'
		self.__enc = _encryption(key=enckey)
		self.__data = Storage() ; self.__error = 0
		self.TimeOut(timeout)
		
	def __Check(data):
		try:
			pickle.dumps(data)
			return True
		except:
			return False
		
	def link(addr,**keys):
		"""
		Description:
			The Link() method is a class method used to establish a connection to a server. It creates a new instance of the Bridge class representing the client side of the connection.
		Parameters:
			addr: A tuple containing the IP address and port number of the server to connect to.
		Returns:
			An instance of the Bridge class representing the client side of the connection.
		Example Usage:
			server_address = ('127.0.0.1', 8000)
			client_bridge = Bridge.Link(server_address)
		"""
		soc = socket()
		soc.connect(addr)
		return Bridge(soc,**keys)
		
	def SetEncKey(self,Key):
		"""
		Description:
			The SetEncMode() method allows changing the encryption mode used by the Bridge object. It updates the encryption key used for encrypting and decrypting data transmitted over the socket connection.
		Parameters:
			mode: The new encryption mode to be set. This should be a 32-byte URL-safe base64-encoded string, typically generated by the Fernet.generate_key() method.
		"""
		try:
			self.__enc = _encryption(key=Key)
		except ValueError:
			raise KeyError("Fernet key must be 32 url-safe base64-encoded bytes.")

	def SendBuffer(self,buffer,end=True):
		"""
		Description:
			The SendBuffer() method is responsible for sending data from the client to the server over the established socket connection. It ensures that the data is encrypted before transmission for secure communication.
		Parameters:
			buffer: The data to be sent from the client to the server. It can be of any serializable type.
		Returns:
			length: The length of the original data buffer that was successfully sent.
		"""
		try:
			if Bridge.__Check(buffer):
				if end:
					payload = pickle.dumps(buffer) ; Buffer = self.__enc.encrypt(payload)
					com = compress(Buffer) ; self.__server.send((com+self.__end_of_enc+self.__end_of_bytes))
					return len(Buffer) , len(com)
				else:
					payload = pickle.dumps(buffer) ; Buffer = self.__enc.encrypt(payload)
					self.__server.send((com:=compress(Buffer))+self.__end_of_enc)
					return len(Buffer) , len(com)
			else:
				raise ValueError(f"can't not encode {buffer}")
		except TypeError:
			raise ValueError(f"can't not encode {buffer}")
		except ConnectionAbortedError as er:
			raise er
		except ConnectionResetError:
			raise ConnectionResetError('the session has closed!')

	def RecvBuffer(self,buffer=1024,buffer_size=-1,returns=False,chunk=-1):
		"""
		Description:
			The RecvBuffer() method is responsible for receiving data from the server by the client over the established socket connection. It ensures that the received data is decrypted for further processing.
		Parameters:
			buffer: The size of the buffer used for receiving data. Defaults to 1024 bytes.
			buffer_size: The maximum size of the data buffer. Defaults to -1 (no limit).
		Returns:
			pyload: the value that recv from the server
		"""
		try:
			position = 0
			while self.__end_of_bytes not in self.__data.read(chunk,position=(position,0)):
				var = self.__server.recv(buffer) ; count = self.__data.lengh - len(self.__end_of_bytes) ; position = 0 if count < 0 else count
				if var == b'':
					if self.__error == 100:
						raise ConnectionAbortedError
					else:
						self.__error += 1
				self.__data.write(var)
				if self.__data.lengh >= buffer_size and buffer_size != -1:
					self.__error = 0
					raise Error.BufferDataError(f'the data bigger than {buffer_size}')
			if not returns:
				pyload = self.__data.read()
				later = pyload.split(self.__end_of_bytes,1)
				pyl = [pickle.loads(dumpdata) for dumpdata in [self.__enc.decrypt(decompress(enc)) for enc in later[0].split(self.__end_of_enc) if enc]]
				self.__data.truncate(0) ; self.__data.write(later[1])
				return tuple(pyl) if len(pyl) != 1 else pyl[0]
			return Mandger(self.__data,self.__enc)
		except ConnectionResetError:
			raise ConnectionResetError('the session has closed!')
		except ConnectionAbortedError as er:
			raise er
		except TimeoutError:
			raise TimeoutError('timed out')

	def Close(self):
		"""
		Description:
			The Close() method is responsible for closing the session between client and server
		"""
		self.__server.close() ; self.__data.close()

	def TimeOut(self,out):
		"""
		Description:
			The TimeOut() method sets a timeout on the underlying socket connection. This timeout specifies the maximum amount of time (in seconds) that the socket will wait for data to be received before raising a timeout exception.
		Paramerters:
			out: The timeout value in seconds.
		"""
		self.__server.settimeout(out) 
		
class Error:

	class ServerInitializeError(Exception):

		def __init__(self,er):
			self.er = er
			
	class BufferDataError(Exception):
	
		def __init__(self,er):
			self.er = er
			
class Container:

	def __init__(self):
		pass
		
	def __getitem__(self,key):
		if type(key) in [str,int]:
			return __session__[key] if key in __session__.keys() else None
		else:
			raise ValueError('')
		
	def __setitem__(self,key,value):
		global __session__
		__session__[key] = value
		
	def __enter__(self):
		return self
		
	def __exit__(self,x,y,z):
		pass
		
	def get(self,parm):
		"""
    	Description:
        	The get() method retrieves the value associated with the specified key from the session container (__session__). If the key is present in the container, it returns the corresponding value; otherwise, it returns None.
    	Parameters:
        	parm: The key whose associated value is to be retrieved from the session container.
    	Returns:
        	value: The value associated with the specified key if it exists in the session container, otherwise returns None.
    	Example Usage:
        	session_container = Container()
        	session_container['key'] = 'value'
        	retrieved_value = session_container.get('key')
    	"""
		return self.__getitem__(parm)
	
	def all(self):
		"""
    	Description:
        	The all() method returns a list containing all the sessions stored in the session container (__session__).
    	Returns:
        	list: A list containing all the sessions stored in the session container.
    	Example Usage:
        	container = Container()
        	values = container.all()
    """
		return [x for x in __session__.values()]
		
	def count(self):
		"""
    	Description:
        	The count() method returns the number of key-value pairs stored in the session container.
    	Returns:
        	count: An integer representing the number of key-value pairs in the session container.
    	Example Usage:
        	container = Container()
        	count = container.count()
    """
		return len(__session__)
		
	def pop(self,parm):
		"""
    	Description:
        	The pop() method removes and returns the value associated with the specified key from the session dictionary (__session__). If the key is not found, it returns None.
    	Parameters:
        	self: The Container object itself.
        	parm: The key whose associated value is to be removed and returned from the session dictionary.
    	Returns:
        	value: The value associated with the specified key if found; otherwise, returns None.
    	Example Usage:
        	container = Container()
        	value = container.pop('key')
    	"""
		return __session__.pop(parm)
	
	def clear(self):
		"""
    	Description:
        	The clear() method removes all items from the session container (__session__). It effectively resets the session container, removing all stored key-value pairs.
    	Example Usage:
        	container = Container()
        	container.clear()
    	"""
		__session__.clear()
		return None
		
class Server(Container):

	def __init__(self,addr):
		self.addr = addr
		self.ip , self.port = addr[::1]
		self.cl = cl ; self.cl.run = True
		

	def __tunnel__(ser,session,cl):
		global sessions 
		while cl.run:
			try:
				client , addr = ser.accept()
				session[addr[0]] = Bridge(client)
			except OSError:
				break

	def init(self):
		"""
    	Description:
        	The init() method initializes the server by creating a socket object, binding it to the specified address, and configuring it to listen for incoming connections.
    	Example Usage:
        	server = Server(('127.0.0.1', 8080))
        	server.init()
    	"""
		self.bridge = socket()
		self.bridge.bind(self.addr)
		self.bridge.listen()

	def listen(self):
		"""
    	Description:
        	The listen() method starts listening for incoming connections on the initialized server socket. It creates a new thread to handle incoming connections concurrently and returns a Container object to manage client sessions.
    	Returns:
        	Container: An instance of the Container class used to manage client sessions.
    	Raises:
        	ServerInitializeError: If the server socket has not been initialized using the init() method.
    	Example Usage:
        	server = Server(('127.0.0.1', 8080))
        	server.init()
        	container = server.listen()
    	"""
		global __session__
		if hasattr(self,'bridge'):
			Thread(target=Server.__tunnel__,args=(self.bridge,__session__,self.cl,)).start()
		else:
			raise Error.ServerInitializeError('the initialize function must be called')
			
	def listen_on(self,func):
		"""
		Description:
			The listen_on() method starts listening for incoming connections on the server in a separate thread while executing a custom function to handle each connection.
		Parameters:
			func: A function to be executed for each incoming connection. This function typically handles the communication with the client.
		Returns:
			None
			Example Usage:
			def handle_connection(socket:socket.socket, session:dict):
				# Custom function to handle each connection
				pass

			server = Server(('127.0.0.1', 8080))
			server.init()
			server.listen_on(handle_connection)
		"""
		global __session__
		if hasattr(self,'bridge'):
			Thread(target=func,args=(self.bridge,__session__,self.cl,)).start()
		else:
			Error.ServerInitializeError('the initialize function must be called')
			
	def release(self):
		"""
		Description:
			The stop() method closes the server socket, effectively stopping the server from accepting any new connections and terminating any existing connections.
		Example Usage:
			server = Server(('127.0.0.1', 8080))
			server.init()
			# Server is running
			server.stop()
		"""
		
		self.cl.run = False
		sleep(0.5)
		self.bridge.close()