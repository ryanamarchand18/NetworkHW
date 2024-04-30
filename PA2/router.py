import time
import sys
import _thread
import queue
from link import Link


class Router():
    """Router superclass that handles the details of
       packet send/receive and link changes.
       Subclass this class and override the "handle..." methods
       to implement the routing algorithms"""


    def __init__(self, addr, heartbeatTime):
        """Initialize Router address and threadsafe queue for link changes"""
        self.addr = addr       # address of router
        self.links = {}        # links indexed by port, i.e., {port:link, ......, port:link}
        self.linkChanges = queue.Queue()
        self.heartbeatTime = heartbeatTime
        self.lastTime = 0
        self.keepRunning = True
        self.f = open("Router-"+self.addr+".dump", "w")
        self.recvdPkts = []


    def changeLink(self, change):
        """Add, remove, or change the cost of a link.
           The change argument is a tuple with first element
           'add', or 'remove' """
        self.linkChanges.put(change)


    def addLink(self, port, endpointAddr, link, cost):
        """Add new link to router"""
        self.links = {p:link for p,link in self.links.items() if p != port}
        self.links[port] = link
        self.handleNewLink(port, endpointAddr, cost)


    def removeLink(self, port):
        """Remove link from router"""
        endpointAddr = None
        for p,link in self.links.items():
            if p == port:
                endpointAddr = link.get_e2(self.addr)
                while not link.q12.empty():
                    link.q12.get_nowait()
                while not link.q21.empty():
                    link.q21.get_nowait()
                break
        self.links = {p:link for p,link in self.links.items() if p != port}
        self.handleRemoveLink(port, endpointAddr)


    def runRouter(self):
        """Main loop of router"""
        while self.keepRunning:
            time.sleep(0.1)
            currTimeInMillisecs = int(round(time.time() * 1000))
            try:
                change = self.linkChanges.get_nowait()
                if change[0] == "add":
                    self.addLink(*change[1:])
                elif change[0] == "remove":
                    self.removeLink(*change[1:])
            except queue.Empty:
                pass
            for port in self.links.keys():
                packet = self.links[port].recv(self.addr)
                if packet:
                    self.logRecvdPacket(port, packet)
                    self.handlePacket(port, packet)
            if (currTimeInMillisecs - self.lastTime >= self.heartbeatTime):
                self.lastTime = currTimeInMillisecs
                self.handlePeriodicOps()


    def send(self, port, packet):
        """Send a packet out given port"""
        try:
            self.links[port].send(packet, self.addr)
        except KeyError:
            pass


    def logRecvdPacket(self, port, packet):
        """log recvd packets"""
        s = packet.srcAddr+"-"+packet.dstAddr+"-"+packet.content
        if packet.isControl():
            self.f.write("Recvd CONTROL packet ("+packet.srcAddr+"->"+packet.dstAddr+" content="+packet.content+") on port "+str(port))
        elif packet.isData():
            self.f.write("Recvd DATA packet ("+packet.srcAddr+"->"+packet.dstAddr+" content="+packet.content+") on port "+str(port))
        else:
            self.f.write("Recvd UNKNOWN TYPE packet ("+packet.srcAddr+"->"+packet.dstAddr+" content="+packet.content+") on port "+str(port))
        if packet.isData():
            if s in self.recvdPkts:
                self.f.write(" -- DUP PKT!!")
            else:
                self.recvdPkts.append(s)
        self.f.write("\n")


    def handlePacket(self, port, packet):
        """process incoming packet"""
        # default implementation sends packet back out the port it arrived
        # you should replace it with your implementation
        self.send(port, packet)


    def handleNewLink(self, port, endpoint, cost):
        """a new link has been added to switch port and initialized, or an existing
        link cost has been updated. Implement any routing/forwarding action that
        you might want to take under such a scenario"""
        pass


    def handleRemoveLink(self, port, endpoint):
        """an existing link has been removed from the switch port. Implement any 
        routing/forwarding action that you might want to take under such a scenario"""
        pass


    def handlePeriodicOps(self):
        """handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file"""
        pass

