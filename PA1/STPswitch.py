# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import sys
import time
from switch import Switch
from link import Link
from client import Client
from packet import Packet


class STPswitch(Switch):
    """MAC learning and forwarding implementation."""

    MAXINFINITY = 40

    def __init__(self, addr, heartbeatTime):
        Switch.__init__(self, addr, heartbeatTime)  # initialize superclass - don't remove
        """TODO: add your own class fields and initialization code here"""
        self.addr = addr
        self.view = (self.addr, 0, self.addr, self.addr)
        self.links = {}
        self.macs = {}
        self.hopcost = 0
        self.nexthop = 0


    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        # default implementation sends packet back out the port it arrived
        #self.send(port, packet)
        if (packet.isControl() == True) : 
            pktview = packet.content.split()
            pktview = map(int, pktview)
            pktview = list(pktview)
            pktsrc = int(packet.srcAddr)
            intview = list(map(int, self.view))
            intaddr = int(self.addr)
            intcost = int(self.links[port].get_cost())
            #print("\n"+str(pktview[0])+" "+str(pktview[1])+" "+str(pktview[2])+" "+str(pktview[3]))
            if (pktsrc == intview[3]) :
                if (pktview[0] < intaddr) :
                    self.view = (str(pktview[0]), str(intcost + pktview[1]), self.addr, packet.srcAddr)
                    #self.hopcost = intcost
                    self.nexthop = port
                else :
                    self.view = (self.addr, "0", self.addr, self.addr)
                    #self.hopcost = 0
                    self.nexthop = 0
                self.maxInfinity()
                self.updateNeighbors()
            else :
                if (pktview[0] < intview[0]) :
                    self.view = (str(pktview[0]), str(intcost + pktview[1]), self.addr, packet.srcAddr)
                    #self.hopcost = intcost
                    self.nexthop = port
                    self.links[port].status = Link.ACTIVE
                    self.maxInfinity()
                    self.updateNeighbors()
                elif ((pktview[0] == intview[0]) & (intview[1] > (pktview[1] + intcost))) :
                    self.view = (str(pktview[0]), str(intcost + pktview[1]), self.addr, packet.srcAddr)
                    #self.hopcost = intcost
                    self.nexthop = port
                    self.links[port].status = Link.ACTIVE
                    self.maxInfinity()
                    self.updateNeighbors()
                elif ((pktview[0] == intview[0]) & (intview[1] == (pktview[1] + intcost))) :
                    if (pktsrc < intview[3]) :
                        self.view = (str(pktview[0]), str(intcost + pktview[1]), self.addr, packet.srcAddr)
                        #self.hopcost = intcost
                        self.nexthop = port
                        self.links[port].status = Link.ACTIVE
                        self.maxInfinity()
                        self.updateNeighbors()
            if ((intview[3] != pktsrc) & (pktview[3] != intaddr)) :
                self.links[port].status = Link.INACTIVE
                deadlinks = []
                for addrs in self.macs :
                    if (self.macs[addrs] == port) :
                        deadlinks.append(addrs)
                for deads in deadlinks :
                    self.macs.pop(deads)
            else :
                self.links[port].status = Link.ACTIVE
        else :
            self.macs.update({packet.srcAddr : port})
            if (packet.dstAddr == "X") :
                #send to all ports except one associated w source address
                for ports in self.links :
                    if self.links[ports].status == Link.ACTIVE :
                        if ports != port :
                            self.send(ports, packet)
            else :
                if (packet.dstAddr in self.macs) :
                    if (self.macs[packet.dstAddr] != port) :
                        self.send(self.macs[packet.dstAddr], packet)
                        #send to destination port
                    #check if associated port is same as source port
                    #if not send to port
                else :
                    for ports in self.links :
                        if self.links[ports].status == Link.ACTIVE :
                            if ports != port :
                                self.send(ports, packet)
                    #broadcast to all but source port if link is active
        


    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        #self.handlePeriodicOps(0)
        self.maxInfinity()
        self.updateNeighbors()
        #maybe update neighbors here
        pass


    def handleRemoveLink(self, port, endpoint):
        """TODO: handle removed link"""
        #self.handlePeriodicOps(0)
        if (port == self.nexthop) :
            self.view = self.view = (self.addr, "0", self.addr, self.addr)
        self.maxInfinity()
        self.updateNeighbors()
        pass


    def handlePeriodicOps(self, currTimeInMillisecs):
        """TODO: handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file."""
        #print("switch info\n")
        #print(self.addr)
        #print(self.hopcost)
        #print(self.nexthop)
        #for ports in self.links :
            #print("connections:")
            #print(self.links[ports].e1)
            #print(self.links[ports].e2)
            #print("link costs:")
            #print(self.links[ports].get_cost())
            #print("status:")
            #print(self.links[ports].status)
        #print(self.links[self.nexthop])
        #print(self.links[self.nexthop].get_cost())
        if (1) :
            for ports in self.links :
                if (self.nexthop == ports) :
                    if (self.hopcost != self.links[ports].get_cost()) :
                        #print("cost change\n")
                        #self.view = list(self.view)
                        #self.view[1] = str((int(self.links[ports].get_cost()) - self.hopcost) + int(self.view[1]))
                        #self.view = tuple(self.view)
                        self.hopcost = int(self.links[ports].get_cost())
                        for ports2 in self.links :
                            self.links[ports2].status = Link.ACTIVE
        self.updateNeighbors()
        pass

    def updateNeighbors(self) :
        content = ""+str(self.view[0])+" "+str(self.view[1])+" "+str(self.view[2])+" "+str(self.view[3])
        packet = Packet(Packet.CONTROL, str(self.addr), "0", content)
        for ports in self.links :
            self.send(ports, packet)
        pass

    def maxInfinity(self) :
        #print("\nmax inf check\n")
        if (int(self.view[1]) >= self.MAXINFINITY) :
            self.view = (self.addr, "0", self.addr, self.addr)
            #print("\nHIT MAX INFINITY VALUE\n")
        pass