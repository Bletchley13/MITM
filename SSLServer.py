import socket, ssl
bindsocket = socket.socket()
bindsocket.bind(('', 8000))
bindsocket.listen(5)
newsocket, fromaddr = bindsocket.accept()
c = ssl.wrap_socket(newsocket, server_side=True, certfile="ca.crt",
		                    keyfile="ca.key", ssl_version=ssl.PROTOCOL_SSLv3)

print c.read()
c.write('200 OK\r\n\r\n')
c.close()
bindsocket.close()


