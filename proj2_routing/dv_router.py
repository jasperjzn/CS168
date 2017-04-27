"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics


INFINITY = 16


class DVRouter (basics.DVRouterBase):

    def __init__ (self):
        """
        Called when the instance is initialized.
        You probably want to do some additional initialization here.
        """
        self.start_timer() # Starts calling handle_timer() at correct rate
        self.PortToLatency = {}  #port -> latency
        self.RoutingTable = {}     #destination -> [latency, port, time]
        self.PortToDestination = {}  #port -> [destination]

    def handle_link_up (self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.
        The port attached to the link and the link latency are passed in.
        """
        self.PortToLatency[port] = latency

        for x in self.RoutingTable:
            self.send(basics.RoutePacket(x, self.RoutingTable[x][0]), port)



    def handle_link_down (self, port):
        """
        Called by the framework when a link attached to this Entity does down.
        The port number used by the link is passed in.
        """
        del self.PortToLatency[port]
        for temp in self.PortToDestination[port]:
            if self.POISON_MODE:
                self.RoutingTable[temp][0] = INFINITY
            else:
                self.PortToDestination[port].remove(temp)
                del self.RoutingTable[temp]

    def handle_rx (self, packet, port):
        """
        Called by the framework when this Entity receives a packet.
        packet is a Packet (or subclass).
        port is the port number it arrived on.
        You definitely want to fill this in.
        """
        if isinstance(packet, basics.RoutePacket):
            boolean1 = self.PortToLatency[port] + packet.latency < INFINITY
            boolean2 = self.POISON_MODE
            if boolean1:
                if boolean2:
                    self.send(basics.RoutePacket(packet.destination, INFINITY), port)
                if (packet.destination not in self.RoutingTable):
                    self.RoutingTable[packet.destination] = [self.PortToLatency[port] + packet.latency, port, api.current_time()]
                    if port not in self.PortToDestination:
                        self.PortToDestination[port] = [packet.destination]
                    else:
                        self.PortToDestination[port].append(packet.destination)
                    self.advertise(packet.destination, self.PortToLatency[port] + packet.latency, port)
                elif (self.RoutingTable[packet.destination][0] > packet.latency + self.PortToLatency[port]):
                    self.RoutingTable[packet.destination] = [self.PortToLatency[port] + packet.latency, port, api.current_time()]
                    if port not in self.PortToDestination:
                        self.PortToDestination[port] = [packet.destination]
                    else:
                        self.PortToDestination[port].append(packet.destination)
                    self.advertise(packet.destination, self.PortToLatency[port] + packet.latency, port)
                else:
                    if self.RoutingTable[packet.destination][1] == port:
                        self.RoutingTable[packet.destination][2] = api.current_time()
                        if packet.latency + self.PortToLatency[port] > self.RoutingTable[packet.destination][0]:
                            self.RoutingTable[packet.destination][0] = packet.latency + self.PortToLatency[port]
                            self.advertise(packet.destination,  self.PortToLatency[port] + packet.latency, port)
            else:
                if self.POISON_MODE:
                    for x in self.RoutingTable.keys():
                        if port in self.PortToDestination:
                            for temp in self.PortToDestination[port]:
                                if temp == packet.destination:
                                    self.advertise(packet.destination, INFINITY, port)
                                    self.PortToDestination[self.RoutingTable[x][1]].remove(x)
                                    del self.RoutingTable[x]

        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.RoutingTable[packet.src] = [self.PortToLatency[port], port, None]
            if port not in self.PortToDestination:
                self.PortToDestination[port] = [packet.src]
            else:
                self.PortToDestination[port].append(packet.src)
            self.advertise(packet.src, self.PortToLatency[port], port)
        else:
          if packet.dst in self.RoutingTable:
            if self.RoutingTable[packet.dst][0] < INFINITY: 
                if self.RoutingTable[packet.dst][1] != port:
                    self.send(packet, self.RoutingTable[packet.dst][1])

    def handle_timer (self):
        """
        Called periodically.
        When called, your router should send tables to neighbors.  It also might
        not be a bad place to check for whether any entries have expired.
        """
        destinations = self.RoutingTable.keys()
        for dt in destinations:
            if self.POISON_MODE:
                self.send(basics.RoutePacket(dt, INFINITY), self.RoutingTable[dt][1])
            if self.RoutingTable[dt][2] == None:
                self.advertise(dt, self.RoutingTable[dt][0], self.RoutingTable[dt][1])
            elif self.timeout(self.RoutingTable[dt][2]):
                self.PortToDestination[self.RoutingTable[dt][1]].remove(dt)
                del self.RoutingTable[dt]
            else:
                self.advertise(dt, self.RoutingTable[dt][0], self.RoutingTable[dt][1])
    def timeout (self, time):
        if (api.current_time() - time) >= self.ROUTE_TIMEOUT:
            return True
        else:
            return False

    def advertise (self, destination, latency, port):
        self.send(basics.RoutePacket(destination, latency), port, flood=True)








