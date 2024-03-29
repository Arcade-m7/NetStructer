import os , sys
	
__file = __file__ if __file__ not in sys.path else ''
	
sys.path.append(os.path.dirname(__file))
import pickle as json
import socket
from threading import Thread
from cryptography.fernet import Fernet
from time import sleep
from utlist import *
from const import *

__session__ = {}

class _encryption:

	def __init__(self,key=DEFAULT_ENC):
		self.__Key = Fernet(key)

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

	def __init__(self,serv,code=DEFAULT_ENC):
		assert isTCP(serv),'Bridge accepts only TCP server'
		self.__server = serv
		self.__end_of_bytes = b'<end_of_bytes>'
		self.__enc = _encryption(key=code)
		self.__data = b''
		
	def __Check(data):
		try:
			json.dumps(data)
			return True
		except:
			return False
		
	def Link(addr):
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
		soc = socket.socket()
		soc.connect(addr)
		return Bridge(soc)
		
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

	def SendBuffer(self,buffer):
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
				Buffer = self.__enc.encrypt(json.dumps(buffer))
				self.__server.send(Buffer+self.__end_of_bytes)
				return len(buffer)
			else:
				raise ValueError(f"can't not encode {buffer}")
		except TypeError:
			raise ValueError(f"can't not encode {buffer}")
		except ConnectionAbortedError as er:
			raise er
		except ConnectionResetError:
			raise ConnectionResetError('the session has closed!')

	def RecvBuffer(self,buffer=1024,buffer_size=-1):
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
			while self.__end_of_bytes not in self.__data:
				var = self.__server.recv(buffer)
				if var == b'':
					raise ConnectionAbortedError
				self.__data += var
				if len(self.__data) >= buffer_size and buffer_size != -1:
					raise Error.BufferDataError(f'the data bigger than {buffer_size}')
			later = self.__data[self.__data.find(self.__end_of_bytes)+len(self.__end_of_bytes):]
			pyl = json.loads(self.__enc.decrypt(self.__data[:self.__data.find(self.__end_of_bytes)]))
			self.__data = later
			return pyl
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
		self.__server.close()

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
		global run ; run = True

	def __tunnel__(ser,session):
		global sessions , run
		while run:
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
		self.bridge = socket.socket()
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
			Thread(target=Server.__tunnel__,args=(self.bridge,__session__)).start()
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
			Thread(target=func,args=(self.bridge,__session__,)).start()
		else:
			Error.ServerInitializeError('the initialize function must be called')
			
	def stop(self):
		"""
		Description:
			The stop() method closes the server socket, effectively stopping the server from accepting any new connections and terminating any existing connections.
		Example Usage:
			server = Server(('127.0.0.1', 8080))
			server.init()
			# Server is running
			server.stop()
		"""
		global run
		run = False
		sleep(0.5)
		self.bridge.close()
				
