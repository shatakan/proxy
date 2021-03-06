import socket
import threading
import sys
# Uses sys module for closing prompt upon exception, and for naming/checking args


# Main server function - accept args passed from main(), create TCP socket and handle errors (i.e. choose a port above 1024) 
def server_routine(local_host,local_port,remote_host,remote_port,receive_first):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    try:
        server.bind((local_host,local_port))
    except:
        print "Error: Chosen port %s:%d is busy, or you lack administrative privileges." % (local_host, local_port)
        sys.exit(0)
    print "*** Listening on %s:%d" % (local_host,local_port)
    
    server.listen(5)
    while True:
        
        client_socket, addr = server.accept()
        print ">>> Receive incoming connection from %s:%d" % (addr[0],addr[1])
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        
        proxy_thread.start()
        
# Dump in hex format: Display one byte unless unicode (which of course requires two)
def hex_output(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
        result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)


def receive_from(connection):
    buffer = ""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer


def request_handler(buffer):
    # Add features to this function (someday)
    return buffer

def response_handler(buffer):
    # And here, too
    return buffer

def proxy_handler(local_host,local_port,remote_host,remote_port,receive_first):
    remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hex_output(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print "<<< Sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)
    
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print ">>> Received %d bytes from localhost." % len(local_buffer)
            hex_output(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print ">>> Sent to remote host."
            
            remote_buffer = receive_from(remote_socket)
            
            if len(remote_buffer):
                print "<<< Received %d bytes from remote host." % len(remote_socket)
                hex_output(remote_buffer)
                remote_buffer = response_handler(remote_buffer)
                client_socket.send(remote_buffer)
                print "<<< Sent to localhost."
            if not len(local_buffer) or not len(remote_buffer):
                client_socket.close()
                remote_socket.close()
                print "*** No more data - closing connections."
                break
            
def main():
    if len(sys.argv[1:]) != 5:
        print "Usage: ./Proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]"
        print "Example: ./Proxy.py 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)
    
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    
    receive_first = sys.argv[5]
    
    if receive_first:
        receive_first = True
    if receive_first == False:
        receive_first = False
    
    server_routine(local_host,local_port,remote_host,remote_port,receive_first)
main()
