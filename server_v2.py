from socket import *
import ssl
import threading
import time
import re 
import httplib
import struct
import string
import os

class handler(threading.Thread):
	def __init__(self,socket) :
		threading.Thread.__init__(self)
		self.socket=socket
	
	def CreateSocketAndConnectToOriginDst(self , cliSock):
		SO_ORIGINAL_DST = 80
		dst = cliSock.getsockopt(SOL_IP, SO_ORIGINAL_DST, 255)
		family, port = struct.unpack('!HH', dst[:4])
		ipaddr = inet_ntoa(dst[4:8])
		fakeSock = socket(AF_INET,SOCK_STREAM)
		if port==443 :
			c = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED,
					ssl_version=ssl.PROTOCOL_SSLv3, ca_certs='ca.crt')
			fakeSock = c
		fakeSock.connect((ipaddr,port))
		print ipaddr,port
		return fakeSock
	
	def ReadLine(self,SourceSock):
		line = ""
		while True:
			char = SourceSock.recv(1)
			line += char
			if not line.find("\r\n") == -1 :
				return line

	def ReadNum(self,SourceSock,length):
		line = ""
		while len(line) < length:
			char = SourceSock.recv(1)
			line += char
		return line

	def ReadHttp(self,SourceSock):
		header = ""
		line = SourceSock.recv(1)
		data = line
		while len(line) :
			line = SourceSock.recv(1)
			data += line
			if not data.find("\r\n\r\n")==-1 :
				header = data
				data = ""
				break;
		dicHeader = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", header))
		#print dicHeader
		for (k,v) in dicHeader.items():
			print k,":",v
		body = ""
		if 'Transfer-Encoding' in dicHeader and dicHeader['Transfer-Encoding'] == 'chunked' :
			while True :
				line = self.ReadLine(SourceSock)
				body += line
				chunkSize = int(line,16)
				if chunkSize == 0 : 
					break
				line = self.ReadNum(SourceSock,chunkSize+2)
				body += line
		else :
			if 'Content-Length' in dicHeader :
				length = int(dicHeader['Content-Length'])
			else :
				length = 0

			while length>0 :
				line = SourceSock.recv(1)
				length -= len(line)
				body += line

		self.PrinfContent(body)
		return header,body

	def PrinfContent(self,content):
		index = 0
		part = 0x10
		print '[PrintContent]'
		
		while index < len(content) :
			length = part if len(content)-index >= part else len(content)-index
			print "%08d" % index ,
			for i in range(index,index+length):
				print content[i:i+2].encode('hex').upper(),
				i += 1
			print_str=""
			for i in range(index,index+length):
				if content[i] not in string.printable or content[i] in {'\n','\r','\t'}:
					print_str+='.'
				else:
					print_str+=content[i]
			print print_str

			index+=length

	def SendTo(self,FowardSock,header , body):
		#print "[SendTo] %s" % header
		#print "[SendTo] %s" % body
		FowardSock.send(header)
		FowardSock.send(body)
		#FowardSock.send(data)
		print "[SendTo] finish"
		return 0

	def ReadAndForward(self,SourceSock,FowardSock):
		header,body = self.ReadHttp(SourceSock)
		#need to append CHUNKED MODE
		#body = self.ReadFrom(SourceSock,header)
		self.SendTo(FowardSock,header , body)
		return 0

	def run(self):
		clientSocket = self.socket
		header = ""
		fakeSock = self.CreateSocketAndConnectToOriginDst(clientSocket)
		print "==================== client request  ================================"
		self.ReadAndForward(clientSocket,fakeSock)
		print "==================== server response  ================================"
		self.ReadAndForward(fakeSock,clientSocket)
		clientSocket.close()
		fakeSock.close()
		print "connect finish"


bindAddress = ("192.168.56.1",81)

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(bindAddress)
serverSocket.listen(1)
threads = []
data_dir = "/home/bletchley/workspace/wms-pr2/"

while True :
	clientSocket,addr = serverSocket.accept()
	SO_ORIGINAL_DST = 80
	dst = clientSocket.getsockopt(SOL_IP, SO_ORIGINAL_DST, 255)
	family, port = struct.unpack('!HH', dst[:4])
	if port == 443 :
		tmpSocket = ssl.wrap_socket(clientSocket, server_side=True, 
				certfile=os.path.join(data_dir, "ca.crt"),
				keyfile=os.path.join(data_dir, "ca.key"),
				ssl_version=ssl.PROTOCOL_SSLv3#,
				#cert_reqs=ssl.CERT_NONE#,
				#do_handshake_on_connect=False
				)
		print tmpSocket.read()
		tmpSocket.write('200 OK\r\n\r\n')
		tmpSocket.close

		#clientSocket = tmpSocket
		print "server cer"
		
	handler(clientSocket).start()


