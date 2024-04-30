# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads


class DVrouter(Router):
    """Distance vector routing and forwarding implementation"""

    def __init__(self, addr, heartbeatTime, infinity):
        Router.__init__(self, addr, heartbeatTime)  # initialize superclass - don't remove
        self.infinity = infinity
        """add your own class fields and initialization code here"""
        self.graph = {}
        self.graph[self.addr] = [self.addr, 0]
        #for link in self.links :
            #self.graph[self.links[link].get_e2(self.addr)] = [self.links[link].get_e2(self.addr), self.links[link].get_cost]
        #print("\n"+self.addr+"\n")
        #print(self.graph)
        #print(self.links)
    def handlePacket(self, port, packet):
        """process incoming packet"""
        # default implementation sends packet back out the port it arrived
        # you should replace it with your implementation
        #self.send(port, packet)
        if (packet.isControl() == True) :
            #print("\n"+self.addr+" CONTROL PACKET\n")
            data = loads(packet.content)
            oldgraph = self.graph
            for rout in data :
                if data[rout][0] != self.addr :
                    if rout in self.graph.keys() :
                        if self.links[port].get_e2(self.addr) == self.graph[rout][0] :
                            #print("CASE 1")
                            self.graph[rout] = [self.links[port].get_e2(self.addr), data[rout][1] + self.links[port].get_cost()]
                            #self.checkInf()
                            #self.updateNeighbors()
                        else :
                            if self.graph[rout][1] >= (data[rout][1] + self.links[port].get_cost()) :
                                #print("CASE 2")
                                self.graph[rout] = [self.links[port].get_e2(self.addr), data[rout][1] + self.links[port].get_cost()]
                                #self.checkInf()
                                #self.updateNeighbors()
                    else :
                        #print("ADD NEW ROUTE")
                        self.graph[rout] = [self.links[port].get_e2(self.addr), data[rout][1] + self.links[port].get_cost()]
                        #self.checkInf()
                        #self.updateNeighbors()
            #if self.graph != oldgraph :
            self.checkInf()
            if oldgraph != self.graph :
                for ports in self.links :
                    if ports != port :
                        self.send(ports, packet)
        else :
            if packet.content != "1000000" :
                self.updateNeighbors()
            #if packet.content == "1000000" :
                #print(self.addr)
                #print(self.graph)
            if packet.dstAddr in self.graph :
                #print("hello")
                p = -1
                for ports in self.links :
                    if self.links[ports].get_e2(self.addr) == self.graph[packet.dstAddr][0] :
                        p = ports
                #print("\nSending from "+self.addr+" to "+str(self.graph[packet.dstAddr][0])+" on port "+str(p)+"\n")
                if p != port :
                    self.send(p, packet)



    def handleNewLink(self, port, endpoint, cost):
        """a new link has been added to switch port and initialized, or an existing
        link cost has been updated. Implement any routing/forwarding action that
        you might want to take under such a scenario"""
        self.graph[endpoint] = [endpoint, self.links[port].get_cost()]
        #print("\n"+self.addr+"\n")
        #print(self.graph)
        self.checkInf()
        self.updateNeighbors()
        pass


    def handleRemoveLink(self, port, endpoint):
        """an existing link has been removed from the switch port. Implement any 
        routing/forwarding action that you might want to take under such a scenario"""
        toremove = []
        for rout in self.graph :
            if self.graph[rout][0] == endpoint :
                #toremove.append(rout)
                self.graph[rout] = [endpoint, self.infinity]
                #print("hi")
        #for rem in toremove :
            #self.graph.pop(rem)
        self.updateNeighbors()
        pass


    def handlePeriodicOps(self):
        """handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file"""
        self.checkInf()
        self.updateNeighbors()
        pass

    def checkInf(self):
        for rout in self.graph :
            if self.graph[rout][1] >= self.infinity :
                #self.graph.pop(rout)
                self.graph[rout] = [None, self.infinity - 1]
        #self.updateNeighbors()
        pass

    def updateNeighbors(self):
        #print("\n"+self.addr+"\n")
        #print(self.graph)
        content = dumps(self.graph)
        packet = Packet(Packet.CONTROL, str(self.addr), "0", content)
        for ports in self.links :
            self.send(ports, packet)

        pass