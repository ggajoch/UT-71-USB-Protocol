import usb, time, threading, socket
from Queue import Queue

dev = usb.core.find(idVendor=0x4b4)

ep = dev[0][(0,0)][0]

QQQ = Queue()

#clear buffer 
MAX_LEN = 100000
while True:
    x = ep.read(ep.wMaxPacketSize*MAX_LEN)
    if( 100*len(x) < ep.wMaxPacketSize*MAX_LEN ):
        break;

class ReadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        app = []
        while True:
            
        
            #time.sleep(0.01)
            x = ep.read(10*ep.wMaxPacketSize).tolist()

            x = filter(lambda a: a != 0 and a < 240, x)
            x = [ i & 0xF for i in x ];
            #print "|",app,"|"
            #print "{",x,"}"

            app.extend(x)
            

            occ = [i for i in range(0, len(app)) if app[i] == 13];
            if( len(occ) > 0 and occ[0] != len(app)-1 ):
                print app
                t = app[max(0,(occ[0]-9)):min(len(app),(occ[0]+2))]
                print t

                from packet import Packet
                x = Packet(t)
                
                QQQ.put(x.decodePacket())

                app = app[(occ[0]+2):]


thr = ReadThread()
thr.start()

class ClientThread(threading.Thread):

    def __init__(self,ip,port):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        print "[+] New thread started for "+ip+":"+str(port)


    def run(self):    
        print "Connection from : "+ip+":"+str(port)

        while True:
            if QQQ.qsize() > 0:
                t = QQQ.get()
                clientsock.send(str(t)+"\r\n")

host = "127.0.0.1"
port = 5505

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host,port))
threads = []


while True:
    tcpsock.listen(4)
    print "\nListening for incoming connections..."
    (clientsock, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port)
    newthread.start()
    threads.append(newthread)