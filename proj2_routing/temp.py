"""
Your awesome Distance Vector router for CS 168
"""

import sim.api as api
import sim.basics as basics


# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter (basics.DVRouterBase):
  #NO_LOG = True # Set to True on an instance to disable its logging
  #POISON_MODE = True # Can override POISON_MODE here
  #DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

  def __init__ (self):
    """
    Called when the instance is initialized.
    You probably want to do some additional initialization here.
    """
    self.start_timer() # Starts calling handle_timer() at correct rate
    self.DV = {}
    self.links = {}
    self.poisoned = {}

  def handle_link_up (self, port, latency):
    """
    Called by the framework when a link attached to this Entity goes up.
    The port attached to the link and the link latency are passed in.
    """
    self.links[port] = latency
    for x in self.DV.keys():
      helpNeighbor = basics.RoutePacket(x, self.DV[x][0])
      self.send(helpNeighbor, port, flood=False)
      #print "NEIGHBORTIME %s" % port, self



  def handle_link_down (self, port):
    """
    Called by the framework when a link attached to this Entity does down.
    The port number used by the link is passed in.
    """
    del self.links[port]
    if not self.POISON_MODE:
      for x in self.DV.keys():
        if self.DV[x][2] == port:
          del self.DV[x]
    else:
      for x in self.DV.keys():
        if self.DV[x][2] == port:
          self.poisoned[x] = self.DV[x]
          routePoison = basics.RoutePacket(x, INFINITY)
          self.send(routePoison, port=None, flood=True)
          del self.DV[x]
          #maybe dont send to next hop? idk

  def handle_rx (self, packet, port):
    """
    Called by the framework when this Entity receives a packet.
    packet is a Packet (or subclass).
    port is the port number it arrived on.
    You definitely want to fill this in.
    """
    #self.log("RX %s on %s (self: %s) (src: %s)", packet, port, self, packet.src)
    if isinstance(packet, basics.RoutePacket):
      if(packet.latency + self.links[port] < INFINITY):
        if ((self.DV.get(packet.destination) == None) or (self.DV[packet.destination][0] > packet.latency + self.links[port])):
          newPacket = basics.RoutePacket(packet.destination, self.links[port] + packet.latency)
          self.DV[packet.destination] = [newPacket.latency, api.current_time(), port]
          self.send(newPacket, port, flood=True)
          if self.POISON_MODE:
            poison = basics.RoutePacket(packet.destination, INFINITY)
            self.send(poison, port, flood=False)
        else:
          if self.DV[packet.destination][2] == port:
            self.DV[packet.destination][1] = api.current_time()
            if packet.latency + self.links[port] > self.DV[packet.destination][0]:
              self.DV[packet.destination][0] = packet.latency + self.links[port]
              newPacket = basics.RoutePacket(packet.destination, self.links[port] + packet.latency)
              self.send(newPacket, port, flood=True)
              if self.POISON_MODE:
                poison = basics.RoutePacket(packet.destination, INFINITY)
                self.send(poison, port, flood=False)
        if self.poisoned.get(packet.destination) != None and self.POISON_MODE:
          del self.poisoned[packet.destination]
      elif packet.latency >= INFINITY and self.POISON_MODE:
        for x in self.DV.keys():
          if (x == packet.destination) and (self.DV[x][2] == port):
            poison = basics.RoutePacket(packet.destination, INFINITY)
            self.send(poison, port, flood=True)
            self.poisoned[x] = self.DV[x]
            del self.DV[x]

    elif isinstance(packet, basics.HostDiscoveryPacket):
        self.DV[packet.src] = [self.links[port], -1, port]
        route = basics.RoutePacket(packet.src, self.links[port])
        self.send(route, port, flood=True)
    else:
      # Totally wrong behavior for the sake of demonstration only: send
      # the packet back to where it came from!
      if (self.DV.get(packet.dst) != None and self.DV[packet.dst][2] != port):
        if self.DV[packet.dst][0] <= INFINITY: 
          self.send(packet, self.DV[packet.dst][2], flood=False)
        #for x in self.DV.keys():
          #print x, self.DV[x][2], self.DV[x][0], self
        #print self.DV[packet.dst][2], packet.dst, packet.src, self

  def handle_timer (self):
    """
    Called periodically.
    When called, your router should send tables to neighbors.  It also might
    not be a bad place to check for whether any entries have expired.
    """
    for x in self.DV.keys():
      #print x, self.DV[x][2], self.DV[x][0], self
      if (api.current_time() - self.DV[x][1] ) <= 15 or self.DV[x][1] == -1:
        route = basics.RoutePacket(x, self.DV[x][0])
        self.send(route, self.DV[x][2], flood=True)
        if self.POISON_MODE:
          routePoison = basics.RoutePacket(x, INFINITY)
          self.send(routePoison, self.DV[x][2], flood=False)
      else:
        if self.POISON_MODE:
          routePoison = basics.RoutePacket(x, INFINITY)
          self.send(routePoison, self.DV[x][2], flood=False)
          self.poisoned[x] = self.DV[x]
        del self.DV[x]
    if self.POISON_MODE:
      for x in self.poisoned.keys():
        poison = basics.RoutePacket(x, INFINITY)
        self.send(poison, port=None, flood=True)