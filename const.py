from cryptography.fernet import Fernet
from utlist import *
import requests , psutil as proc
import socket

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
		return requests.get("https://api.ipify.org/?format=text").text
	except requests.exceptions.ConnectionError:
		raise ValueError('You are not online -__-')
	
	
def LocalIP():
	'''
	Description:
		PublicIp : return the local ip of the network
	Returns:
		return the local ip of your wifi
	'''	
	for x,y in proc.net_if_addrs().items():
		for z in y:
			if z.address.startswith('192.168'):
				return z.address
	return ''
	
def isTCP(ser):
	if ser.family is socket.AF_INET and ser.type is socket.SOCK_STREAM:
		return True
	else:
		return False