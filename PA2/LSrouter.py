# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads
from heapq import heappush, heappop, heapify
import queue

class PQEntry:

    def __init__(self, addr, cost, next_hop):
        self.addr = addr
        self.cost = cost
        self.next_hop = next_hop

    def __lt__(self, other):
         return (self.cost < other.cost)

    def __eq__(self, other):
         return (self.cost == other.cost)


class LSrouter(Router):
    """Link state routing and forwarding implementation"""

    def __init__(self, addr, heartbeatTime):
        Router.__init__(self, addr, heartbeatTime)  # initialize superclass - don't remove
        self.graph = {} # A dictionary with KEY = router
                        # VALUE = a list of lists of all its neighbor routers/clients and the cost to each neighbor
                        # {router: [[neighbor_router_or_client, cost]]}
        self.graph[self.addr] = []
        """add your own class fields and initialization code here"""
        self.paths = self.dijkstra()
        self.seq = 1
        self.seqvec = {}
        self.seqvec[self.addr] = self.seq


    def handlePacket(self, port, packet):
        """process incoming packet"""
        # default implementation sends packet back out the port it arrived
        # you should replace it with your implementation
        #self.send(port, packet)
        
        if (packet.isControl() == True) :
            #print("\n\n\n")
            #print(self.addr)
            #print(self.graph)
            #print("\n\n")
            data = loads(packet.content)
            inseq = int(packet.dstAddr)
            if packet.srcAddr in self.seqvec.keys() :
                if inseq <= self.seqvec[packet.srcAddr] :
                    
                    #print("bonjour")
                    
                    return    
            self.seqvec[packet.srcAddr] = inseq
            #print(self.seqvec)
            #print(self.addr)
            #print(data)
            if self.addr in data.keys() :
                data.pop(self.addr)
                data[self.addr] = []
                for j in self.links :
                    data[self.addr].append([self.links[j].get_e2(self.addr), self.links[j].get_cost()])
            self.graph[packet.srcAddr] = data[packet.srcAddr]
            #for rout in data :
                #self.graph[rout] = data[rout]
            self.paths = self.dijkstra()
            #print("\n\n"+self.addr)
            #print(self.graph)
            for ports in self.links :
                #if ports != port :
                    
                self.send(ports, packet)
                    
            #print(self.graph)
        else :
            #print(self.paths)
            #print("bonjour")
            #self.paths = self.dijkstra()
            #print("\n\n"+self.addr)
            #for i in self.paths :
                #print(i.addr)
                #print(i.next_hop)
            hop = -1
            p = -1
            for i in self.paths :
                if i.addr == packet.dstAddr :
                    hop = i.next_hop
                    #print("\nhippity hoppity")
                    #print(i.next_hop)
                    #print(self.links)
            if hop != -1 :
                for ports in self.links :
                    if self.links[ports].get_e2(self.addr) == hop :
                        p = ports
                        #print("yee")
            if p != -1 :
                #print("\nSending from "+self.addr+" to "+str(hop)+" on port "+str(p)+"\n")
                self.send(p, packet)



    def handleNewLink(self, port, endpoint, cost):
        """a new link has been added to switch port and initialized, or an existing
        link cost has been updated. Implement any routing/forwarding action that
        you might want to take under such a scenario"""
        for neighbor in self.graph[self.addr]:
            if neighbor[0] == endpoint:
                self.graph[self.addr].remove(neighbor)
        self.graph[self.addr].append([endpoint,cost])
        #print(self.graph)
        self.dijkstra()
        self.updateNeighbors()


    def handleRemoveLink(self, port, endpoint):
        """an existing link has been removed from the switch port. Implement any 
        routing/forwarding action that you might want to take under such a scenario"""
        for neighbor in self.graph[self.addr]:
            if neighbor[0] == endpoint:
                self.graph[self.addr].remove(neighbor)
        self.dijkstra()
        self.updateNeighbors()

    def handlePeriodicOps(self):
        """handle periodic operations. This method is called every heartbeatTime.
        You can change the value of heartbeatTime in the json file"""
        self.updateNeighbors()
        pass


    def dijkstra(self):
        """An implementation of Dijkstra's shortest path algorithm.
        Operates on self.graph datastructure and returns the cost and next hop to
        each destination router in the graph as a List (finishedQ) of type PQEntry"""
        priorityQ = []
        finishedQ = [PQEntry(self.addr, 0, self.addr)]
        for neighbor in self.graph[self.addr]:
            heappush(priorityQ, PQEntry(neighbor[0], neighbor[1], neighbor[0]))

        while len(priorityQ) > 0:
            dst = heappop(priorityQ)
            finishedQ.append(dst)
            if not(dst.addr in self.graph.keys()):
                continue
            for neighbor in self.graph[dst.addr]:
                #neighbor already exists in finnishedQ
                found = False
                for e in finishedQ:
                    if e.addr == neighbor[0]:
                        found = True
                        break
                if found:
                    continue
                newCost = dst.cost + neighbor[1]
                #neighbor already exists in priorityQ
                found = False
                for e in priorityQ:
                    if e.addr == neighbor[0]:
                        found = True
                        if newCost < e.cost:
                            del e
                            heapify(priorityQ)
                            heappush(priorityQ, PQEntry(neighbor[0], newCost, dst.next_hop))
                        break
                if not found:
                    heappush(priorityQ, PQEntry(neighbor[0], newCost, dst.next_hop))

        return finishedQ


    def updateNeighbors(self) :
        content = dumps(self.graph)
        #print("\nsending out this graph:\n")
        #print(self.addr)
        #print(self.seq)
        #print(self.graph)
        self.graph.pop(self.addr)
        self.graph[self.addr] = []
        for j in self.links :
            self.graph[self.addr].append([self.links[j].get_e2(self.addr), self.links[j].get_cost()])
        packet = Packet(Packet.CONTROL, str(self.addr), str(self.seq), content)
        for ports in self.links :
            self.send(ports, packet)
        self.seq = self.seq + 1
        #if self.addr == "6" :
            #print(self.graph)
        pass
