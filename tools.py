from cryptography.fernet import Fernet
from psutil import net_if_addrs
from os.path import join , dirname
from requests import get
from requests.exceptions import ConnectionError
from socket import AF_INET , SOCK_STREAM

class InvalidIP(Exception):

	def __init__(self, *args: object) -> None:
		super().__init__(*args)

def GenerateKey():
	'''
	Description:
		GenerateKey: generate a random key using crpytography
	Returns:
		None
	'''
	return Fernet.generate_key()
	
def PublicIP():
	'''
	Description:
		PublicIp : return the public ip of the network
	Returns:
		return the public ip of your wifi
	'''	
	try:
		return get("https://api.ipify.org/?format=text").text
	except ConnectionError:
		raise ValueError('You are not online -__-')
	
	
def LocalIP():
	'''
	Description:
		PublicIp : return the local ip of the network
	Returns:
		return the local ip of your wifi
	'''	
	for x,y in net_if_addrs().items():
		for z in y:
			if z.address.startswith('192.168'):
				return z.address
	return ''

def DetailsIp(ip=''):
	cont = get(f"http://ip-api.com/json/{ip}").json()
	if cont['status'] == 'success':
		return cont
	else:
		raise InvalidIP(f"can't find {ip}")
	
def isTCP(ser):
	if ser.family is AF_INET and ser.type is SOCK_STREAM:
		return True
	else:
		return False
